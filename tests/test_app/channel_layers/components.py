from reactpy import component, hooks, html

from reactpy_django.hooks import use_channel_layer


@component
def receiver():
    state, set_state = hooks.use_state("None")

    async def receiver(message):
        set_state(message["text"])

    use_channel_layer(channel="channel-messenger", receiver=receiver)

    return html.div(
        {"id": "receiver", "data-message": state},
        f"Message Receiver: {state}",
    )


@component
def sender():
    sender = use_channel_layer(channel="channel-messenger")

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
def group_receiver(id_number: int):
    state, set_state = hooks.use_state("None")

    async def receiver(message):
        set_state(message["text"])

    use_channel_layer(receiver=receiver, group="group-messenger")

    return html.div(
        {"id": f"group-receiver-{id_number}", "data-message": state},
        f"Group Message Receiver #{id_number}: {state}",
    )


@component
def group_sender():
    sender = use_channel_layer(group="group-messenger")

    async def submit_event(event):
        if event["key"] == "Enter":
            await sender({"text": event["target"]["value"]})

    return html.div(
        "Group Message Sender: ",
        html.input(
            {"type": "text", "id": "group-sender", "onKeyDown": submit_event},
        ),
    )
