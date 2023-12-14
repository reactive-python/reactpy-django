from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable
from warnings import warn

from reactpy import component
from reactpy.core.types import ComponentConstructor, ComponentType, VdomDict

from reactpy_django.exceptions import DecoratorParamError
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
            return _user_passes_test(
                user_component, fallback, test_func, *args, **kwargs
            )

        return _wrapper

    return decorator


@component
def _user_passes_test(component_constructor, fallback, test_func, *args, **kwargs):
    """Dedicated component for `user_passes_test` to allow us to always have access to hooks."""
    user = use_user()

    if test_func(user):
        # Ensure that the component is a ReactPy component.
        user_component = component_constructor(*args, **kwargs)
        if not getattr(user_component, "render", None):
            raise DecoratorParamError(
                "`user_passes_test` is not decorating a ReactPy component. "
                "Did you forget `@user_passes_test` must be ABOVE the `@component` decorator?"
            )

        # Render the component.
        return user_component

    # Render the fallback component.
    # Returns an empty string if fallback is None, since ReactPy currently renders None as a string.
    # TODO: Remove this fallback when ReactPy can render None properly.
    return fallback(*args, **kwargs) if callable(fallback) else (fallback or "")
