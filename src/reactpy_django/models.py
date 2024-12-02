from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from reactpy_django.utils import get_pk


class ComponentSession(models.Model):
    """A model for storing component sessions."""

    uuid = models.UUIDField(primary_key=True, editable=False, unique=True)
    params = models.BinaryField(editable=False)
    last_accessed = models.DateTimeField(auto_now=True)


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


@receiver(pre_delete, sender=get_user_model(), dispatch_uid="reactpy_delete_user_data")
def delete_user_data(sender, instance, **kwargs):
    """Delete ReactPy's `UserDataModel` when a Django `User` is deleted."""
    pk = get_pk(instance)

    UserDataModel.objects.filter(user_pk=pk).delete()
