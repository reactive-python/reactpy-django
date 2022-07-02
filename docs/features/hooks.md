???+ tip "Looking for more hooks?"

    Check out the [IDOM Core docs](https://idom-docs.herokuapp.com/docs/reference/hooks-api.html?highlight=hooks) on hooks!

## Use Sync to Async

This is the suggested method of performing ORM queries when using Django IDOM. 

Fundamentally, this hook is an ORM-safe version of [use_effect](https://idom-docs.herokuapp.com/docs/reference/hooks-api.html#use-effect).

```python title="components.py"
from example_project.my_app.models import Category
from channels.db import database_sync_to_async
from idom import component, html
from django_idom import hooks

@component
def simple_list():
    categories, set_categories = hooks.use_state(None)

    @hooks.use_sync_to_async
    def get_categories():
        if categories:
            return
        set_categories(Category.objects.all())

    if not categories:
        return html.h2("Loading...")

    return html.ul(
        [html.li(category.name, key=category.name) for category in categories]
    )
```

??? question "Why can't I make ORM calls without hooks?"

    Due to Django's ORM design, database queries must be deferred using hooks. Otherwise, you will see a `SynchronousOnlyOperation` exception.

## Use Websocket

You can fetch the Django Channels websocket at any time by using `use_websocket`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_websocket

@component
def MyComponent():
    my_websocket = use_websocket()
    return html.div(my_websocket)
```

## Use Scope

This is a shortcut that returns the Websocket's `scope`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_scope

@component
def MyComponent():
    my_scope = use_scope()
    return html.div(my_scope)
```

## Use Location

??? info "This hook's behavior will be changed in a future update"

    This hook will be updated to return the browser's current URL. This will come in alongside our built-in [Single Page Application (SPA) support](https://github.com/idom-team/idom/issues/569).

This is a shortcut that returns the Websocket's `path`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_location

@component
def MyComponent():
    my_location = use_location()
    return html.div(my_location)
```
