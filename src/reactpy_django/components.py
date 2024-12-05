from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Type, Union, cast
from urllib.parse import urlencode
from uuid import uuid4

from django.contrib.staticfiles.finders import find
from django.core.cache import caches
from django.forms import BooleanField, ChoiceField, Form, MultipleChoiceField
from django.http import HttpRequest
from django.urls import reverse
from reactpy import component, hooks, html, utils
from reactpy.types import ComponentType, Key, VdomDict
from reactpy.web import export, module_from_file

from reactpy_django.exceptions import ViewNotRegisteredError
from reactpy_django.html import pyscript
from reactpy_django.transforms import (
    convert_option_props,
    convert_textarea_children_to_prop,
    ensure_controlled_inputs,
    standardize_prop_names,
)
from reactpy_django.utils import (
    generate_obj_name,
    import_module,
    render_pyscript_template,
    render_view,
    vdom_or_component_to_string,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.views import View

DjangoForm = export(
    module_from_file("reactpy-django", file=Path(__file__).parent / "static" / "reactpy_django" / "client.js"),
    ("DjangoForm"),
)


def view_to_component(
    view: Callable | View | str,
    transforms: Sequence[Callable[[VdomDict], Any]] = (),
    strict_parsing: bool = True,
) -> Any:
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
    ):
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


def view_to_iframe(view: Callable | View | str, extra_props: dict[str, Any] | None = None):
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
        return _view_to_iframe(view=view, extra_props=extra_props, args=args, kwargs=kwargs, key=key)

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


def django_form(
    form: Type[Form],
    *,
    top_children: Sequence = (),
    bottom_children: Sequence = (),
    auto_submit: bool = False,
    auto_submit_wait: int = 3,
    key: Key | None = None,
):
    return _django_form(
        form=form,
        top_children=top_children,
        bottom_children=bottom_children,
        auto_submit=auto_submit,
        auto_submit_wait=auto_submit_wait,
        key=key,
    )


def pyscript_component(
    *file_paths: str,
    initial: str | VdomDict | ComponentType = "",
    root: str = "root",
):
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
    """The actual component. Used to prevent pollution of acceptable kwargs keys."""
    converted_view, set_converted_view = hooks.use_state(cast(Union[VdomDict, None], None))
    _args: Sequence = args or ()
    _kwargs: dict = kwargs or {}
    if request:
        _request: HttpRequest = request
    else:
        _request = HttpRequest()
        _request.method = "GET"
    resolved_view: Callable = import_module(view) if isinstance(view, str) else view

    # Render the view render within a hook
    @hooks.use_effect(
        dependencies=[
            json.dumps(vars(_request), default=generate_obj_name),
            json.dumps([_args, _kwargs], default=generate_obj_name),
        ]
    )
    async def async_render():
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
) -> VdomDict:
    """The actual component. Used to prevent pollution of acceptable kwargs keys."""
    from reactpy_django.config import REACTPY_REGISTERED_IFRAME_VIEWS

    if hasattr(view, "view_class"):
        view = view.view_class
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
    return html.style(_cached_static_contents(static_path))


@component
def _django_js(static_path: str):
    return html.script(_cached_static_contents(static_path))


@component
def _django_form(
    form: Type[Form], top_children: Sequence, bottom_children: Sequence, auto_submit: bool, auto_submit_wait: int
):
    # TODO: Implement form restoration on page reload. Probably want to create a new setting called
    # form_restoration_method that can be set to "URL", "CLIENT_STORAGE", "SERVER_SESSION", or None.
    # Or maybe just recommend pre-rendering to have the browser handle it.
    # Be clear that URL mode will limit you to one form per page.
    # TODO: Test this with django-bootstrap forms and see how errors behave
    # TODO: Test this with django-colorfield and django-ace
    # TODO: Add pre-submit and post-submit hooks
    # TODO: Add auto-save option for database-backed forms
    uuid_ref = hooks.use_ref(uuid4().hex.replace("-", ""))
    top_children_count = hooks.use_ref(len(top_children))
    bottom_children_count = hooks.use_ref(len(bottom_children))
    submitted_data, set_submitted_data = hooks.use_state({} or None)

    uuid = uuid_ref.current

    # Don't allow the count of top and bottom children to change
    if len(top_children) != top_children_count.current or len(bottom_children) != bottom_children_count.current:
        raise ValueError("Dynamically changing the number of top or bottom children is not allowed.")

    # Try to initialize the form with the provided data
    try:
        initialized_form = form(data=submitted_data)
    except Exception as e:
        if not isinstance(form, type(Form)):
            raise ValueError(
                "The provided form must be an uninitialized Django Form. "
                "Do NOT initialize your form by calling it (ex. `MyForm()`)."
            ) from e
        raise e

    # Run the form validation, if data was provided
    if submitted_data:
        initialized_form.full_clean()

    def on_submit_callback(new_data: dict[str, Any]):
        choice_field_map = {
            field_name: {choice_value: choice_key for choice_key, choice_value in field.choices}
            for field_name, field in initialized_form.fields.items()
            if isinstance(field, ChoiceField)
        }
        multi_choice_fields = {
            field_name
            for field_name, field in initialized_form.fields.items()
            if isinstance(field, MultipleChoiceField)
        }
        boolean_fields = {
            field_name for field_name, field in initialized_form.fields.items() if isinstance(field, BooleanField)
        }

        # Choice fields submit their values as text, but Django choice keys are not always equal to their values.
        # Due to this, we need to convert the text into keys that Django would be happy with
        for choice_field_name, choice_map in choice_field_map.items():
            if choice_field_name in new_data:
                submitted_value = new_data[choice_field_name]
                if isinstance(submitted_value, list):
                    new_data[choice_field_name] = [
                        choice_map.get(submitted_value_item, submitted_value_item)
                        for submitted_value_item in submitted_value
                    ]
                elif choice_field_name in multi_choice_fields:
                    new_data[choice_field_name] = [choice_map.get(submitted_value, submitted_value)]
                else:
                    new_data[choice_field_name] = choice_map.get(submitted_value, submitted_value)

        # Convert boolean field text into actual booleans
        for boolean_field_name in boolean_fields:
            new_data[boolean_field_name] = boolean_field_name in new_data

        # TODO: ReactPy's use_state hook really should be de-duplicating this by itself. Needs upstream fix.
        if submitted_data != new_data:
            set_submitted_data(new_data)

    async def on_change(event): ...

    rendered_form = utils.html_to_vdom(
        initialized_form.render(),
        standardize_prop_names,
        convert_textarea_children_to_prop,
        convert_option_props,
        ensure_controlled_inputs(on_change),
        strict=False,
    )

    return html.form(
        {"id": f"reactpy-{uuid}"},
        DjangoForm({"onSubmitCallback": on_submit_callback, "formId": f"reactpy-{uuid}"}),
        *top_children,
        html.div({"key": uuid4().hex}, rendered_form),
        *bottom_children,
    )


def _cached_static_contents(static_path: str) -> str:
    from reactpy_django.config import REACTPY_CACHE

    # Try to find the file within Django's static files
    abs_path = find(static_path)
    if not abs_path:
        msg = f"Could not find static file {static_path} within Django's static files."
        raise FileNotFoundError(msg)
    if isinstance(abs_path, (list, tuple)):
        abs_path = abs_path[0]

    # Fetch the file from cache, if available
    last_modified_time = os.stat(abs_path).st_mtime
    cache_key = f"reactpy_django:static_contents:{static_path}"
    file_contents: str | None = caches[REACTPY_CACHE].get(cache_key, version=int(last_modified_time))
    if file_contents is None:
        with open(abs_path, encoding="utf-8") as static_file:
            file_contents = static_file.read()
        caches[REACTPY_CACHE].delete(cache_key)
        caches[REACTPY_CACHE].set(cache_key, file_contents, timeout=None, version=int(last_modified_time))

    return file_contents


@component
def _pyscript_component(
    *file_paths: str,
    initial: str | VdomDict | ComponentType = "",
    root: str = "root",
):
    rendered, set_rendered = hooks.use_state(False)
    uuid_ref = hooks.use_ref(uuid4().hex.replace("-", ""))
    uuid = uuid_ref.current
    initial = vdom_or_component_to_string(initial, uuid=uuid)
    executor = render_pyscript_template(file_paths, uuid, root)

    if not rendered:
        # FIXME: This is needed to properly re-render PyScript during a WebSocket
        # disconnection / reconnection. There may be a better way to do this in the future.
        set_rendered(True)
        return None

    return html._(
        html.div(
            {"id": f"pyscript-{uuid}", "className": "pyscript", "data-uuid": uuid},
            initial,
        ),
        pyscript({"async": ""}, executor),
    )
