import contextlib

import orjson as pickle
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


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

    # Can't store user model as a ForeignKey/OneToOneField because it may not be in the same database
    # and Django does not allow cross-database relations. Also, the PK is not guaranteed to be an integer,
    # so we can't use a PositiveIntegerField.
    user_pk = models.BinaryField(unique=True)  # type: ignore
    data = models.BinaryField(null=True, blank=True)  # type: ignore


@receiver(pre_delete, sender=get_user_model(), dispatch_uid="reactpy_delete_user_data")
def delete_user_data(sender, instance, **kwargs):
    """Delete `UserDataModel` when the `User` is deleted."""
    pk_field_name = instance._meta.pk.name
    pickled_pk = pickle.dumps(getattr(instance, pk_field_name))

    with contextlib.suppress(Exception):
        UserDataModel.objects.get(user_pk=pickled_pk).delete()

    # Make a list of all user PKs in the database
    all_users = sender.objects.all()
    all_user_pks = [pickle.dumps(getattr(user, pk_field_name)) for user in all_users]

    # Delete any `UserDataModel` objects that are no longer associated with a `User`
    UserDataModel.objects.exclude(user_pk__in=all_user_pks).delete()

