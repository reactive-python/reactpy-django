import asyncio

from reactpy import component, hooks, html
from reactpy_django.hooks import use_channel_layer


@component
def receiver():
    state, set_state = hooks.use_state("None")

    async def receiver(message):
        set_state(message["text"])

    use_channel_layer("simple-messenger", receiver=receiver)

    return html.div(
        {"id": "receiver", "data-message": state}, f"Message Receiver: {state}"
    )


@component
def sender():
    sender = use_channel_layer("simple-messenger")

    async def submit_event(event):
        if event["key"] == "Enter":
            await sender({"text": event["target"]["value"]})

    return html.div(
        "Message Sender: ",
        html.input(
            {"type": "text", "id": "sender", "onKeyDown": submit_event},
        ),
    )


@component
def group_receiver():
    state, set_state = hooks.use_state("None")

    async def receiver(message):
        set_state(message["text"])

    use_channel_layer("group-messenger", group_name="1", receiver=receiver)

    return html.div(f"Group Message Receiver: {state}")


@component
def group_receiver_load_late():
    ready, set_ready = hooks.use_state(False)

    @hooks.use_effect
    async def load_late():
        await asyncio.sleep(10)
        set_ready(True)

    if ready:
        return group_receiver()

    return html.div("Group Message Receiver (Late Load): Loading...")


@component
def group_sender():
    sender = use_channel_layer("group-messenger", group_name="1")

    async def submit_event(event):
        if event["key"] == "Enter":
            await sender({"text": event["target"]["value"]})

    return html.div(
        "Group Message Sender: ",
        html.input(
            {"type": "text", "id": "group-sender", "onKeyDown": submit_event},
        ),
    )
