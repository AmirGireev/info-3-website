from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Outfit(models.Model):
        # The owner (e.g., "fashionalex")
        owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

        name = models.CharField(max_length=100)  # e.g., "Streetwear Look"
        description = models.TextField()
        image = models.ImageField(upload_to='outfits/')

        # Who has saved this? (Liam's Virtual Wardrobe)
        saved_by = models.ManyToManyField(UserProfile, related_name='wardrobe', blank=True)

        def __str__(self):
            return f"{self.name} by {self.owner.user.username}"