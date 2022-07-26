???+ tip "Looking for more hooks?"

    Check out the [IDOM Core docs](https://idom-docs.herokuapp.com/docs/reference/hooks-api.html?highlight=hooks) on hooks!

## Use Query and Use Mutation

<!-- TODO: Add description -->

```python
from example_project.my_app.models import TodoItem
from idom import component, html
from django_idom.hooks import use_query, use_mutation


def get_items():
    return TodoItem.objects.all()

def add_item(text: str):
    TodoItem(text=text).save()


@component
def todo_list():
    items_query = use_query(get_items)
    add_item_mutation = use_mutation(add_item, refetch=get_items)
    item_draft, set_item_draft = use_state("")

    if items_query.loading:
        items_view = html.h2("Loading...")
    elif items_query.error:
        items_view = html.h2(f"Error when loading: {items.error}")
    else:
        items_view = html.ul(html.li(item, key=item) for item in items_query.data)

    if add_item_mutation.loading:
        add_item_status = html.h2("Adding...")
    elif add_item_mutation.error:
        add_item_status = html.h2(f"Error when adding: {add_item_mutation.error}")
    else:
        add_item_status = ""

    def click_event(event):
        set_item_draft("")
        add_item_mutation.execute(text=item_draft)

    return html.div(
        html.label("Add an item:")
        html.input({"type": "text", "onClick": click_event})
        add_item_status,
        items_view,
    )
```

## Use Websocket

You can fetch the Django Channels websocket at any time by using `use_websocket`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_websocket

@component
def my_component():
    my_websocket = use_websocket()
    return html.div(my_websocket)
```

## Use Scope

This is a shortcut that returns the Websocket's `scope`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_scope

@component
def my_component():
    my_scope = use_scope()
    return html.div(my_scope)
```

## Use Location

??? info "This hook's behavior will be changed in a future update"

    This hook will be updated to return the browser's current URL. This change will come in alongside IDOM URL routing support.

    Check out [idom-team/idom#569](https://github.com/idom-team/idom/issues/569) for more information.

This is a shortcut that returns the Websocket's `path`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_location

@component
def my_component():
    my_location = use_location()
    return html.div(my_location)
```
