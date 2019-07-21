from django.http.response import JsonResponse, Http404
from django.contrib import auth, messages
from django.views.decorators.gzip import gzip_page
from django.shortcuts import get_object_or_404
import datetime
import json
from . import models

# This is called from views.py
def game_json(request, game):
    """Handle JSON messages from game/site"""
    if not request.user.is_authenticated:
        raise Http404("Must be logged in to use this API")
    data = json.loads(request.body)
    t = data.get("messageType", None)
    res = {}  # Default empty response
    if t == "SCORE":
        hs = models.submit_hiscore(game, request.user, float(data["score"]))
        if hs:
            messages.success(request, f"New hiscore: {hs.score:.0f}")
            res = dict(messageType="REFRESH", element="hiscore")
    elif t == "SAVE":
        state = json.dumps(data["gameState"])
        models.Savegame.objects.filter(game=game, user=request.user).delete()
        models.Savegame(game=game, user=request.user, state=state).save()
    elif t == "LOAD_REQUEST":
        s = models.Savegame.objects.get(game=game, user=request.user)
        res = dict(messageType="LOAD", gameState=json.loads(s.state))
    else:
        print("Unknown message", data)
        raise Http404("Unknown message type")
    return JsonResponse(res)

# TODO: Could use more informative error messages when authentication fails (now 404 or 500 errors)
def json_api(func):
    """A decorator for JSON API functions; handles auth if required and formats the response."""
    # Check if func has an argument named "user", in which case it requires auth
    need_user = "user" in func.__code__.co_varnames[:func.__code__.co_argcount]
    def wrapper(request, **kwargs):
        allow_cors = True
        if need_user:
            if "username" in request.GET:
                # Auth doesn't use cookies, allow cross-origin
                user = auth.authenticate(username=request.GET["username"], password=request.GET["password"])
            else:
                # Fallback to cookie-based session, only same-origin
                allow_cors = False
                user = request.user
            if not user or not user.is_authenticated:
                raise Http404("Must be authenticated / authentication failed")
            res, filename = func(user, **kwargs)
        else:
            # No auth, allow cross-origin
            res, filename = func(**kwargs)
        response = JsonResponse(res)
        response["Content-Disposition"] = f"attachment; filename={filename}"
        if allow_cors: response["Access-Control-Allow-Origin"] = "*"
        return response
    return wrapper

@gzip_page
@json_api
def games_list():
    """List of all genres, developers and games (sorted by popularity) and their hiscores."""
    games = []
    for game in models.Game.objects.all():
        gd = dict(
            name=game.name,
            developer=game.developer.slug,
            genres=[genre.slug for genre in game.genres.all()],
            description=game.description,
            url=game.get_absolute_url(),
            hiscores=game.get_hiscores_list(padding=False),
        )
        if game.image:
            gd["image_url"] = game.image.url
        games.append(gd)
    res = dict(
        genres={
            genre.slug: dict(name=genre.name, url=genre.get_absolute_url())
            for genre in models.Genre.objects.all()
        },
        developers={
            dev.slug: dict(name=dev.name, url=dev.get_absolute_url())
            for dev in models.Developer.objects.all()
        },
        games=games)
    return res, "games.json"

@json_api
def sales(user, devslug, gameslug=None):
    # The JSON API wrapper has already sorted out user for us, so we don't use req
    developer = get_object_or_404(models.Developer, slug=devslug)
    if not developer.has_access(user): raise Http404("Must be authenticated developer")
    if gameslug:
        game = get_object_or_404(models.Game, developer=developer, slug=gameslug)
        sales = models.Sale.objects.filter(game=game)
    else:
        sales = models.Sale.objects.filter(developer=developer)
    details = []
    weekly = {}
    for s in sales.order_by("date"):
        details.append(dict(
            game=s.game.slug if s.game else None,
            buyer=s.buyer.username if s.buyer else None,
            price=str(s.price),
            ref=s.ref,
            date=str(s.date),
        ))
        day = 86400 # seconds
        week = datetime.datetime.fromtimestamp((s.date.timestamp() - 4 * day) // (7 * day) * (7 * day) + 4 * day)
        weekly[week] = weekly.get(week, 0.0) + float(s.price)
    # Format a more useful name than simply "sales.json" (note: slugs contain only safe characters)
    filename = devslug
    if gameslug: filename += "." + gameslug
    filename += ".sales.json"
    return dict(details=details, weekly=list(weekly.items())), filename
