from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Model
from django.db.models.signals import pre_save
from django.dispatch import receiver


class ExampleModel(Model): ...


@receiver(pre_save, sender=ExampleModel)
def my_sender_signal(sender, instance, **kwargs):
    layer = get_channel_layer()

    # Example of sending a message to a channel
    async_to_sync(layer.send)("my-channel-name", {"text": "Hello World!"})

    # Example of sending a message to a group channel
    async_to_sync(layer.group_send)("my-group-name", {"text": "Hello World!"})
