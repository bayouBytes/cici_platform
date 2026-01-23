import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model to distinguish Chef/Admin from Customers.
    """
    is_chef = models.BooleanField(default=False, help_text="Designates if this user has Chef privileges.")
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verification_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self):
        if self.used_at is None:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])

    def __str__(self):
        return f"{self.user.username} ({self.token})"