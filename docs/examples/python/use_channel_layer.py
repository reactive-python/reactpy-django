from reactpy import component, hooks, html

from reactpy_django.hooks import use_channel_layer


@component
def my_component():
    async def receive_message(message):
        set_message_data(message["text"])

    async def send_message(event):
        if event["key"] == "Enter":
            await sender({"text": event["target"]["value"]})

    message_data, set_message_data = hooks.use_state("")
    sender = use_channel_layer(group="my-group-name", receiver=receive_message)

    return html.div(
        f"Received: {message_data}",
        html.br(),
        "Send: ",
        html.input({"type": "text", "onKeyDown": send_message}),
    )
