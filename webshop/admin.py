from django.contrib import admin
from . import models

class GenreAdmin(admin.ModelAdmin):
    list_display = 'slug', 'name', 'description',
    filter_horizontal = 'games',

class GameAdmin(admin.ModelAdmin):
    list_display = 'slug', 'name', 'developer', 'published',
    list_filter = 'published', 'genres',
    search_fields = 'slug', 'name', 'developer__name', 'developer__slug',
    filter_horizontal = 'genres',

class DeveloperAdmin(admin.ModelAdmin):
    list_display = 'slug', 'name', 'description', 'registered', 'user',
    search_fields = 'slug', 'name',

class SaleAdmin(admin.ModelAdmin):
    list_display = 'developer', 'game', 'price', 'buyer', 'date',
    list_filter = 'date',
    search_fields = 'developer__name', 'developer__slug', 'game__name', 'game__slug', 'buyer__username',

class HiscoreAdmin(admin.ModelAdmin):
    list_display = 'game', 'user', 'score', 'date',
    list_filter = 'date',
    search_fields = 'game__name', 'game__slug', 'user__username',

class SavegameAdmin(admin.ModelAdmin):
    list_display = 'game', 'user', 'date',
    list_filter = 'date',
    search_fields = 'game__name', 'game__slug', 'user__username',

class PaymentAdmin(admin.ModelAdmin):
    list_display = 'pid', 'user', 'game', 'price', 'date',
    list_filter = 'date',
    search_fields = 'pid', 'user__username',

admin.site.register(models.Genre, GenreAdmin)
admin.site.register(models.Game, GameAdmin)
admin.site.register(models.Developer, DeveloperAdmin)
admin.site.register(models.Sale, SaleAdmin)
admin.site.register(models.Hiscore, HiscoreAdmin)
admin.site.register(models.Savegame, SavegameAdmin)
admin.site.register(models.Payment, PaymentAdmin)
