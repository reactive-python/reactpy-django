from django.db import models


class ComponentParams(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, unique=True)  # type: ignore
    data = models.BinaryField(editable=False)  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, editable=False)  # type: ignore
