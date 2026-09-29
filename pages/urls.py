from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    AddToWardrobeView, EditProfileView, LandingView, OutfitDetailView,
    ProfileView, RemoveFromWardrobeView, SearchResultsView, SearchView,
    SignUpView, WardrobeView, profile_search,
)

app_name = "pages"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),

    # Accounts
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),

    # Outfits
    path("search/", SearchView.as_view(), name="search"),
    path("results/", SearchResultsView.as_view(), name="results"),
    path("outfit/<int:pk>/", OutfitDetailView.as_view(), name="outfit_detail"),

    # Profiles
    path("profile/", ProfileView.as_view(), name="profile_view"),
    path("profile/<str:username>/", ProfileView.as_view(), name="profile_detail"),
    path("edit_profile/", EditProfileView.as_view(), name="edit_profile"),
    path("profile_search/", profile_search, name="profile_search"),

    # Wardrobe
    path("wardrobe/", WardrobeView.as_view(), name="wardrobe"),
    path("wardrobe/add/<int:pk>/", AddToWardrobeView.as_view(), name="add_to_wardrobe"),
    path("wardrobe/remove/<int:pk>/", RemoveFromWardrobeView.as_view(), name="remove_from_wardrobe"),
]