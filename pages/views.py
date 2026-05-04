from django.shortcuts import render
from django.urls import reverse
from urllib.parse import quote
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from profiles.models import UserProfile, Outfit

class LandingView(TemplateView):
    template_name = "landing_page.html"

class SearchView(TemplateView):
    template_name = "search.html"

class SearchResultsView(TemplateView):
    template_name = "results.html"

class OutfitDetailView(TemplateView):
    template_name = "outfit_detail.html"

class EditProfileView(TemplateView):

    template_name = "edit_profile.html"


class ProfileView(TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        target_user = User.objects.get(username='liam')


        user_profile = UserProfile.objects.get(user=target_user)


        user_outfits = Outfit.objects.filter(owner=user_profile)

        context['profile'] = user_profile
        context['outfits'] = user_outfits
        return context


class WardrobeView(TemplateView):
    template_name = "wardrobe.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        liam_user = User.objects.get(username='liam')
        liam_profile = UserProfile.objects.get(user=liam_user)

        saved_outfits = liam_profile.wardrobe.all()

        context['saved_outfits'] = saved_outfits
        return context

class AddToWardrobeView(View):
    def get(self, request, pk):

        liam_user = User.objects.get(username='liam')
        liam_profile = UserProfile.objects.get(user=liam_user)

        outfit_to_save = get_object_or_404(Outfit, pk=pk)

        outfit_to_save.saved_by.add(liam_profile)
        next_url = request.GET.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(f"{reverse('pages:wardrobe')}?next={quote(next_url)}")

        return redirect('pages:wardrobe')


class FashionalexView(TemplateView):
    template_name = "fashionalex_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        target_user = User.objects.get(username='fashionalex')
        user_profile = UserProfile.objects.get(user=target_user)

        user_outfits = Outfit.objects.filter(owner=user_profile)

        context['profile'] = user_profile
        context['outfits'] = user_outfits
        return context




def profile_search(request):
    query = request.GET.get('query')
    if query:
        if query.lower() == 'fashionalex':
            return render(request, 'search_results.html', {'query': query})
        else:
            return render(request, 'no_results.html', {'query': query})

    return render(request, 'profile_search.html')


class RemoveFromWardrobeView(View):
    def get(self, request, pk):
        liam_user = User.objects.get(username='liam')
        liam_profile = UserProfile.objects.get(user=liam_user)

        outfit_to_remove = get_object_or_404(Outfit, pk=pk)

        outfit_to_remove.saved_by.remove(liam_profile)

        next_url = request.GET.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(f"{reverse('pages:wardrobe')}?next={quote(next_url)}")

        return redirect('pages:wardrobe')