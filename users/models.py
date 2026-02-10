from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=100)
    phone_or_upi = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.username
