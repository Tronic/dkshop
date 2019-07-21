from django.http import HttpResponse
from django.contrib import auth, messages
from django.middleware import csrf
from django.urls import reverse
from html5tagger import Document, E
from .models import Genre, static


page_urls = (
#    static("bootstrap/js/bootstrap.bundle.js"),
    static("bootstrap/css/bootstrap.min.css"),
    static("style.css"),
    static("script.js"),
    static("logo-icon.svg"),
    static("logo-icon.png"),
)

def page(request, title, content, intro=None, urls=page_urls):
    doc = Document(title + " - DK", lang="en", _urls=urls)
    # Attempt to use native pixel dimensions on mobile devices
    doc.meta(name="viewport", content="width=device-width, initial-scale=1")
    msgs = messages.get_messages(request)
    # Popup messages
    with doc.aside(id="messages"):
        for m in msgs: doc.div(m, class_=m.tags)
    # Header bar
    with doc.header:
        # Site logo
        with doc.picture:
            doc.source(media="(min-width: 40rem)", srcset=static("logo-full.svg"))
            doc.img(src=static("logo-small.svg"), alt="Dark Karma games webshop")
        # Search bar
        with doc.form(action=reverse("webshop:index"), id="search"):
            doc.input(type="search", name="q", placeholder="Games or developers", autofocus=True)
            doc.input(type="submit", value="Search")
        # Login/logout form
        doc.div(form_login(request), id="login")
    # Main page content
    with doc.main:
        with doc.ul(id="breadcrumbs"):
            path = ""
            for p in request.path.split("/")[:-1]:
                path += p + "/"
                if not p: p = "///"
                doc.li.a(p, href=path)
        doc.h1(title)
        if intro: doc(intro)
        doc.div(content, id="content")
    # Genre navigation bar
    with doc.nav(id="sidenav"):
        with doc.ul:
            doc.li.a("Top Games", href=reverse("webshop:index"))
            for g in Genre.objects.all():
                doc.li.a(g.name, href=g.get_absolute_url(), title=g.description)
    # Master navigation (bottom)
    with doc.nav(id="masternav"):
        with doc.ul:
            if request.user.is_authenticated:
                doc.li.a("My Library", href=reverse("webshop:library"))
                if hasattr(request.user, "developer"):
                    developer = request.user.developer
                    doc.li.a(developer.name, href=developer.get_absolute_url())
                doc.li.a("Account settings", href=reverse("webshop:user_prefs"))
                if request.user.is_staff:
                    doc.li.a("Admin site", href=reverse("admin:index"))
            else:
                doc.li.a("Register", href=reverse("webshop:register"))
    return HttpResponse(doc)

def form_post(request, form=None, content=None, submit="Submit", name=None, action=None):
    token = csrf.get_token(request)
    with E.form(action=action, method="POST", enctype="multipart/form-data") as doc:
        doc.input(type="hidden", name="csrfmiddlewaretoken", value=token)
        if form: doc.table(form)
        if content: doc(content)
        doc.input(type="submit", value=submit, name=name)
    return doc

def form_login(request):
    doc = None
    if request.user.is_authenticated:
        submit = "Logout " + request.user.username
    else:
        doc = E.input(id="username", type="text", name="username", placeholder="Username", required=True, size=8)
        doc.input(id="password", name="password", placeholder="Password", type="password", required=True, size=8)
        submit = "Login"
    return form_post(request, action=reverse("webshop:login"), content=doc, submit=submit)
