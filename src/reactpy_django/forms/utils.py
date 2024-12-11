from __future__ import annotations

from typing import Any

from django.forms import BooleanField, Form, ModelForm, ModelMultipleChoiceField, MultipleChoiceField, NullBooleanField


def convert_form_fields(data: dict[str, Any], initialized_form: Form | ModelForm) -> None:
    for field_name, field in initialized_form.fields.items():
        value = data.get(field_name)

        if isinstance(field, (MultipleChoiceField, ModelMultipleChoiceField)) and value is not None:
            data[field_name] = value if isinstance(value, list) else [value]

        elif isinstance(field, BooleanField) and not isinstance(field, NullBooleanField):
            data[field_name] = field_name in data
