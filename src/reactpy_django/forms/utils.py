from __future__ import annotations

from typing import Any

from django.forms import BooleanField, Form, ModelForm, ModelMultipleChoiceField, MultipleChoiceField, NullBooleanField


def convert_multiple_choice_fields(data: dict[str, Any], initialized_form: Form | ModelForm) -> None:
    multi_choice_fields = {
        field_name
        for field_name, field in initialized_form.fields.items()
        if isinstance(field, (MultipleChoiceField, ModelMultipleChoiceField))
    }

    # Convert multiple choice field text into a list of values
    for choice_field_name in multi_choice_fields:
        if not isinstance(data.get(choice_field_name), list):
            data[choice_field_name] = [data[choice_field_name]]


def convert_boolean_fields(data: dict[str, Any], initialized_form: Form | ModelForm) -> None:
    boolean_fields = {
        field_name
        for field_name, field in initialized_form.fields.items()
        if isinstance(field, BooleanField) and not isinstance(field, NullBooleanField)
    }

    # Convert boolean field text into actual booleans
    for boolean_field_name in boolean_fields:
        data[boolean_field_name] = boolean_field_name in data
