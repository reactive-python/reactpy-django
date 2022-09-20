from __future__ import annotations

import json
import os
from inspect import iscoroutinefunction
from typing import Any, Callable, Dict, Iterable

from channels.db import database_sync_to_async
from django.contrib.staticfiles.finders import find
from django.http import HttpRequest
from django.urls import reverse
from django.views import View
from idom import component, hooks, html, utils
from idom.types import VdomDict

from django_idom.config import IDOM_CACHE, IDOM_VIEW_COMPONENT_IFRAMES
from django_idom.types import ViewComponentIframe


# TODO: Might want to intercept href clicks and form submit events.
# Form events will probably be accomplished through the upcoming DjangoForm.
@component
def view_to_component(
    view: Callable | View,
    compatibility: bool = False,
    transforms: Iterable[Callable[[VdomDict], Any]] = (),
    strict_parsing: bool = True,
    request: HttpRequest | None = None,
    args: Iterable = (),
    kwargs: Dict | None = None,
) -> VdomDict | None:
    """Converts a Django view to an IDOM component.

    Args:
        view: The view function or class to convert.

    Keyword Args:
        compatibility: If True, the component will be rendered in an iframe.
            When using compatibility mode `tranforms`, `strict_parsing`, and `request`
            arguments will be ignored.
        transforms: A list of functions that transforms the newly generated VDOM.
            The functions will be called on each VDOM node.
        strict_parsing: If True, an exception will be generated if the HTML does not
            perfectly adhere to HTML5.
        request: Request object to provide to the view.
        args: The positional arguments to pass to the view.
        kwargs: The keyword arguments to pass to the view.
    """
    kwargs = kwargs or {}
    rendered_view, set_rendered_view = hooks.use_state(None)
    request_obj = request
    if not request:
        request_obj = HttpRequest()
        request_obj.method = "GET"

    # Render the view render within a hook
    @hooks.use_effect(
        dependencies=[
            json.dumps(vars(request_obj), default=lambda x: _generate_obj_name(x)),
            json.dumps([args, kwargs], default=lambda x: _generate_obj_name(x)),
        ]
    )
    async def async_renderer():
        """Render the view in an async hook to avoid blocking the main thread."""
        # Render Check 1: Compatibility mode
        if compatibility:
            dotted_path = f"{view.__module__}.{view.__name__}"
            dotted_path = dotted_path.replace("<", "").replace(">", "")
            IDOM_VIEW_COMPONENT_IFRAMES[dotted_path] = ViewComponentIframe(
                view, args, kwargs
            )

            # Signal that the view has been rendered
            set_rendered_view(
                html.iframe(
                    {
                        "src": reverse("idom:view_to_component", args=[dotted_path]),
                        "loading": "lazy",
                    }
                )
            )
            return

        # Render Check 2: Async function view
        elif iscoroutinefunction(view):
            render = await view(request_obj, *args, **kwargs)

        # Render Check 3: Async class view
        elif getattr(view, "view_is_async", False):
            view_or_template_view = await view.as_view()(request_obj, *args, **kwargs)
            if getattr(view_or_template_view, "render", None):  # TemplateView
                render = await view_or_template_view.render()
            else:  # View
                render = view_or_template_view

        # Render Check 4: Sync class view
        elif getattr(view, "as_view", None):
            async_cbv = database_sync_to_async(view.as_view())
            view_or_template_view = await async_cbv(request_obj, *args, **kwargs)
            if getattr(view_or_template_view, "render", None):  # TemplateView
                render = await database_sync_to_async(view_or_template_view.render)()
            else:  # View
                render = view_or_template_view

        # Render Check 5: Sync function view
        else:
            render = await database_sync_to_async(view)(request_obj, *args, **kwargs)

        # Signal that the view has been rendered
        set_rendered_view(
            utils.html_to_vdom(
                render.content.decode("utf-8").strip(),
                *transforms,
                strict=strict_parsing,
            )
        )

    # Return the view if it's been rendered via the `async_renderer` hook
    return rendered_view


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
    file_contents = IDOM_CACHE.get(cache_key, version=int(last_modified_time))
    if file_contents is None:
        with open(abs_path, encoding="utf-8") as static_file:
            file_contents = static_file.read()
        IDOM_CACHE.delete(cache_key)
        IDOM_CACHE.set(
            cache_key, file_contents, timeout=None, version=int(last_modified_time)
        )

    return file_contents


def _generate_obj_name(object: Any) -> str | None:
    """Makes a best effort to create a name for an object.
    Useful for JSON serialization of Python objects."""
    if hasattr(object, "__module__"):
        if hasattr(object, "__name__"):
            return f"{object.__module__}.{object.__name__}"
        if hasattr(object, "__class__"):
            return f"{object.__module__}.{object.__class__.__name__}"
    return None
