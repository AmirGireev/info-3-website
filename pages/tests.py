from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Outfit


class SearchTests(TestCase):
    def setUp(self):
        user = User.objects.create_user("alex", password="pw")
        self.profile = user.profile  # created automatically by the signal
        Outfit.objects.create(
            owner=self.profile, image="outfits/a.jpg", title="Street look",
            style_genre="Streetwear", color="Black", sex="Male",
        )
        Outfit.objects.create(
            owner=self.profile, image="outfits/b.jpg", title="Office look",
            style_genre="Formal", color="White", sex="Female",
        )

    def test_text_search(self):
        response = self.client.get(reverse("pages:results"), {"q": "street"})
        self.assertContains(response, "Street look")
        self.assertNotContains(response, "Office look")

    def test_filter_search(self):
        response = self.client.get(reverse("pages:results"), {"style": "Formal", "color": "White"})
        self.assertContains(response, "Office look")
        self.assertNotContains(response, "Street look")

    def test_no_match_shows_empty_message(self):
        response = self.client.get(reverse("pages:results"), {"q": "doesnotexist"})
        self.assertContains(response, "No outfits found")

    def test_profile_search(self):
        response = self.client.get(reverse("pages:profile_search"), {"query": "ale"})
        self.assertContains(response, "alex")
        response = self.client.get(reverse("pages:profile_search"), {"query": "zzz"})
        self.assertContains(response, "No results found")


class WardrobeTests(TestCase):
    def setUp(self):
        self.mia = User.objects.create_user("mia", password="pw")
        alex = User.objects.create_user("alex", password="pw")
        self.outfit = Outfit.objects.create(owner=alex.profile, image="outfits/a.jpg", title="Street look")

    def test_add_and_remove(self):
        self.client.login(username="mia", password="pw")
        self.client.post(reverse("pages:add_to_wardrobe", args=[self.outfit.pk]))
        self.assertIn(self.outfit, self.mia.profile.wardrobe.all())
        self.client.post(reverse("pages:remove_from_wardrobe", args=[self.outfit.pk]))
        self.assertNotIn(self.outfit, self.mia.profile.wardrobe.all())

    def test_wardrobe_is_per_user(self):
        self.client.login(username="mia", password="pw")
        self.client.post(reverse("pages:add_to_wardrobe", args=[self.outfit.pk]))
        self.client.logout()
        self.client.login(username="alex", password="pw")
        response = self.client.get(reverse("pages:wardrobe"))
        self.assertContains(response, "No saved outfits yet")

    def test_wardrobe_requires_login(self):
        response = self.client.get(reverse("pages:wardrobe"))
        self.assertRedirects(response, f"{reverse('pages:login')}?next={reverse('pages:wardrobe')}")

    def test_add_requires_login(self):
        response = self.client.post(reverse("pages:add_to_wardrobe", args=[self.outfit.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.outfit.saved_by.count(), 0)


class AccountTests(TestCase):
    def setUp(self):
        User.objects.create_user("alex", password="pw")

    def test_signup_creates_user_profile_and_logs_in(self):
        password = "S0me-strong-pass!"
        response = self.client.post(
            reverse("pages:signup"),
            {"username": "newuser", "password1": password, "password2": password},
        )
        self.assertRedirects(response, reverse("pages:landing"))
        self.assertTrue(hasattr(User.objects.get(username="newuser"), "profile"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_and_logout(self):
        response = self.client.post(reverse("pages:login"), {"username": "alex", "password": "pw"})
        self.assertRedirects(response, reverse("pages:landing"))
        self.assertIn("_auth_user_id", self.client.session)
        self.client.post(reverse("pages:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_browsing_is_open_without_login(self):
        for name in ("landing", "search", "results", "profile_search"):
            self.assertEqual(self.client.get(reverse(f"pages:{name}")).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("pages:profile_detail", args=["alex"])).status_code, 200)

    def test_own_profile_and_edit_require_login(self):
        for name in ("profile_view", "edit_profile"):
            response = self.client.get(reverse(f"pages:{name}"))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn(reverse("pages:login"), response["Location"])