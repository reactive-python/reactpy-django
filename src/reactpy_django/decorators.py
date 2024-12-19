from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

from reactpy import component

from reactpy_django.exceptions import DecoratorParamError
from reactpy_django.hooks import use_user

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from reactpy.core.types import ComponentConstructor


def user_passes_test(
    test_func: Callable[[AbstractUser], bool],
    /,
    fallback: Any | None = None,
) -> ComponentConstructor:
    """You can limit component access to users that pass a test function by using this decorator.

    This decorator is inspired by Django's `user_passes_test` decorator, but works with ReactPy components.

    Args:
        test_func: A function that accepts a `User` returns a boolean.
        fallback: The content to be rendered if the test fails. Typically is a ReactPy component or \
            VDOM (`reactpy.html` snippet).
    """

    def decorator(user_component):
        @wraps(user_component)
        def _wrapper(*args, **kwargs):
            return _user_passes_test(user_component, fallback, test_func, *args, **kwargs)

        return _wrapper

    return decorator  # type: ignore


@component  # type: ignore
def _user_passes_test(component_constructor, fallback, test_func, *args, **kwargs):
    """Dedicated component for `user_passes_test` to allow us to always have access to hooks."""
    user = use_user()

    if test_func(user):
        # Ensure that the component is a ReactPy component.
        user_component = component_constructor(*args, **kwargs)
        if not getattr(user_component, "render", None):
            msg = (
                "`user_passes_test` is not decorating a ReactPy component. "
                "Did you forget `@user_passes_test` must be ABOVE the `@component` decorator?"
            )
            raise DecoratorParamError(msg)

        # Render the component.
        return user_component

    # Render the fallback content.
    return fallback(*args, **kwargs) if callable(fallback) else (fallback or None)
