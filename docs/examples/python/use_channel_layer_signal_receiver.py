from reactpy import component, hooks, html

from reactpy_django.hooks import use_channel_layer


@component
def my_receiver_component():
    message, set_message = hooks.use_state("")

    async def receive_message(message):
        set_message(message["text"])

    # This is defined to receive any messages from both "my-channel-name" and "my-group-name".
    use_channel_layer(channel="my-channel-name", group="my-group-name", receiver=receive_message)

    return html.div(f"Message Receiver: {message}")
