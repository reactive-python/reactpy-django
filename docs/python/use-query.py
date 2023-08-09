from example.models import TodoItem
from reactpy import component, html
from reactpy_django.hooks import use_query


def get_items():
    return TodoItem.objects.all()


@component
def todo_list():
    item_query = use_query(get_items)

    if item_query.loading:
        rendered_items = html.h2("Loading...")
    elif item_query.error or not item_query.data:
        rendered_items = html.h2("Error when loading!")
    else:
        rendered_items = html.ul([html.li(item, key=item) for item in item_query.data])

    return html.div("Rendered items: ", rendered_items)
