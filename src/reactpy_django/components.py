"""This file contains Django related components. Most of these components utilize wrappers to fix type hints."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Callable, Union, cast
from urllib.parse import urlencode

from django.http import HttpRequest
from django.urls import reverse
from reactpy import component, hooks, html, utils
from reactpy.types import ComponentType, Key, VdomDict

from reactpy_django.exceptions import ViewNotRegisteredError
from reactpy_django.forms.components import _django_form
from reactpy_django.pyscript.components import _pyscript_component
from reactpy_django.utils import cached_static_file, generate_obj_name, import_module, render_view

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.forms import Form, ModelForm
    from django.views import View

    from reactpy_django.types import AsyncFormEvent, SyncFormEvent, ViewToComponentConstructor, ViewToIframeConstructor


def view_to_component(
    view: Callable | View | str,
    transforms: Sequence[Callable[[VdomDict], Any]] = (),
    strict_parsing: bool = True,
) -> ViewToComponentConstructor:
    """Converts a Django view to a ReactPy component.

    Keyword Args:
        view: The view to convert, or the view's dotted path as a string.
        transforms: A list of functions that transforms the newly generated VDOM. \
            The functions will be called on each VDOM node.
        strict_parsing: If True, an exception will be generated if the HTML does not \
            perfectly adhere to HTML5.

    Returns:
        A function that takes `request, *args, key, **kwargs` and returns a ReactPy component.
    """

    def constructor(
        request: HttpRequest | None = None,
        *args,
        key: Key | None = None,
        **kwargs,
    ) -> ComponentType:
        return _view_to_component(
            view=view,
            transforms=transforms,
            strict_parsing=strict_parsing,
            request=request,
            args=args,
            kwargs=kwargs,
            key=key,
        )

    return constructor


def view_to_iframe(view: Callable | View | str, extra_props: dict[str, Any] | None = None) -> ViewToIframeConstructor:
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
    ) -> ComponentType:
        return _view_to_iframe(view=view, extra_props=extra_props, args=args, kwargs=kwargs, key=key)

    return constructor


def django_css(static_path: str, key: Key | None = None) -> ComponentType:
    """Fetches a CSS static file for use within ReactPy. This allows for deferred CSS loading.

    Args:
        static_path: The path to the static file. This path is identical to what you would \
            use on Django's `{% static %}` template tag
        key: A key to uniquely identify this component which is unique amongst a component's \
            immediate siblings
    """

    return _django_css(static_path=static_path, key=key)


def django_js(static_path: str, key: Key | None = None) -> ComponentType:
    """Fetches a JS static file for use within ReactPy. This allows for deferred JS loading.

    Args:
        static_path: The path to the static file. This path is identical to what you would \
            use on Django's `{% static %}` template tag.
        key: A key to uniquely identify this component which is unique amongst a component's \
            immediate siblings
    """

    return _django_js(static_path=static_path, key=key)


def django_form(
    form: type[Form | ModelForm],
    *,
    on_success: AsyncFormEvent | SyncFormEvent | None = None,
    on_error: AsyncFormEvent | SyncFormEvent | None = None,
    on_receive_data: AsyncFormEvent | SyncFormEvent | None = None,
    on_change: AsyncFormEvent | SyncFormEvent | None = None,
    auto_save: bool = True,
    extra_props: dict[str, Any] | None = None,
    extra_transforms: Sequence[Callable[[VdomDict], Any]] | None = None,
    form_template: str | None = None,
    thread_sensitive: bool = True,
    top_children: Sequence[Any] = (),
    bottom_children: Sequence[Any] = (),
    key: Key | None = None,
) -> ComponentType:
    """Converts a Django form to a ReactPy component.

    Args:
        form: The form to convert.

    Keyword Args:
        on_success: A callback function that is called when the form is successfully submitted.
        on_error: A callback function that is called when the form submission fails.
        on_receive_data: A callback function that is called before newly submitted form data is rendered.
        on_change: A callback function that is called when a form field is modified by the user.
        auto_save: If `True`, the form will automatically call `save` on successful submission of \
            a `ModelForm`. This has no effect on regular `Form` instances.
        extra_props: Additional properties to add to the `html.form` element.
        extra_transforms: A list of functions that transforms the newly generated VDOM. \
            The functions will be repeatedly called on each VDOM node.
        form_template: The template to use for the form. If `None`, Django's default template is used.
        thread_sensitive: Whether to run event callback functions in thread sensitive mode. \
            This mode only applies to sync functions, and is turned on by default due to Django \
            ORM limitations.
        top_children: Additional elements to add to the top of the form.
        bottom_children: Additional elements to add to the bottom of the form.
        key: A key to uniquely identify this component which is unique amongst a component's \
            immediate siblings.
    """

    return _django_form(
        form=form,
        on_success=on_success,
        on_error=on_error,
        on_receive_data=on_receive_data,
        on_change=on_change,
        auto_save=auto_save,
        extra_props=extra_props or {},
        extra_transforms=extra_transforms or [],
        form_template=form_template,
        thread_sensitive=thread_sensitive,
        top_children=top_children,
        bottom_children=bottom_children,
        key=key,
    )


def pyscript_component(
    *file_paths: str,
    initial: str | VdomDict | ComponentType = "",
    root: str = "root",
) -> ComponentType:
    """
    Args:
        file_paths: File path to your client-side component. If multiple paths are \
            provided, the contents are automatically merged.

    Kwargs:
        initial: The initial HTML that is displayed prior to the PyScript component \
            loads. This can either be a string containing raw HTML, a \
            `#!python reactpy.html` snippet, or a non-interactive component.
        root: The name of the root component function.
    """
    return _pyscript_component(
        *file_paths,
        initial=initial,
        root=root,
    )


@component
def _view_to_component(
    view: Callable | View | str,
    transforms: Sequence[Callable[[VdomDict], Any]],
    strict_parsing: bool,
    request: HttpRequest | None,
    args: Sequence | None,
    kwargs: dict | None,
):
    converted_view, set_converted_view = hooks.use_state(cast(Union[VdomDict, None], None))
    _args: Sequence = args or ()
    _kwargs: dict = kwargs or {}
    if request:
        _request: HttpRequest = request
    else:
        _request = HttpRequest()
        _request.method = "GET"
    resolved_view: Callable = import_module(view) if isinstance(view, str) else view  # type: ignore

    # Render the view render within a hook
    @hooks.use_effect(
        dependencies=[
            json.dumps(vars(_request), default=generate_obj_name),
            json.dumps([_args, _kwargs], default=generate_obj_name),
        ]
    )
    async def _render_view():
        """Render the view in an async hook to avoid blocking the main thread."""
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

    # Return the view if it's been rendered via the `async_render` hook
    return converted_view


@component
def _view_to_iframe(
    view: Callable | View | str,
    extra_props: dict[str, Any] | None,
    args: Sequence,
    kwargs: dict,
):
    from reactpy_django.config import REACTPY_REGISTERED_IFRAME_VIEWS

    if hasattr(view, "view_class"):
        view = view.view_class  # type: ignore
    dotted_path = view if isinstance(view, str) else generate_obj_name(view)
    registered_view = REACTPY_REGISTERED_IFRAME_VIEWS.get(dotted_path)

    if not registered_view:
        msg = (
            f"'{dotted_path}' has not been registered as an iframe! "
            "Are you sure you called `register_iframe` within a Django `AppConfig.ready` method?"
        )
        raise ViewNotRegisteredError(msg)

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
            "loading": "lazy",
        }
        | extra_props
    )


@component
def _django_css(static_path: str):
    return html.style(cached_static_file(static_path))


@component
def _django_js(static_path: str):
    return html.script(cached_static_file(static_path))
