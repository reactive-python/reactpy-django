from example.models import TodoItem
from idom import component, html

from django_idom.hooks import use_mutation


def add_item(text: str):
    TodoItem(text=text).save()


@component
def todo_list():
    def submit_event(event):
        if event["key"] == "Enter":
            item_mutation.execute(text=event["target"]["value"])

    item_mutation = use_mutation(add_item)
    if item_mutation.loading:
        mutation_status = html.h2("Adding...")
    elif item_mutation.error:
        mutation_status = html.h2("Error when adding!")
    else:
        mutation_status = html.h2("Mutation done.")

    return html.div(
        html.label("Add an item:"),
        html.input({"type": "text", "onKeyDown": submit_event}),
        mutation_status,
    )
