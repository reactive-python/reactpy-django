## Auth Required

You can limit access to a component to a specific `auth_attribute` by using this decorator.

Common uses of this decorator are to hide components from `AnonymousUser`, or render a component to only `staff` or `superuser` members.

This decorator can be used with or without parentheses.

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
    | auth_attribute | `str` | The field to check within the user object. This value can be... <br><br> - One of the predefined `django_idom.AuthAttribute` values. <br> - A string for a custom user attribute to check. This is checked in the form of `UserModel.is_<auth_attribute>`. | `AuthAttribute.active` |
    | fallback | `ComponentType`, `VdomDict`, `None` | The component or VDOM (`idom.html` snippet) to render if the user is not authenticated. | `None` |

