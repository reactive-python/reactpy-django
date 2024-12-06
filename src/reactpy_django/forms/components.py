from __future__ import annotations

from pathlib import Path
from pprint import pprint
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from django.forms import Form
from django.utils import timezone
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

if TYPE_CHECKING:
    from collections.abc import Sequence

DjangoForm = export(
    module_from_file("reactpy-django", file=Path(__file__).parent.parent / "static" / "reactpy_django" / "client.js"),
    ("DjangoForm"),
)


@component
def _django_form(form: type[Form], top_children: Sequence, bottom_children: Sequence):
    # TODO: Implement form restoration on page reload. Probably want to create a new setting called
    # form_restoration_method that can be set to "URL", "CLIENT_STORAGE", "SERVER_SESSION", or None.
    # Or maybe just recommend pre-rendering to have the browser handle it.
    # Be clear that URL mode will limit you to one form per page.
    # TODO: Test this with django-bootstrap, django-colorfield, django-ace, django-crispy-forms
    # TODO: Add pre-submit and post-submit hooks
    # TODO: Add auto-save option for database-backed forms
    uuid_ref = hooks.use_ref(uuid4().hex.replace("-", ""))
    top_children_count = hooks.use_ref(len(top_children))
    bottom_children_count = hooks.use_ref(len(bottom_children))
    submitted_data, set_submitted_data = hooks.use_state({} or None)
    last_changed = hooks.use_ref(timezone.now())

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

    @event(prevent_default=True)
    def on_submit(_event):
        """The server was notified that a form was submitted. Note that actual submission behavior is handled by `on_submit_callback`."""
        last_changed.set_current(timezone.now())

    def on_submit_callback(new_data: dict[str, Any]):
        convert_multiple_choice_fields(new_data, initialized_form)
        convert_boolean_fields(new_data, initialized_form)

        # TODO: ReactPy's use_state hook really should be de-duplicating this by itself. Needs upstream fix.
        if submitted_data != new_data:
            set_submitted_data(new_data)

    def on_change(_event):
        last_changed.set_current(timezone.now())

    rendered_form = utils.html_to_vdom(
        initialized_form.render(),
        convert_html_props_to_reactjs,
        convert_textarea_children_to_prop,
        set_value_prop_on_select_element,
        ensure_input_elements_are_controlled(on_change),
        intercept_anchor_links,
        strict=False,
    )

    return html.form(
        {"id": f"reactpy-{uuid}", "onSubmit": on_submit},
        DjangoForm({"onSubmitCallback": on_submit_callback, "formId": f"reactpy-{uuid}"}),
        *top_children,
        rendered_form,
        *bottom_children,
    )
