from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Model
from django.db.models.signals import pre_save
from django.dispatch import receiver


class ExampleModel(Model): ...


@receiver(pre_save, sender=ExampleModel)
def my_sender_signal(sender, instance, **kwargs):
    layer = get_channel_layer()

    # EXAMPLE 1: Sending a message to a group.
    # Note that `group_send` requires using the `group` argument in `use_channel_layer`.
    async_to_sync(layer.group_send)("my-group-name", {"text": "Hello World!"})

    # EXAMPLE 2: Sending a message to a single channel.
    # Note that this is typically only used for channels that use point-to-point communication
    async_to_sync(layer.send)("my-channel-name", {"text": "Hello World!"})
