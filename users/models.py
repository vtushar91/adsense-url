from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
class User(AbstractUser):
    name = models.CharField(max_length=100)
    phone_or_upi = models.CharField(max_length=50, unique=True)
    earnings = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal("0.0"))

    pending_withdraw = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal("0.0"))

    total_withdrawn = models.DecimalField(max_digits=10, decimal_places=6, default=Decimal("0.0"))

    referral_code = models.CharField(
    max_length=20,
    unique=True,
    editable=False
    )

    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals"
    )
    referral_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal("0.0")
    )
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)

    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    zip_code = models.CharField(max_length=20, blank=True)

    phone_number = models.CharField(max_length=20, blank=True)

    # Optional social/contact
    whatsapp = models.CharField(max_length=20, blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    skype = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)