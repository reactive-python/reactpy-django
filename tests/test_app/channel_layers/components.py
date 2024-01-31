from reactpy import component, hooks, html
from reactpy_django.hooks import use_channel_layer


@component
def receiver():
    state, set_state = hooks.use_state("None")

    async def receiver(message):
        set_state(message["text"])

    use_channel_layer(channel_name="test_channel", receiver=receiver)

    return html.div(f"Message Receiver: {state}")


@component
def sender():
    sender = use_channel_layer(channel_name="test_channel")

    async def submit_event(event):
        if event["key"] == "Enter":
            await sender({"text": event["target"]["value"]})

    return html.div(
        "Message Sender: ",
        html.input(
            {"type": "text", "onKeyDown": submit_event},
        ),
    )
