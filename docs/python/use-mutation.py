from example.models import TodoItem
from reactpy import component, html
from reactpy_django.hooks import use_mutation


async def add_item(text: str):
    await TodoItem(text=text).asave()


@component
def todo_list():
    item_mutation = use_mutation(add_item)

    def submit_event(event):
        if event["key"] == "Enter":
            item_mutation(text=event["target"]["value"])

    if item_mutation.loading:
        mutation_status = html.h2("Adding...")
    elif item_mutation.error:
        mutation_status = html.h2("Error when adding!")
    else:
        mutation_status = html.h2("Mutation done.")

    return html.div(
        html.label("Add an item:"),
        html.input({"type": "text", "on_key_down": submit_event}),
        mutation_status,
    )
