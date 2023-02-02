???+ summary

    Decorator utilities can be used within your `components.py` to help simplify development.

## Auth Required

You can limit access to a component to users with a specific `auth_attribute` by using this decorator (with or without parentheses).

By default, this decorator checks if the user is logged in, and his/her account has not been deactivated.

This decorator is commonly used to selectively render a component only if a user [`is_staff`](https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.User.is_staff) or [`is_superuser`](https://docs.djangoproject.com/en/dev/ref/contrib/auth/#django.contrib.auth.models.User.is_superuser).

=== "components.py"

    ```python
    from django_idom.decorators import auth_required
    from idom import component, html

    @component
    @auth_required
    def my_component():
        return html.div("I am logged in!")
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `auth_attribute` | `str` | The value to check within the user object. This is checked in the form of `UserModel.<auth_attribute>`. | `#!python "is_active"` |
    | `fallback` | `ComponentType`, `VdomDict`, `None` | The `component` or `idom.html` snippet to render if the user is not authenticated. | `None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Component` | An IDOM component. |
    | `VdomDict` | An `idom.html` snippet. |
    | `None` | No component render. |

??? question "How do I render a different component if authentication fails?"

    You can use a component with the `fallback` argument, as seen below.

    === "components.py"

        ```python
        from django_idom.decorators import auth_required
        from idom import component, html

        @component
        def my_component_fallback():
            return html.div("I am NOT logged in!")

        @component
        @auth_required(fallback=my_component_fallback)
        def my_component():
            return html.div("I am logged in!")
        ```

??? question "How do I render a simple `idom.html` snippet if authentication fails?"

    You can use a `idom.html` snippet with the `fallback` argument, as seen below.

    === "components.py"

        ```python
        from django_idom.decorators import auth_required
        from idom import component, html

        @component
        @auth_required(fallback=html.div("I am NOT logged in!"))
        def my_component():
            return html.div("I am logged in!")
        ```

??? question "How can I check if a user `is_staff`?"

    You can set the `auth_attribute` to `is_staff`, as seen blow.

    === "components.py"

        ```python
        from django_idom.decorators import auth_required
        from idom import component, html


        @component
        @auth_required(auth_attribute="is_staff")
        def my_component():
            return html.div("I am logged in!")
        ```

??? question "How can I check for a custom attribute?"

    You will need to be using a [custom user model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-a-custom-user-model) within your Django instance.

    For example, if your user model has the field `is_really_cool` ...

    === "models.py"

        ```python
        from django.contrib.auth.models import AbstractBaseUser

        class CustomUserModel(AbstractBaseUser):
            @property
            def is_really_cool(self):
                return True
        ```

    ... then you would do the following within your decorator:

    === "components.py"

        ```python
        from django_idom.decorators import auth_required
        from idom import component, html

        @component
        @auth_required(auth_attribute="is_really_cool")
        def my_component():
            return html.div("I am logged in!")
        ```
