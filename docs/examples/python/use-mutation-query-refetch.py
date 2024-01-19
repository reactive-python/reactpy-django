from example.models import TodoItem
from reactpy import component, html
from reactpy_django.hooks import use_mutation, use_query


def get_items():
    return TodoItem.objects.all()


def add_item(text: str):
    TodoItem(text=text).save()


@component
def todo_list():
    item_query = use_query(get_items)
    item_mutation = use_mutation(add_item, refetch=get_items)

    def submit_event(event):
        if event["key"] == "Enter":
            item_mutation(text=event["target"]["value"])

    # Handle all possible query states
    if item_query.loading:
        rendered_items = html.h2("Loading...")
    elif item_query.error or not item_query.data:
        rendered_items = html.h2("Error when loading!")
    else:
        rendered_items = html.ul(html.li(item, key=item) for item in item_query.data)

    # Handle all possible mutation states
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
        rendered_items,
    )
