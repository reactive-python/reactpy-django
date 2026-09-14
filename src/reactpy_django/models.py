from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone

from reactpy_django.utils import get_pk


class ComponentSession(models.Model):
    """A model for storing component sessions.

    This is used to store component arguments provided within Django templates.
    These arguments are retrieved within the layout renderer (WebSocket consumer)."""

    uuid = models.UUIDField(primary_key=True, editable=False, unique=True)
    params = models.BinaryField(editable=False)
    last_accessed = models.DateTimeField(auto_now=True)


class AuthToken(models.Model):
    """A model that contains any relevant data needed to force Django's HTTP session to
    match the websocket session.

    The session key is tied to an arbitrary UUID token for security (obfuscation) purposes.

    Source code must be written to respect the expiration property of this model."""

    value = models.UUIDField(primary_key=True, editable=False, unique=True)
    session_key = models.CharField(max_length=40, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    @property
    def expired(self) -> bool:
        from reactpy_django.config import REACTPY_AUTH_TOKEN_MAX_AGE

        return self.created_at < (timezone.now() - timedelta(seconds=REACTPY_AUTH_TOKEN_MAX_AGE))


class Config(models.Model):
    """A singleton model for storing ReactPy configuration."""

    cleaned_at = models.DateTimeField(auto_now_add=True)

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

    # We can't store User as a ForeignKey/OneToOneField because it may not be in the same database
    # and Django does not allow cross-database relations. Also, since we can't know the type of the UserModel PK,
    # we store it as a string to normalize.
    user_pk = models.CharField(max_length=255, unique=True)
    data = models.BinaryField(null=True, blank=True)


class SessionStateModel(models.Model):
    """A model for storing `session_state` data.

    This is used to persistently store ReactPy state across WebSocket reconnects (and, depending
    on the configured `REACTPY_SESSION_STATE_MODE`, optionally across page reloads as well).

    The `scope_id` uniquely identifies the scope that the state belongs to. By default it is a
    per-component (per-tab) token that is stable across WebSocket reconnects. When
    `REACTPY_SESSION_STATE_MODE` is set to `"user"`, the scope is instead the authenticated user's
    primary key (falling back to a per-tab token for anonymous users)."""

    scope_id = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    data = models.BinaryField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["scope_id", "key"], name="reactpy_session_state_unique"),
        ]
        indexes = [
            models.Index(fields=["scope_id", "updated_at"], name="reactpy_session_state_idx"),
        ]


@receiver(pre_delete, sender=get_user_model(), dispatch_uid="reactpy_delete_user_data")
def delete_user_data(sender, instance, **kwargs):
    """Delete ReactPy's `UserDataModel` when a Django `User` is deleted."""
    pk = get_pk(instance)

    UserDataModel.objects.filter(user_pk=pk).delete()
