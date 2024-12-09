from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Union, cast
from uuid import uuid4

from channels.db import database_sync_to_async
from django.forms import Form, ModelForm
from reactpy import component, hooks, html, utils
from reactpy.core.events import event
from reactpy.web import export, module_from_file

from reactpy_django.forms.transforms import (
    convert_html_props_to_reactjs,
    convert_textarea_children_to_prop,
    intercept_anchor_links,
    set_value_prop_on_select_element,
    transform_value_prop_on_input_element,
)
from reactpy_django.forms.utils import convert_boolean_fields, convert_multiple_choice_fields
from reactpy_django.types import AsyncFormEvent, FormEventData, SyncFormEvent
from reactpy_django.utils import ensure_async

if TYPE_CHECKING:
    from collections.abc import Sequence

    from reactpy.core.types import VdomDict

DjangoForm = export(
    module_from_file("reactpy-django", file=Path(__file__).parent.parent / "static" / "reactpy_django" / "client.js"),
    ("DjangoForm"),
)


@component
def _django_form(
    form: type[Form | ModelForm],
    on_success: AsyncFormEvent | SyncFormEvent | None,
    on_error: AsyncFormEvent | SyncFormEvent | None,
    on_receive_data: AsyncFormEvent | SyncFormEvent | None,
    on_change: AsyncFormEvent | SyncFormEvent | None,
    auto_save: bool,
    extra_props: dict,
    extra_transforms: Sequence[Callable[[VdomDict], Any]],
    form_template: str | None,
    top_children: Sequence,
    bottom_children: Sequence,
):
    from reactpy_django import config

    uuid_ref = hooks.use_ref(uuid4().hex.replace("-", ""))
    top_children_count = hooks.use_ref(len(top_children))
    bottom_children_count = hooks.use_ref(len(bottom_children))
    submitted_data, set_submitted_data = hooks.use_state({} or None)
    rendered_form, set_rendered_form = hooks.use_state(cast(Union[str, None], None))
    uuid = uuid_ref.current

    # Check the provided arguments
    if len(top_children) != top_children_count.current or len(bottom_children) != bottom_children_count.current:
        msg = "Dynamically changing the number of top or bottom children is not allowed."
        raise ValueError(msg)
    if not isinstance(form, (type(Form), type(ModelForm))):
        msg = (
            "The provided form must be an uninitialized Django Form. "
            "Do NOT initialize your form by calling it (ex. `MyForm()`)."
        )
        raise TypeError(msg)

    # Try to initialize the form with the provided data
    initialized_form = form(data=submitted_data)
    form_event = FormEventData(
        form=initialized_form, submitted_data=submitted_data or {}, set_submitted_data=set_submitted_data
    )

    # Validate and render the form
    @hooks.use_effect
    async def render_form():
        """Forms must be rendered in an async loop to allow database fields to execute."""
        if submitted_data:
            await database_sync_to_async(initialized_form.full_clean)()
            success = not initialized_form.errors.as_data()
            if success and on_success:
                await ensure_async(on_success)(form_event)
            if not success and on_error:
                await ensure_async(on_error)(form_event)
            if success and auto_save and isinstance(initialized_form, ModelForm):
                await database_sync_to_async(initialized_form.save)()
                set_submitted_data(None)

        new_form = await database_sync_to_async(initialized_form.render)(
            form_template or config.REACTPY_DEFAULT_FORM_TEMPLATE
        )
        if new_form != rendered_form:
            set_rendered_form(new_form)

    async def on_submit_callback(new_data: dict[str, Any]):
        """Callback function provided directly to the client side listener. This is responsible for transmitting
        the submitted form data to the server for processing."""
        convert_multiple_choice_fields(new_data, initialized_form)
        convert_boolean_fields(new_data, initialized_form)

        if on_receive_data:
            new_form_event = FormEventData(
                form=initialized_form, submitted_data=new_data, set_submitted_data=set_submitted_data
            )
            await ensure_async(on_receive_data)(new_form_event)

        if submitted_data != new_data:
            set_submitted_data(new_data)

    async def _on_change(_event):
        """Event that exist solely to allow the user to detect form changes."""
        if on_change:
            await ensure_async(on_change)(form_event)

    if not rendered_form:
        return None

    return html.form(
        extra_props
        | {
            "id": f"reactpy-{uuid}",
            # Intercept the form submission to prevent the browser from navigating
            "onSubmit": event(lambda _: None, prevent_default=True),
            "onChange": _on_change,
        },
        DjangoForm({"onSubmitCallback": on_submit_callback, "formId": f"reactpy-{uuid}"}),
        *top_children,
        utils.html_to_vdom(
            rendered_form,
            convert_html_props_to_reactjs,
            convert_textarea_children_to_prop,
            set_value_prop_on_select_element,
            transform_value_prop_on_input_element,
            intercept_anchor_links,
            *extra_transforms,
            strict=False,
        ),
        *bottom_children,
    )
