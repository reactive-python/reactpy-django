from django.conf import settings
from django.db import models


class ComponentSession(models.Model):
    """A model for storing component sessions.
    All queries must be routed through `reactpy_django.config.REACTPY_DATABASE`.
    """

    uuid = models.UUIDField(primary_key=True, editable=False, unique=True)  # type: ignore
    params = models.BinaryField(editable=False)  # type: ignore
    last_accessed = models.DateTimeField(auto_now=True)  # type: ignore


class Config(models.Model):
    """A singleton model for storing ReactPy configuration."""

    cleaned_at = models.DateTimeField(auto_now_add=True)  # type: ignore

    def save(self, *args, **kwargs):
        """Singleton save method."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class UserDataModel(models.Model):
    """A model for storing `user_state` data."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # type: ignore
    data = models.BinaryField(blank=True)  # type: ignore
