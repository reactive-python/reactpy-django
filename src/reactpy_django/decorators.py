from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable
from warnings import warn

from reactpy.core.types import ComponentType, VdomDict

from reactpy_django.hooks import use_scope, use_user

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


def auth_required(
    component: Callable | None = None,
    auth_attribute: str = "is_active",
    fallback: ComponentType | Callable | VdomDict | None = None,
) -> Callable:
    """If the user passes authentication criteria, the decorated component will be rendered.
    Otherwise, the fallback component will be rendered.

    This decorator can be used with or without parentheses.

    Args:
        auth_attribute: The value to check within the user object. \
            This is checked in the form of `UserModel.<auth_attribute>`. \
        fallback: The component or VDOM (`reactpy.html` snippet) to render if the user is not authenticated.
    """

    warn(
        "auth_required is deprecated and will be removed in the next major version. "
        "An equivalent to this decorator's default is @user_passes_test('is_active').",
        DeprecationWarning,
    )

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


def user_passes_test(
    test_func: Callable[[AbstractUser], bool],
    fallback: Any | None = None,
) -> Callable:
    """Imitation of Django's `user_passes_test` decorator that works with components.
    This decorator runs your test function on the websocket connection's `user`. If the test passes,
    then decorated component will be rendered. Otherwise, the fallback component will be rendered.

    Args:
        test_func: The function that returns a boolean.
        fallback: The content to be rendered if the test fails. Typically is a ReactPy component or \
            VDOM (`reactpy.html` snippet).
    """

    def decorator(component):
        @wraps(component)
        def _wrapper(*args, **kwargs):
            user = use_user()

            # Run the test and render the component if it passes.
            if test_func(user):
                return component(*args, **kwargs)

            # Render the fallback component.
            return fallback(*args, **kwargs) if callable(fallback) else fallback

        return _wrapper

    return decorator
