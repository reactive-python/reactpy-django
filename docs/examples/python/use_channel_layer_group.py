from reactpy import component, hooks, html

from reactpy_django.hooks import use_channel_layer


@component
def my_sender_component():
    sender = use_channel_layer(group="my-group-name")

    async def submit_event(event):
        if event["key"] == "Enter":
            await sender({"text": event["target"]["value"]})

    return html.div(
        "Message Sender: ",
        html.input({"type": "text", "onKeyDown": submit_event}),
    )


@component
def my_receiver_component_1():
    message, set_message = hooks.use_state("")

    async def receive_message(message):
        set_message(message["text"])

    use_channel_layer(group="my-group-name", receiver=receive_message)

    return html.div(f"Message Receiver 1: {message}")


@component
def my_receiver_component_2():
    message, set_message = hooks.use_state("")

    async def receive_message(message):
        set_message(message["text"])

    use_channel_layer(group="my-group-name", receiver=receive_message)

    return html.div(f"Message Receiver 2: {message}")
