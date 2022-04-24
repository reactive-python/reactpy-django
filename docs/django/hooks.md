# Django Hooks

## Use Websocket

You can fetch the Django Channels websocket at any time by using `use_websocket`.

```python
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

```python
from idom import component, html
from django_idom.hooks import use_scope

@component
def MyComponent():
    my_scope = use_scope()
    return html.div(my_scope)
```

---

## Use Location

This is a shortcut that returns the Websocket's `path`.

!!! note

        This hook will [eventually be updated](https://github.com/idom-team/idom/issues/569) to return the client's current webpage URL. This will come in conjunction with Single Page Application (SPA) support.

```python
from idom import component, html
from django_idom.hooks import use_location

@component
def MyComponent():
    my_location = use_location()
    return html.div(my_location)
```
