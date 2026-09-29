from django.contrib import admin

from .models import Outfit, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "style", "created_at")
    search_fields = ("user__username",)


@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
    list_display = ("__str__", "owner", "style_genre", "weather_suitability", "sex", "color", "created_at")
    list_filter = ("style_genre", "weather_suitability", "sex", "color")
    search_fields = ("title", "description", "owner__user__username")