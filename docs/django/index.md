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

## Use Scope

This is a shortcut that returns the websocket's `scope`.

```python
from idom import component, html
from django_idom.hooks import use_scope

@component
def MyComponent():
    my_scope = use_scope()
    return html.div(my_scope)
```

## Use Location

Returns the URL that the websocket was opened from.

_Note: This will [eventually be updated](https://github.com/idom-team/idom/issues/569) to return the client's current webpage URL. This will come in conjunction with Single Page Application (SPA) support._

```python
from idom import component, html
from django_idom.hooks import use_location

@component
def MyComponent():
    my_location = use_location()
    return html.div(my_location)
```
