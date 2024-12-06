from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable
from uuid import uuid4

from django.forms import Form
from reactpy import component, hooks, html, utils
from reactpy.core.events import event
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
    form: type[Form],
    extra_props: dict,
    on_success: Callable[[FormEvent], None] | None,
    on_error: Callable[[FormEvent], None] | None,
    on_submit: Callable[[FormEvent], None] | None,
    form_template: str | None,
    top_children: Sequence,
    bottom_children: Sequence,
):
    # TODO: Implement form restoration on page reload. Maybe this involves creating a new setting called
    # `form_restoration_method` that can be set to "URL", "CLIENT_STORAGE", "SERVER_SESSION", or None.
    # Perhaps pre-rendering is robust enough already handle this scenario?
    # Additionally, "URL" mode would limit the user to one form per page.
    # TODO: Test this with django-colorfield, django-ace, django-crispy-forms
    # TODO: Add auto-save option for database-backed forms
    uuid_ref = hooks.use_ref(uuid4().hex.replace("-", ""))
    top_children_count = hooks.use_ref(len(top_children))
    bottom_children_count = hooks.use_ref(len(bottom_children))
    submitted_data, set_submitted_data = hooks.use_state({} or None)
    uuid = uuid_ref.current

    # Don't allow the count of top and bottom children to change
    if len(top_children) != top_children_count.current or len(bottom_children) != bottom_children_count.current:
        msg = "Dynamically changing the number of top or bottom children is not allowed."
        raise ValueError(msg)

    # Try to initialize the form with the provided data
    try:
        initialized_form = form(data=submitted_data)
    except Exception as e:
        if not isinstance(form, type(Form)):
            msg = (
                "The provided form must be an uninitialized Django Form. "
                "Do NOT initialize your form by calling it (ex. `MyForm()`)."
            )
            raise TypeError(msg) from e
        raise

    # Run the form validation, if data was provided
    if submitted_data:
        initialized_form.full_clean()
        success = not initialized_form.errors.as_data()
        form_event = FormEvent(form=initialized_form, data=submitted_data or {})
        if success and on_success:
            on_success(form_event)
        if not success and on_error:
            on_error(form_event)

    def on_submit_callback(new_data: dict[str, Any]):
        """Callback function provided directly to the client side listener. This is responsible for transmitting
        the submitted form data to the server for processing."""
        convert_multiple_choice_fields(new_data, initialized_form)
        convert_boolean_fields(new_data, initialized_form)

        # TODO: The `use_state`` hook really should be de-duplicating this by itself. Needs upstream fix.
        if submitted_data != new_data:
            if on_submit:
                on_submit(FormEvent(form=initialized_form, data=new_data))
            set_submitted_data(new_data)

    return html.form(
        {"id": f"reactpy-{uuid}", "onSubmit": event(lambda _: None, prevent_default=True)} | extra_props,
        DjangoForm({"onSubmitCallback": on_submit_callback, "formId": f"reactpy-{uuid}"}),
        *top_children,
        utils.html_to_vdom(
            initialized_form.render(form_template),
            convert_html_props_to_reactjs,
            convert_textarea_children_to_prop,
            set_value_prop_on_select_element,
            ensure_input_elements_are_controlled(),
            intercept_anchor_links,
            strict=False,
        ),
        *bottom_children,
    )
