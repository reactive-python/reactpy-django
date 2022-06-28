from inspect import isclass, iscoroutinefunction
from typing import Callable

from asgiref.sync import async_to_sync
from django.urls import reverse
from idom import component, html, utils
from idom.core.component import Component

from django_idom.config import IDOM_REGISTERED_IFRAMES
from django_idom.types import ViewToComponentIframe


def view_to_component(
    middleware: list[Callable | str], compatibility: bool = False, *args, **kwargs
) -> Component | object:
    """Converts a Django view to an IDOM component.

    Args:
        middleware: The list of middleware to use when rendering the component.
        compatibility: If True, the component will be rendered in an iframe.
        *args: The positional arguments to pass to the view.

    Keyword Args:
        **kwargs: The keyword arguments to pass to the view.
    """

    def decorator(view):

        dotted_path = f"{view.__module__}.{view.__name__}".replace("<", "").replace(
            ">", ""
        )

        @component
        def new_component():
            if compatibility:
                return html.iframe(
                    {
                        "src": reverse("idom:view_to_component", args=[dotted_path]),
                        "loading": "lazy",
                    }
                )

            # TODO: Apply middleware using some helper function
            if isclass(view):
                rendered_view = view.as_view()(*args, **kwargs)
            elif iscoroutinefunction(view):
                rendered_view = async_to_sync(view)(*args, **kwargs)
            else:
                rendered_view = view(*args, **kwargs)

            return html._(utils.html_to_vdom(rendered_view))

        IDOM_REGISTERED_IFRAMES[dotted_path] = ViewToComponentIframe(
            middleware, view, new_component, args, kwargs
        )

        return new_component

    return decorator
