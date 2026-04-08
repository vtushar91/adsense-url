import string
import random
from django.db import models
from django.conf import settings
import uuid

class MonetizationRule(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=50)
    # core configs
    ad_pages = models.PositiveIntegerField(default=1)
    cpm = models.DecimalField(max_digits=10, decimal_places=2)
    
    # optional logic controls
    min_user_level = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.cpm} CPM"

class ShortLink(models.Model):
    short_code = models.CharField(max_length=10, unique=True, db_index=True)
    original_url = models.URLField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="links"
    )
    monetization = models.ForeignKey(
        MonetizationRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    unique_clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.short_code
    
    def generate_short_code(self, length=6):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
class Announcement(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    is_active = models.BooleanField(default=True)

    # scheduling (VERY useful 🔥)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    # optional targeting
    min_user_level = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title