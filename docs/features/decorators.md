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

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | auth_attribute | `str` | The field to check within the user object. This value can be... <br><br> - One of the predefined `django_idom.AuthAttribute` values. <br> - A string for a custom user attribute to check. This is checked in the form of `UserModel.<auth_attribute>`. | `AuthAttribute.active` |
    | fallback | `ComponentType`, `VdomDict`, `None` | The component or VDOM (`idom.html` snippet) to render if the user is not authenticated. | `None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Component` | An IDOM component. |
    | `VdomDict` | An `idom.html` snippet. |
    | `None` | No component render. |

??? question "How do I render a different component if authentication fails?"

    ```python title="components.py"
    from django_idom.decorators import auth_required
    from django_idom.hooks import use_websocket
    from idom import component, html

    @component
    def my_component_fallback():
        return html.div("I'm not logged in!")

    @component
    @auth_required(fallback=my_component_fallback)
    def my_component():
        return html.div("This won't render if I'm not logged in!")
    ```

??? question "How do I render a simple `idom.html` snippet if authentication fails?"

    ```python title="components.py"
    from django_idom.decorators import auth_required
    from django_idom.hooks import use_websocket
    from idom import component, html

    @component
    @auth_required(fallback=html.div("I'm not logged in!"))
    def my_component():
        return html.div("This won't render if I'm not logged in!")
    ```

??? question "How can I check if a user `is_staff`?"

    ```python title="components.py"
    from django_idom.decorators import auth_required
    from django_idom.hooks import use_websocket
    from django_idom import AuthAttribute
    from idom import component, html


    @component
    @auth_required(auth_attribute=AuthAttribute.staff)
    def my_component():
        return html.div("This won't render if I'm not logged in!")
    ```

??? question "How can I check for a custom attribute?"

    You will need to be using a [custom user model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-a-custom-user-model) within your Django instance.

    For example, if your user model has the field `is_really_cool` ...

    ```python
    from django.contrib.auth.models import AbstractBaseUser

    class CustomUserModel(AbstractBaseUser):
        @property
        def is_really_cool(self):
            return self.name == "Groot"
    ```

    ... then you would do the following within your decorator:

    ```python title="components.py"
    from django_idom.decorators import auth_required
    from django_idom.hooks import use_websocket
    from idom import component, html

    @component
    @auth_required(auth_attribute="is_really_cool")
    def my_component():
        return html.div("This won't render if I'm not logged in!")
    ```
