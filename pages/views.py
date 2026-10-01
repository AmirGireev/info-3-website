from urllib.parse import quote

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView, View,DeleteView
from .models import (
    COLOR_OPTIONS, SEX_OPTIONS, STYLE_OPTIONS, WEATHER_OPTIONS,
    Outfit, UserProfile,
)



def get_current_profile(request):
    """Profile of the logged-in user, or None if nobody is logged in."""
    if not request.user.is_authenticated:
        return None
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return profile


def redirect_to_wardrobe(request):
    """Go to the wardrobe and remember where the user came from (for the Back button)."""
    wardrobe_url = reverse("pages:wardrobe")
    next_url = request.POST.get("next", "")
    is_safe = next_url.startswith("/") and not next_url.startswith("//")
    if is_safe and not next_url.startswith(wardrobe_url):
        return redirect(f"{wardrobe_url}?next={quote(next_url)}")
    return redirect(wardrobe_url)


class SavedIdsMixin:
    """Adds `saved_ids` (IDs of outfits in the current wardrobe) so cards can show Add/Remove."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_current_profile(self.request)
        context["saved_ids"] = set(profile.wardrobe.values_list("pk", flat=True)) if profile else set()
        return context


class LandingView(TemplateView):
    template_name = "landing_page.html"


class SearchView(TemplateView):
    """Filter form (gender, weather, style, color)."""
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            sex_options=SEX_OPTIONS,
            weather_options=WEATHER_OPTIONS,
            style_options=STYLE_OPTIONS,
            color_options=COLOR_OPTIONS,
        )
        return context


class SearchResultsView(SavedIdsMixin, TemplateView):
    """Handles both the text search (?q=...) and the filter form."""
    template_name = "results.html"

    FILTER_FIELDS = {
        "weather": "weather_suitability",
        "style": "style_genre",
        "color": "color",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET
        outfits = Outfit.objects.select_related("owner__user")
        active_filters = []

        q = params.get("q", "").strip()
        if q:
            outfits = outfits.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(style_genre__icontains=q)
                | Q(color__icontains=q)
                | Q(weather_suitability__icontains=q)
                | Q(owner__user__username__icontains=q)
            )

        sex = params.get("sex", "").strip()
        if sex:
            
            outfits = outfits.filter(Q(sex__iexact=sex) | Q(sex__iexact="Unisex"))
            active_filters.append(sex)

        for param, field in self.FILTER_FIELDS.items():
            value = params.get(param, "").strip()
            if value:
                outfits = outfits.filter(**{f"{field}__iexact": value})
                active_filters.append(value)

        context.update(outfits=outfits, q=q, active_filters=active_filters)
        return context


class OutfitDetailView(SavedIdsMixin, DetailView):
    model = Outfit
    template_name = "outfit_detail.html"
    context_object_name = "outfit"


def profile_search(request):
    query = request.GET.get("query", "").strip()
    if not query:
        return render(request, "profile_search.html")

    profiles = list(
        UserProfile.objects.select_related("user").filter(user__username__icontains=query)
    )
    if not profiles:
        return render(request, "no_results.html", {"query": query})
    return render(request, "search_results.html", {"query": query, "profiles": profiles})


class ProfileView(SavedIdsMixin, TemplateView):
    """Own profile (/profile/, login needed) or somebody else's (/profile/<username>/, open)."""
    template_name = "profile.html"

    def dispatch(self, request, *args, **kwargs):
        if "username" not in kwargs and not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current = get_current_profile(self.request)
        username = self.kwargs.get("username")

        if username:
            profile = get_object_or_404(
                UserProfile.objects.select_related("user"), user__username__iexact=username
            )
        else:
            profile = current

        context.update(
            profile=profile,
            outfits=profile.outfits.all(),
            is_own=current is not None and current.pk == profile.pk,
        )
        return context


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("pages:landing")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()  # the profile is created automatically (signal)
        login(self.request, user)
        return redirect("pages:landing")


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ["bio", "style", "profile_picture"]
    template_name = "edit_profile.html"
    success_url = reverse_lazy("pages:profile_view")

    def get_object(self, queryset=None):
        return get_current_profile(self.request)


class WardrobeView(LoginRequiredMixin, SavedIdsMixin, TemplateView):
    template_name = "wardrobe.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_current_profile(self.request)
        context["saved_outfits"] = profile.wardrobe.select_related("owner__user")
        context["profile"] = profile
        return context


class AddToWardrobeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        outfit = get_object_or_404(Outfit, pk=pk)
        outfit.saved_by.add(get_current_profile(request))
        return redirect_to_wardrobe(request)


class RemoveFromWardrobeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        outfit = get_object_or_404(Outfit, pk=pk)
        outfit.saved_by.remove(get_current_profile(request))
        return redirect_to_wardrobe(request)

class AddOutfitView(LoginRequiredMixin, CreateView):
    model = Outfit
    fields = ["title", "description", "image", "sex", "weather_suitability", "style_genre", "color"]
    template_name = "add_outfit.html"

    def form_valid(self, form):
        form.instance.owner = get_current_profile(self.request)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("pages:profile_view")

class DeleteOutfitView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Outfit
    template_name = "delete_outfit.html"
    success_url = reverse_lazy("pages:profile_view")

    def test_func(self):
        outfit = self.get_object()
        profile = get_current_profile(self.request)
        return outfit.owner == profile