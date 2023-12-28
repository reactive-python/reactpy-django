from __future__ import annotations

import json
import os
from typing import Any, Callable, Sequence, Union, cast, overload
from urllib.parse import urlencode
from warnings import warn

from django.contrib.staticfiles.finders import find
from django.core.cache import caches
from django.http import HttpRequest
from django.urls import reverse
from django.views import View
from reactpy import component, hooks, html, utils
from reactpy.types import Key, VdomDict

from reactpy_django.exceptions import ViewNotRegisteredError
from reactpy_django.utils import generate_obj_name, import_module, render_view


# Type hints for:
#   1. example = view_to_component(my_view, ...)
#   2. @view_to_component
@overload
def view_to_component(
    view: Callable | View | str,
    compatibility: bool = False,
    transforms: Sequence[Callable[[VdomDict], Any]] = (),
    strict_parsing: bool = True,
) -> Any:
    ...


# Type hints for:
#   1. @view_to_component(...)
@overload
def view_to_component(
    view: None = ...,
    compatibility: bool = False,
    transforms: Sequence[Callable[[VdomDict], Any]] = (),
    strict_parsing: bool = True,
) -> Callable[[Callable], Any]:
    ...


def view_to_component(
    view: Callable | View | str | None = None,
    compatibility: bool = False,
    transforms: Sequence[Callable[[VdomDict], Any]] = (),
    strict_parsing: bool = True,
) -> Any | Callable[[Callable], Any]:
    """Converts a Django view to a ReactPy component.

    Keyword Args:
        view: The view to convert, or the view's dotted path as a string.
        compatibility: **DEPRECATED.** Use `view_to_iframe` instead.
        transforms: A list of functions that transforms the newly generated VDOM. \
            The functions will be called on each VDOM node.
        strict_parsing: If True, an exception will be generated if the HTML does not \
            perfectly adhere to HTML5.

    Returns:
        A function that takes `request, *args, key, **kwargs` and returns a ReactPy component.
    """

    def decorator(view: Callable | View | str):
        if not view:
            raise ValueError("A view must be provided to `view_to_component`")

        def constructor(
            request: HttpRequest | None = None,
            *args,
            key: Key | None = None,
            **kwargs,
        ):
            return _view_to_component(
                view=view,
                compatibility=compatibility,
                transforms=transforms,
                strict_parsing=strict_parsing,
                request=request,
                args=args,
                kwargs=kwargs,
                key=key,
            )

        return constructor

    if not view:
        warn(
            "Using `view_to_component` as a decorator is deprecated. "
            "This functionality will be removed in a future version.",
            DeprecationWarning,
        )

    return decorator(view) if view else decorator


def view_to_iframe(
    view: Callable | View | str, extra_props: dict[str, Any] | None = None
):
    """
    Args:
        view: The view function or class to convert, or the dotted path to the view.

    Keyword Args:
        extra_props: Additional properties to add to the `iframe` element.

    Returns:
        A function that takes `*args, key, **kwargs` and returns a ReactPy component.
    """

    def constructor(
        *args,
        key: Key | None = None,
        **kwargs,
    ):
        return _view_to_iframe(
            view=view, extra_props=extra_props, args=args, kwargs=kwargs, key=key
        )

    return constructor


def django_css(static_path: str, key: Key | None = None):
    """Fetches a CSS static file for use within ReactPy. This allows for deferred CSS loading.

    Args:
        static_path: The path to the static file. This path is identical to what you would \
            use on Django's `{% static %}` template tag
        key: A key to uniquely identify this component which is unique amongst a component's \
            immediate siblings
    """

    return _django_css(static_path=static_path, key=key)


def django_js(static_path: str, key: Key | None = None):
    """Fetches a JS static file for use within ReactPy. This allows for deferred JS loading.

    Args:
        static_path: The path to the static file. This path is identical to what you would \
            use on Django's `{% static %}` template tag.
        key: A key to uniquely identify this component which is unique amongst a component's \
            immediate siblings
    """

    return _django_js(static_path=static_path, key=key)


@component
def _view_to_component(
    view: Callable | View | str,
    compatibility: bool,
    transforms: Sequence[Callable[[VdomDict], Any]],
    strict_parsing: bool,
    request: HttpRequest | None,
    args: Sequence | None,
    kwargs: dict | None,
):
    """The actual component. Used to prevent pollution of acceptable kwargs keys."""
    converted_view, set_converted_view = hooks.use_state(
        cast(Union[VdomDict, None], None)
    )
    _args: Sequence = args or ()
    _kwargs: dict = kwargs or {}
    if request:
        _request: HttpRequest = request
    else:
        _request = HttpRequest()
        _request.method = "GET"
    resolved_view: Callable = import_module(view) if isinstance(view, str) else view  # type: ignore[assignment]

    # Render the view render within a hook
    @hooks.use_effect(
        dependencies=[
            json.dumps(vars(_request), default=lambda x: generate_obj_name(x)),
            json.dumps([_args, _kwargs], default=lambda x: generate_obj_name(x)),
        ]
    )
    async def async_render():
        """Render the view in an async hook to avoid blocking the main thread."""
        # Compatibility mode doesn't require a traditional render
        if compatibility:
            return

        # Render the view
        response = await render_view(resolved_view, _request, _args, _kwargs)
        set_converted_view(
            utils.html_to_vdom(
                response.content.decode("utf-8").strip(),
                utils.del_html_head_body_transform,
                *transforms,
                strict=strict_parsing,
            )
        )

    # Render in compatibility mode, if needed
    if compatibility:
        # Warn the user that compatibility mode is deprecated
        warn(
            "view_to_component(compatibility=True) is deprecated and will be removed in a future version. "
            "Please use `view_to_iframe` instead.",
            DeprecationWarning,
        )

        return view_to_iframe(resolved_view)(*_args, **_kwargs)

    # Return the view if it's been rendered via the `async_render` hook
    return converted_view


@component
def _view_to_iframe(
    view: Callable | View | str,
    extra_props: dict[str, Any] | None,
    args: Sequence,
    kwargs: dict,
) -> VdomDict:
    """The actual component. Used to prevent pollution of acceptable kwargs keys."""
    from reactpy_django.config import REACTPY_REGISTERED_IFRAME_VIEWS

    if hasattr(view, "view_class"):
        view = view.view_class
    dotted_path = view if isinstance(view, str) else generate_obj_name(view)
    registered_view = REACTPY_REGISTERED_IFRAME_VIEWS.get(dotted_path)

    if not registered_view:
        raise ViewNotRegisteredError(
            f"'{dotted_path}' has not been registered as an iframe! "
            "Are you sure you called `register_iframe` within a Django `AppConfig.ready` method?"
        )

    query = kwargs.copy()
    if args:
        query["_args"] = args
    query_string = f"?{urlencode(query, doseq=True)}" if args or kwargs else ""
    extra_props = extra_props or {}
    extra_props.pop("src", None)

    return html.iframe(
        {
            "src": reverse("reactpy:view_to_iframe", args=[dotted_path]) + query_string,
            "style": {"border": "none"},
            "onload": 'javascript:(function(o){o.style.height=o.contentWindow.document.body.scrollHeight+"px";}(this));',
            "loading": "lazy",
        }
        | extra_props
    )


@component
def _django_css(static_path: str):
    return html.style(_cached_static_contents(static_path))


@component
def _django_js(static_path: str):
    return html.script(_cached_static_contents(static_path))


def _cached_static_contents(static_path: str):
    from reactpy_django.config import REACTPY_CACHE

    # Try to find the file within Django's static files
    abs_path = find(static_path)
    if not abs_path:
        raise FileNotFoundError(
            f"Could not find static file {static_path} within Django's static files."
        )

    # Fetch the file from cache, if available
    last_modified_time = os.stat(abs_path).st_mtime
    cache_key = f"reactpy_django:static_contents:{static_path}"
    file_contents = caches[REACTPY_CACHE].get(
        cache_key, version=int(last_modified_time)
    )
    if file_contents is None:
        with open(abs_path, encoding="utf-8") as static_file:
            file_contents = static_file.read()
        caches[REACTPY_CACHE].delete(cache_key)
        caches[REACTPY_CACHE].set(
            cache_key, file_contents, timeout=None, version=int(last_modified_time)
        )

    return file_contents
