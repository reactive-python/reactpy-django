from functools import wraps
from typing import Callable, Union

from idom.core.types import ComponentType, VdomDict

from django_idom.hooks import use_websocket
from django_idom.types import AuthAttribute


def auth_required(
    component: Union[Callable, None] = None,
    auth_attribute: str = AuthAttribute.active,
    fallback: Union[ComponentType, VdomDict, None] = None,
) -> Callable:
    """If the user passes authentication criteria, the decorated component will be rendered.
    Otherwise, the fallback component will be rendered.

    This decorator can be used with or without parentheses.

    Args:
        auth_attribute: The field to check within the user object. This value can be
           - One of the predefined `django_idom.AuthAttribute` values.
           - A string for a custom user attribute to check (ex. `UserModel.is_<auth_attribute>`).
        fallback: The component or VDOM (`idom.html` snippet) to render if the user is not authenticated.
    """

    def decorator(component):
        @wraps(component)
        def _wrapped_func(*args, **kwargs):
            websocket = use_websocket()

            if getattr(websocket.scope["user"], f"is_{auth_attribute}", False):
                return component(*args, **kwargs)

            if callable(fallback):
                return fallback(*args, **kwargs)
            return fallback

        return _wrapped_func

    # Return when used as @authenticated(...)
    if component is None:
        return decorator

    # Return when used as @authenticated
    return decorator(component)
