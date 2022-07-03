from functools import wraps
from typing import Callable, Union

from idom.core.types import ComponentType, VdomDict

from django_idom.hooks import use_websocket
from django_idom.types import AuthLevel


def authenticated(
    component: Union[Callable, None] = None,
    auth_level: str = AuthLevel.user,
    fallback: Union[ComponentType, VdomDict, None] = None,
) -> ComponentType | VdomDict | Callable | None:
    """If the user is authenticated, the decorated component will be rendered.
    Otherwise, the fallback component will be rendered.

    This decorator can be used with or without paranthesis.

    Args:
        auth_level: The user's auth level. This value can be
           - One of the predefined `django_idom.AuthLevel` values
           - A string for a custom user attribute to check (ex. `UserModel.is_<auth_level>`).
        fallback: The component to render if the user is not authenticated.
    """

    def decorator(component):
        @wraps(component)
        def _wrapped_func(*args, **kwargs):
            websocket = use_websocket()

            if getattr(websocket.scope["user"], f"is_{auth_level}", False):
                return component(*args, **kwargs)

            if callable(fallback):
                return fallback(*args, **kwargs)
            return fallback

        return _wrapped_func

    # Return when used as @authenticated
    if component is None:
        return decorator

    # Return when used as @authenticated(...)
    return decorator(component)
