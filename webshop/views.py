import datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse, FileResponse
from django.db.models import Q
from django.db import transaction
from django.contrib import auth, messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from html5tagger import E
from .forms import GameForm
from . import api, layout, models, payments
from dkproject import settings

def listing(request, devslug=None, genreslug=None, owned=None):
    title = "The Top Ten"
    games = models.Game.objects.all()
    description = None
    if owned is True:
        title = "Your library"
        if not request.user.is_authenticated:
            return layout.page(request, title, E.p("You need to login first."))
        games = request.user.games.all()
    elif devslug:
        developer = get_object_or_404(models.Developer, slug=devslug)
        title, description = developer.name, developer.description
        games = games.filter(developer=developer)
    elif genreslug:
        genre = get_object_or_404(models.Genre, slug=genreslug)
        title, description = genre.name, genre.description
        games = genre.games.all()
    else:
        if "q" in request.GET:
            q = request.GET["q"].strip()
            if not q: return HttpResponseRedirect(reverse("webshop:index"))
            games = games.filter(Q(name__icontains=q) | Q(developer__name__icontains=q))
            title = "Search: " + q
        games = games[:10]
    with E.div as intro:
        if description: intro.p(description)
        if not games: intro.p("No games.")
        if not devslug and not owned and not "q" in request.GET:
            # On "Top Ten" index page offer JSON download
            intro.p.a("Full listing in JSON format", href=reverse("webshop:api_index"))
        # On developer page the developer has links for adding new games and checking sales
        if devslug and developer.has_access(request.user):
            with intro.ul:
                intro.li.a("Add new game", href=reverse("webshop:add_game", kwargs=dict(devslug=devslug)))
                intro.li.a("View sales", href=reverse("webshop:sales", kwargs=dict(devslug=devslug)))
    # A listing of all matching games
    with E.ul(id="games") as doc:
        for g in games:
            with doc.li.a(href=g.get_absolute_url(), title=g.description):
                doc.img(src=g.get_image(), alt="")
                doc(g.name)
    return layout.page(request, title, doc, intro)

def game(request, devslug, gameslug):
    """Game page and edit form dispatch"""
    game = get_object_or_404(models.Game, slug=gameslug, developer__slug=devslug)
    if request.method == "GET": return game_GET(request, game)
    if request.method == "POST":
        if request.content_type == "application/json":
            return api.game_json(request, game) # Handle AJAX from site
        return game_POST(request, game)

    raise Http404("Invalid method")

def game_GET(request, g, form=None):
    owns = g.has_access(request.user)
    with E.div(id="gameinfo") as doc:
        doc.img(src=g.get_image())
        with doc.div:
            with doc.small:
                for i, genre in enumerate(g.genres.all()):
                    if i: doc(", ")
                    doc.a(genre.name, href=genre.get_absolute_url())
                doc.br("Published ", E.strong(g.published), " by ", g.developer.get_link())
            doc.p(g.description)
            # Options/info about purchases and ownership
            if g.price > 0:
                if not request.user.is_authenticated: doc.p.strong("Login or register to play!")
                elif g.developer.has_access(request.user): doc.p.strong("You have developer access.")
                elif owns: doc.p.strong("You own this game!")
                else: doc(layout.form_post(request, name="_purchase", submit=f"Purchase for {g.price} €"))
            else:
                doc.p.strong("Free to Play!")
        if g.developer.has_access(request.user):
            # Developer options
            with doc.details(open=(form != None)):
                doc.summary("Developer")
                kwargs = dict(devslug=g.developer.slug, gameslug=g.slug)
                doc.p.a("View sales", href=reverse("webshop:sales", kwargs=kwargs))
                doc(layout.form_post(request, form or GameForm(instance=g), name="_edit"))
                # TODO: Django forms for deletion?
                delform = E.hr.input(type="checkbox", name="confirm", id="game_delete")
                delform.label(f" Yes, piss off the {g.users.count()} customers who bought {g.name}", for_="game_delete").br
                doc(layout.form_post(request, content=delform, name="_delete", submit="Delete"))
        elif not hasattr(request.user, "developer"):
            # Only non-developer's accesses update popularity
            g.update_popularity()
    if owns:
        doc.iframe(id="game", src=g.url, sandbox="allow-modals allow-scripts", allowfullscreen=True, width=1280, height=720)
    with doc.table(id="hiscore"):
        doc.caption("Hiscores")
        for name, score in g.get_hiscores_list():
            doc.tr.td(name).td(score, class_="numeric")
    return layout.page(request, g.name, doc)

def game_POST(request, game):
    if not request.user.is_authenticated:
        raise Http404("Must be authenticated!")  # We just use 404 for everything
    if "_edit" in request.POST:
        if not game.developer.has_access(request.user):
            raise Http404("User does not have developer access to this game")
        form = GameForm(request.POST, request.FILES, instance=game)
        if not form.is_valid():
            messages.error(request, "Please correct the errors marked on the edit form!")
            game = models.Game.objects.get(pk=game.pk)  # Reload original from database
            return game_GET(request, game, form)  # Send back the form for corrections
        game = form.save()
        messages.success(request, game.name + " modified")
    if "_delete" in request.POST:
        if "confirm" in request.POST:
            game.delete()
            messages.success(request, game.name + " deleted")
            return HttpResponseRedirect(reverse("webshop:index"))
        messages.warning(request, "Deletion not confirmed!")
    if "_purchase" in request.POST:
        return payments.purchase_form(request, game)
    return HttpResponseRedirect(game.get_absolute_url())

@transaction.atomic   # Adding a game and assigning genres must occur together
def add_game(request, devslug):
    """Add new game form/handler."""
    developer = get_object_or_404(models.Developer, slug=devslug)
    if not developer.has_access(request.user):
        raise Http404("Access denied for this user to add games")
    if request.method == "GET":
        return layout.page(request, "Add Game", layout.form_post(request, GameForm()))
    if request.method == "POST":
        form = GameForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "Please correct the errors marked on form!")
            return layout.page(request, "Add Game", layout.form_post(request, form))
        game = form.save(commit=False)
        game.developer = developer
        game.save()
        form.save_m2m()
        return HttpResponseRedirect(game.get_absolute_url())
    raise Http404("Invalid method")

def sales(request, devslug, gameslug=None):
    developer = get_object_or_404(models.Developer, slug=devslug)
    if gameslug:
        game = get_object_or_404(models.Game, developer=developer, slug=gameslug)
        sales = models.Sale.objects.filter(game=game)
        name = game.name
    else:
        sales = models.Sale.objects.filter(developer=developer)
        name = developer.name
    # Recent sales (the last two weeks)
    today = datetime.datetime.now()
    then = today - datetime.timedelta(days=14)
    recent = sales.filter(date__gt=then)
    doc = salesTable(recent) if recent else E.p("No recent sales.")
    doc.div(id="chart");
    # Link for JSON download
    kwargs = dict(devslug=devslug, gameslug=gameslug) if gameslug else dict(devslug=devslug)
    doc.p.a("Download JSON", href=reverse("webshop:api_sales", kwargs=kwargs))
    # Render page
    return layout.page(request, f"{name} Sales", doc,
        urls = layout.page_urls + (layout.static("highcharts/code/highcharts.js"), layout.static("sales.js"),)
    )

def salesTable(recent):
    with E.table(id="sales") as doc:
        total = None
        doc.caption("The Latest Sales")
        doc.tr.th("Customer").th("Game").th("Price").th("Date").th("Ref")
        for i, s in enumerate(recent):
            if i < 20: doc.tr.td(s.buyer or "-").td(s.game or "-").td(s.price).td(f"{s.date:%Y-%m-%dT%H:%M}").td(s.ref)
            elif i == 20: doc.tr.td("(...)", colspan=5)
            if total: total += s.price
            else: total = s.price
            i += 1
        doc.tr.th("Total:", scope="row").th(len(recent)).th(total).th(f"last 2 weeks")
    return doc

def mediafile(request, filepath):
    """Send a media file. For testing (runserver), normally handled by frontend."""
    return FileResponse(open(settings.MEDIA_ROOT + filepath, "rb"))
