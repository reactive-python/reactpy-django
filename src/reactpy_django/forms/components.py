from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Union, cast
from uuid import uuid4

from channels.db import database_sync_to_async
from django.forms import Form, ModelForm
from reactpy import component, hooks, html, utils
from reactpy.core.events import event
from reactpy.core.types import VdomDict
from reactpy.web import export, module_from_file

from reactpy_django.forms.transforms import (
    convert_html_props_to_reactjs,
    convert_textarea_children_to_prop,
    ensure_input_elements_are_controlled,
    intercept_anchor_links,
    set_value_prop_on_select_element,
)
from reactpy_django.forms.utils import convert_boolean_fields, convert_multiple_choice_fields
from reactpy_django.types import FormEvent

if TYPE_CHECKING:
    from collections.abc import Sequence

DjangoForm = export(
    module_from_file("reactpy-django", file=Path(__file__).parent.parent / "static" / "reactpy_django" / "client.js"),
    ("DjangoForm"),
)


@component
def _django_form(
    form: type[Form | ModelForm],
    extra_props: dict,
    on_success: Callable[[FormEvent], None] | None,
    on_error: Callable[[FormEvent], None] | None,
    on_submit: Callable[[FormEvent], None] | None,
    on_change: Callable[[FormEvent], None] | None,
    auto_save: bool,
    extra_transforms: Sequence[Callable[[VdomDict], Any]],
    form_template: str | None,
    top_children: Sequence,
    bottom_children: Sequence,
):
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
    if "id" in extra_props:
        msg = "The `extra_props` argument cannot contain an `id` key."
        raise ValueError(msg)

    # Try to initialize the form with the provided data
    initialized_form = form(data=submitted_data)
    form_event = FormEvent(form=initialized_form, data=submitted_data or {}, set_data=set_submitted_data)

    # Validate and render the form
    @hooks.use_effect
    async def render_form():
        """Forms must be rendered in an async loop to allow database fields to execute."""
        if submitted_data:
            await database_sync_to_async(initialized_form.full_clean)()
            success = not initialized_form.errors.as_data()
            if success and on_success:
                on_success(form_event)
            if not success and on_error:
                on_error(form_event)
            if success and auto_save and isinstance(initialized_form, ModelForm):
                await database_sync_to_async(initialized_form.save)()
                set_submitted_data(None)

        new_form = await database_sync_to_async(initialized_form.render)(form_template)
        if new_form != rendered_form:
            set_rendered_form(new_form)

    def on_submit_callback(new_data: dict[str, Any]):
        """Callback function provided directly to the client side listener. This is responsible for transmitting
        the submitted form data to the server for processing."""
        convert_multiple_choice_fields(new_data, initialized_form)
        convert_boolean_fields(new_data, initialized_form)

        if on_submit:
            on_submit(FormEvent(form=initialized_form, data=new_data, set_data=set_submitted_data))

        if submitted_data != new_data:
            set_submitted_data(new_data)

    if not rendered_form:
        return None

    return html.form(
        {
            "id": f"reactpy-{uuid}",
            "onSubmit": event(lambda _: None, prevent_default=True),
            "onChange": on_change(form_event) if on_change else lambda _: None,
        }
        | extra_props,
        DjangoForm({"onSubmitCallback": on_submit_callback, "formId": f"reactpy-{uuid}"}),
        *top_children,
        utils.html_to_vdom(
            rendered_form,
            convert_html_props_to_reactjs,
            convert_textarea_children_to_prop,
            set_value_prop_on_select_element,
            ensure_input_elements_are_controlled,
            intercept_anchor_links,
            *extra_transforms,
            strict=False,
        ),
        *bottom_children,
    )
