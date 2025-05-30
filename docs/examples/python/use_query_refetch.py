from channels.db import database_sync_to_async
from reactpy import component, html

from example.models import TodoItem
from reactpy_django.hooks import use_query


async def get_items():
    return await database_sync_to_async(TodoItem.objects.all)()


@component
def todo_list():
    item_query = use_query(get_items)

    if item_query.loading:
        rendered_items = html.h2("Loading...")
    elif item_query.error or not item_query.data:
        rendered_items = html.h2("Error when loading!")
    else:
        rendered_items = html.ul([html.li(item.text, key=item.pk) for item in item_query.data])

    def on_click(event):
        item_query.refetch()

    return html.div("Rendered items: ", rendered_items, html.button({"onClick": on_click}, "Refresh"))
