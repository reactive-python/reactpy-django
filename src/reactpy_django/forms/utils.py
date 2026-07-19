from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.forms import (
    BooleanField,
    Form,
    ModelForm,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    NullBooleanField,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from reactpy import Ref


def convert_form_fields(data: dict[str, Any], initialized_form: Form | ModelForm) -> None:
    """Convert submitted form data into the format expected by Django fields.

    This handles the mismatch between browser FormData serialisation and
    Django's field-level expectations:

    * ``MultipleChoiceField`` / ``ModelMultipleChoiceField`` – always stored as a
      list.  When no option is selected the key may be absent or ``None``; we
      normalise to an empty list.
    * ``BooleanField`` (non-null) – represented by the browser as "key present
      = checked".  We convert to ``True``/``False``.
    * All other fields (including ``MultiValueField``, ``SplitDateTimeField``)
      are passed through unchanged.  Their sub-widgets already produce unique
      ``_0``, ``_1``, … keys so no re-shaping is needed.
    """
    for field_name, field in initialized_form.fields.items():
        value = data.get(field_name)

        if isinstance(field, (MultipleChoiceField, ModelMultipleChoiceField)):
            if value is None:
                data[field_name] = []
            elif not isinstance(value, list):
                data[field_name] = [value]

        elif isinstance(field, BooleanField) and not isinstance(field, NullBooleanField):
            data[field_name] = field_name in data


def validate_form_args(
    top_children: Sequence,
    top_children_count: Ref[int],
    bottom_children: Sequence,
    bottom_children_count: Ref[int],
    form: type[Form | ModelForm],
) -> None:
    if len(top_children) != top_children_count.current or len(bottom_children) != bottom_children_count.current:
        msg = "Dynamically changing the number of top or bottom children is not allowed."
        raise ValueError(msg)
    if not isinstance(form, (type(Form), type(ModelForm))):
        msg = (
            "The provided form must be an uninitialized Django Form. "
            "Do NOT initialize your form by calling it (ex. `MyForm()`)."
        )
        raise TypeError(msg)
