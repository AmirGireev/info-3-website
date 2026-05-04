from django.db import models
# Create your models here.

class UserProfile(models.Model):
    """represents user profile displayed on profile and search pages notwendig für profile.html, edit_profile.html, profile_search.html"""

    username = models.CharField(max_length=50, unique=True)

    bio = models.TextField(blank=True)
    profile_picture_url = models.URLField(blank=True)
    banner_url = models.URLField(blank=True)
    #personalization style tag (e.g. streetwear, casual...)
    style = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str: #admin readability
        """Return readable string representation of the user profile for the Django admin."""
        return self.username

class ClothingItem(models.Model):
    """ Represents single clothing item, can be owned by a user, displayed in wardrobe and used inside outfits  -> wardrobe.html, outfit_detail.html"""

    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"

    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='clothingItems')
    name = models.CharField(max_length=100)
    image_url = models.URLField()

    category = models.CharField(max_length=100)
    color = models.CharField(max_length=30, blank=True)

    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return readable string representation of the clothing item."""
        return self.name


class Outfit(models.Model):
    """Represents outfit created by user consisting of multiple or just one clothing items shown in search result, profile pages. notwendig für: results.html, outfit details, recent outfits"""
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='outfits')

    image_url = models.URLField()
    title = models.CharField(max_length=100, blank=True) #name outfit
    description = models.TextField(blank=True)

    #for search filter
    style_genre = models.CharField(max_length=60, blank=True)
    weather_suitability = models.CharField(max_length=60, blank=True)
    sex = models.CharField(max_length=10, blank=True)
    color = models.CharField(max_length=30, blank=True)

    #clothing items that can make the outfit(nochmal anschauen ob wir das wollen!)
    items = models.ManyToManyField(ClothingItem, blank=True, related_name='outfits')


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Return readable string representation of the outfit"""
        return self.title if self.title else f"{self.owner.username}'s Outfit"

#Sammelmodell
class WardrobeCollection(models.Model):
    """Represents a named wardrobe collection owned by a user. Collection can contain complete outfits and individual clothing items """
    class Visibility(models.TextChoices):
            PRIVATE = "private", "Private"
            PUBLIC = "public", "Public"

        # which profile owns collection
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    # private/public
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE)
    # can contain outfit or items
    outfits = models.ManyToManyField(Outfit, blank=True, related_name='saved_in')
    items = models.ManyToManyField(ClothingItem, blank=True, related_name='saved_in')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return readable string representation of the collection"""
        return self.name if self.name else f"{self.owner.username}'s Collection"




