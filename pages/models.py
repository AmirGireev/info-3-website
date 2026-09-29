from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Options used both in the admin dropdowns and in the outfit search form,
# so the values always match.
SEX_OPTIONS = ["Female", "Male", "Unisex"]
WEATHER_OPTIONS = ["Rainy", "Sunny", "Cold", "Windy"]
STYLE_OPTIONS = ["Streetwear", "Casual", "Formal", "Vintage", "Sporty"]
COLOR_OPTIONS = ["Black", "White", "Blue", "Red", "Green", "Beige"]


def as_choices(values):
    return [(value, value) for value in values]


class UserProfile(models.Model):
    """Public profile of a user (bio, picture, style)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True)
    style = models.CharField(max_length=30, blank=True, choices=as_choices(STYLE_OPTIONS))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.username


class Outfit(models.Model):
    """An outfit posted by a user. Other users can save it to their wardrobe."""

    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="outfits")
    image = models.ImageField(upload_to="outfits/")
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    # Fields used by the search filters
    style_genre = models.CharField(max_length=60, blank=True, choices=as_choices(STYLE_OPTIONS))
    weather_suitability = models.CharField(max_length=60, blank=True, choices=as_choices(WEATHER_OPTIONS))
    sex = models.CharField(max_length=10, blank=True, choices=as_choices(SEX_OPTIONS))
    color = models.CharField(max_length=30, blank=True, choices=as_choices(COLOR_OPTIONS))

    # Profiles that saved this outfit -> profile.wardrobe.all()
    saved_by = models.ManyToManyField(UserProfile, blank=True, related_name="wardrobe")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title or f"{self.owner.user.username}'s outfit"


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Every new user automatically gets an (empty) profile."""
    if created:
        UserProfile.objects.create(user=instance)