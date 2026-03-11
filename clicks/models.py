from django.db import models
from links.models import ShortLink


class ClickEvent(models.Model):
    short_link = models.ForeignKey(
        ShortLink,
        on_delete=models.CASCADE,
        related_name="clicks"
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_unique = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.short_link.short_code} - {self.ip_address}"