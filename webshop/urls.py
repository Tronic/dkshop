from django.urls import path, register_converter
from dkproject import settings
from . import accountviews, api, payments, slugs, views

register_converter(slugs.USlug, "uslug")  # Upper case slug
register_converter(slugs.LSlug, "lslug")  # Lower case slug

app_name = "webshop"
urlpatterns = [
    path('u/', views.listing, name="library", kwargs=dict(owned=True)),
    path('u/payment/', payments.payment, name="payment"),
    path('u/login/', accountviews.login, name="login"),
    path('u/prefs/', accountviews.user_prefs, name="user_prefs"),
    path('u/register/', accountviews.register, name="register"),
    path('games.json', api.games_list, name="api_index"),
    path('', views.listing, name="index"),
    path('<lslug:genreslug>/', views.listing, name="genre"),
    path('<uslug:devslug>/', views.listing, name="developer"),
    path('<uslug:devslug>/+', views.add_game, name="add_game"),
    path('<uslug:devslug>/s/', views.sales, name="sales"),
    path('<uslug:devslug>/s/sales.json', api.sales, name="api_sales"),
    path('<uslug:devslug>/<uslug:gameslug>/', views.game, name="game"),
    path('<uslug:devslug>/<uslug:gameslug>/s/', views.sales, name="sales"),
    path('<uslug:devslug>/<uslug:gameslug>/s/sales.json', api.sales, name="api_sales"),
]

if settings.DEBUG:
    # Serve media files when in debug mode
    urlpatterns.append(path('m/<path:filepath>', views.mediafile, name="media"))
