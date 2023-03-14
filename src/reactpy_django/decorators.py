from __future__ import annotations

from functools import wraps
from typing import Callable

from reactpy.core.types import ComponentType, VdomDict

from reactpy_django.hooks import use_scope


def auth_required(
    component: Callable | None = None,
    auth_attribute: str = "is_active",
    fallback: ComponentType | Callable | VdomDict | None = None,
) -> Callable:
    """If the user passes authentication criteria, the decorated component will be rendered.
    Otherwise, the fallback component will be rendered.

    This decorator can be used with or without parentheses.

    Args:
        auth_attribute: The value to check within the user object.
            This is checked in the form of `UserModel.<auth_attribute>`.
        fallback: The component or VDOM (`reactpy.html` snippet) to render if the user is not authenticated.
    """

    def decorator(component):
        @wraps(component)
        def _wrapped_func(*args, **kwargs):
            scope = use_scope()

            if getattr(scope["user"], auth_attribute):
                return component(*args, **kwargs)
            return fallback(*args, **kwargs) if callable(fallback) else fallback

        return _wrapped_func

    # Return for @authenticated(...) and @authenticated respectively
    return decorator if component is None else decorator(component)
