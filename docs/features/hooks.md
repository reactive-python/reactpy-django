# Django Hooks

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

---

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

---

## Use Location

??? info "This hook's behavior will be changed in a future update"

    This hook will eventually be updated to return the client's current webpage URL. This will come in alongside our built-in [Single Page Application (SPA) support](https://github.com/idom-team/idom/issues/569).

This is a shortcut that returns the Websocket's `path`.

```python title="components.py"
from idom import component, html
from django_idom.hooks import use_location

@component
def MyComponent():
    my_location = use_location()
    return html.div(my_location)
```
