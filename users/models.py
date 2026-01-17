from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model to distinguish Chef/Admin from Customers.
    """
    is_chef = models.BooleanField(default=False, help_text="Designates if this user has Chef privileges.")

    def __str__(self):
        return self.username