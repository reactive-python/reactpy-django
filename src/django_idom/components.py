import os
from inspect import iscoroutinefunction
from typing import Callable, Dict, Iterable, Union

from channels.db import database_sync_to_async
from django.contrib.staticfiles.finders import find
from django.http import HttpRequest
from django.urls import reverse
from django.views import View
from idom import component, hooks, html, utils
from idom.types import VdomDict

from django_idom.config import IDOM_CACHE, IDOM_VIEW_COMPONENT_IFRAMES
from django_idom.types import ViewComponentIframe


@component
def view_to_component(
    view: Union[Callable, View],
    compatibility: bool = False,
    strict_parsing: bool = True,
    request: Union[HttpRequest, None] = None,
    args: Union[Iterable, None] = None,
    kwargs: Union[Dict, None] = None,
) -> Union[VdomDict, None]:
    """Converts a Django view to an IDOM component.

    Args:
        view: The view function or class to convert.

    Keyword Args:
        compatibility: If True, the component will be rendered in an iframe.
        strict_parsing: If True, an exception will be generated if the HTML does not
            perfectly adhere to HTML5.
        request: Request object to provide to the view.
        args: The positional arguments to pass to the view.
        kwargs: The keyword arguments to pass to the view.
    """
    args = args or []
    kwargs = kwargs or {}

    # Return the view if it's been rendered via the `async_renderer`
    rendered_view, set_rendered_view = hooks.use_state(None)
    if rendered_view:
        return html._(
            utils.html_to_vdom(
                rendered_view.content.decode("utf-8").strip(), strict=strict_parsing
            )
        )

    # Create a synthetic request object.
    request_obj = request
    if not request:
        request_obj = HttpRequest()
        # TODO: Figure out some intelligent way to set the method.
        # Might need intercepting common things such as form submission?
        request_obj.method = "GET"

    # Render Check 1: Compatibility mode
    if compatibility:
        dotted_path = f"{view.__module__}.{view.__name__}"
        dotted_path = dotted_path.replace("<", "").replace(">", "")

        # Register the iframe's URL if needed
        IDOM_VIEW_COMPONENT_IFRAMES[dotted_path] = ViewComponentIframe(
                view, args, kwargs
            )

        return html.iframe(
            {
                "src": reverse("idom:view_to_component", args=[dotted_path]),
                "loading": "lazy",
            }
        )

    # Asynchronous view rendering via hooks
    @hooks.use_effect(dependencies=[rendered_view])
    async def async_renderer():
        """Render the view in an async hook to avoid blocking the main thread."""
        if rendered_view:
            return

        # Render Check 2: Async function view
        if iscoroutinefunction(view):
            render = await view(request_obj, *args, **kwargs)

        # Render Check 3: Async class view
        elif getattr(view, "view_is_async", False):
            async_cbv = view.as_view()
            async_view = await async_cbv(request_obj, *args, **kwargs)
            if getattr(async_view, "render", None):
                render = await async_view.render()
            else:
                render = async_view

        # Render Check 4: Sync class view
        elif getattr(view, "as_view", None):
            async_cbv = database_sync_to_async(view.as_view())
            async_view = await async_cbv(request_obj, *args, **kwargs)
            if getattr(async_view, "render", None):
                render = await database_sync_to_async(async_view.render)()
            else:
                render = async_view

        # Render Check 5: Sync function view
        else:
            render = await database_sync_to_async(view)(request_obj, *args, **kwargs)

        set_rendered_view(render)


@component
def django_css(static_path: str):
    """Fetches a CSS static file for use within IDOM. This allows for deferred CSS loading.

    Args:
        static_path: The path to the static file. This path is identical to what you would
        use on a `static` template tag.
    """
    return html.style(_cached_static_contents(static_path))


@component
def django_js(static_path: str):
    """Fetches a JS static file for use within IDOM. This allows for deferred JS loading.

    Args:
        static_path: The path to the static file. This path is identical to what you would
        use on a `static` template tag.
    """
    return html.script(_cached_static_contents(static_path))


def _cached_static_contents(static_path: str):
    # Try to find the file within Django's static files
    abs_path = find(static_path)
    if not abs_path:
        raise FileNotFoundError(
            f"Could not find static file {static_path} within Django's static files."
        )

    # Fetch the file from cache, if available
    # Cache is preferrable to `use_memo` due to multiprocessing capabilities
    last_modified_time = os.stat(abs_path).st_mtime
    cache_key = f"django_idom:static_contents:{static_path}"
    file_contents = IDOM_CACHE.get(cache_key, version=last_modified_time)
    if file_contents is None:
        with open(abs_path, encoding="utf-8") as static_file:
            file_contents = static_file.read()
        IDOM_CACHE.delete(cache_key)
        IDOM_CACHE.set(
            cache_key, file_contents, timeout=None, version=last_modified_time
        )

    return file_contents
