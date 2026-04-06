from django.db import models
from links.models import ShortLink
from decimal import Decimal

class ClickEvent(models.Model):
    short_link = models.ForeignKey(
        ShortLink,
        on_delete=models.CASCADE,
        related_name="clicks"
    )

    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField()

    is_unique = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    # Earnings tracking
    earned_amount = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal("0.000000")
    )

    cpm_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["short_link", "created_at"]),
        ]

    def __str__(self):
        return f"{self.short_link.short_code} - {self.ip_address}"