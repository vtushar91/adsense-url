from django.db.models.signals import post_migrate
from django.dispatch import receiver
from decimal import Decimal
from .models import MonetizationRule


@receiver(post_migrate)
def create_default_monetization_rule(sender, **kwargs):
    # 🔒 prevent duplicate creation
    if not MonetizationRule.objects.filter(is_default=True).exists():
        MonetizationRule.objects.create(
            name="Default",
            ad_pages=4,
            cpm=Decimal("50.00"),
            is_active=True,
            is_default=True
        )