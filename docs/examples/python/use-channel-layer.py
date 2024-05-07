from reactpy import component, hooks, html
from reactpy_django.hooks import use_channel_layer


@component
def my_component():
    async def receive_message(message):
        set_message(message["text"])

    async def send_message(event):
        if event["key"] == "Enter":
            await sender({"text": event["target"]["value"]})

    message, set_message = hooks.use_state("")
    sender = use_channel_layer("my-channel-name", receiver=receive_message)

    return html.div(
        f"Received: {message}",
        html.br(),
        "Send: ",
        html.input({"type": "text", "onKeyDown": send_message}),
    )
