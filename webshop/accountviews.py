from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.contrib import auth, messages
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from html5tagger import Document, E
from .forms import UserForm, RegisterForm, DeveloperForm
from . import layout, models

def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        if username and password:
            user = auth.authenticate(request, username=username, password=password)
            if user is None:
                messages.error(request, "Invalid credentials")
            else:
                auth.login(request, user)
                messages.success(request, "Logged in")
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        messages.success(request, "Logged out")
        auth.logout(request)
        return HttpResponseRedirect(reverse("webshop:index"))
    raise Http404("Invalid method")

def register(request):
    if request.method == "POST":
        f = RegisterForm(request.POST)
        if f.is_valid():
            user = f.save()
            auth.login(request, user)
            messages.add_message(request, messages.INFO, "Welcome!")
            return HttpResponseRedirect(reverse("webshop:user_prefs"))
        messages.error(request, "Please correct the marked values!")
    else:
        f = RegisterForm()
    doc = layout.form_post(request, f, submit="Register")
    return layout.page(request, "Register", doc)

def user_prefs(request):
    u = request.user
    if not u.is_authenticated:
        messages.error(request, "Login first to access that page.")
        return HttpResponseRedirect(reverse("webshop:index"))
    developer = u.developer if hasattr(u, "developer") else None
    doc = E()
    uform = UserForm(instance=u)
    pwform = PasswordChangeForm(user=u)
    dform = DeveloperForm(instance=developer)
    if request.method == "POST":
        p = request.POST
        try:
            if "_user" in p:
                uform = UserForm(p, instance=u)
                if not uform.is_valid(): raise ValueError("User form invalid")
                uform.save()
                messages.success(request, "Settings saved!")
            if "_password" in p:
                pwform = PasswordChangeForm(p, user=u)
                if not pwform.is_valid(): raise ValueError("Password form invalid")
                auth.update_session_auth_hash(request, pwform.save())
                messages.success(request, "Password changed!")
            if "_developer" in p:
                if not developer: developer = models.Developer(user=u)
                dform = DeveloperForm(p, instance=developer)
                print("Update: ", dform, dform.is_valid())
                if not dform.is_valid(): raise ValueError("Developer form invalid")
                dform.save()
                messages.error(request, "Developer settings saved")
            return HttpResponseRedirect(reverse("webshop:user_prefs"))
        except ValueError:
            messages.error(request, "Please correct the marked values on form!")
        # Error occurred; reload true values from DB to dismiss partial form changes
        request.user = models.User.objects.get(pk=u.pk)
    with doc.section:
        doc.h2("Basic settings")
        doc(layout.form_post(request, uform, name="_user"))
    with doc.section:
        doc.h2("Change password")
        doc(layout.form_post(request, pwform, name="_password"))
    with doc.section:
        doc.h2("Change developer info" if developer else "Register as developer")
        doc(layout.form_post(request, dform, name="_developer"))
    return layout.page(request, "Account settings", doc)

