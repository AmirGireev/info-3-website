from django.urls import path
from .views import (
    LandingView, SearchView, SearchResultsView, OutfitDetailView,
    EditProfileView, ProfileView, WardrobeView, profile_search, FashionalexView, AddToWardrobeView, RemoveFromWardrobeView
)
app_name = 'pages'

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('search/', SearchView.as_view(), name='search'),
    path('results/', SearchResultsView.as_view(), name='results'),
    path('outfit/', OutfitDetailView.as_view(), name='outfit_detail'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('profile_search/', profile_search, name='profile_search'),
    path('profile/fashionalex/', FashionalexView.as_view(), name='fashionalex'),
    path('profile/', ProfileView.as_view(), name='profile_view'),
    path('wardrobe/', WardrobeView.as_view(), name='wardrobe'),
    path('wardrobe/', WardrobeView.as_view(), name='wardrobe'),
    path('wardrobe/add/<int:pk>/', AddToWardrobeView.as_view(), name='add_to_wardrobe'),
    path('wardrobe/remove/<int:pk>/', RemoveFromWardrobeView.as_view(), name='remove_from_wardrobe'),
]