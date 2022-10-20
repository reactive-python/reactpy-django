from django.db import models


class TodoItem(models.Model):
    done = models.BooleanField()  # type: ignore
    text = models.CharField(max_length=1000)  # type: ignore
