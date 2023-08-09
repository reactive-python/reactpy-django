from example.models import TodoItem
from reactpy import component, html
from reactpy_django.hooks import use_mutation


def add_item(text: str):
    TodoItem(text=text).save()


@component
def todo_list():
    item_mutation = use_mutation(add_item)

    def reset_event(event):
        item_mutation.reset()

    def submit_event(event):
        if event["key"] == "Enter":
            item_mutation.execute(text=event["target"]["value"])

    if item_mutation.loading:
        mutation_status = html.h2("Adding...")
    elif item_mutation.error:
        mutation_status = html.button({"onClick": reset_event}, "Error: Try again!")
    else:
        mutation_status = html.h2("Mutation done.")

    return html.div(
        html.label("Add an item:"),
        html.input({"type": "text", "onKeyDown": submit_event}),
        mutation_status,
    )
