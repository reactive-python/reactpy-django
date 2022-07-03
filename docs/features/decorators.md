## Auth Required

You can limit access to a component via an `auth_level` by using this decorator.

Common uses of this decorator are to hide components from `AnonymousUser`, or only render a component to `staff` or `superuser` members.

This decorator can be used with or without paranthesis.

```python title="components.py"
from django_idom.decorators import auth_required
from django_idom.hooks import use_websocket
from idom import component, html

@component
@auth_required
def my_component():
    return html.div("This won't render if I'm not logged in!")
```

??? example "See Interface"

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | auth_level | `str` | The user's auth level. This value can be... <br><br> - One of the predefined `django_idom.AuthLevel` values. <br> - A string for a custom user attribute to check. This is checked in the form of `UserModel.is_<auth_level>`. | `AuthLevel.active` |
    | fallback | `ComponentType`, `VdomDict`, `None` | The component or VDOM (`idom.html` snippet) to render if the user is not authenticated. | `None` |

