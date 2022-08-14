???+ tip "Looking for more hooks?"

    Check out the [IDOM Core docs](https://idom-docs.herokuapp.com/docs/reference/hooks-api.html?highlight=hooks) on hooks!

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
