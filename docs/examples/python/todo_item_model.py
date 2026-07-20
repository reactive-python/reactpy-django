from django.db.models import CharField, Model


class TodoItem(Model):
    text: CharField = CharField(max_length=255)
