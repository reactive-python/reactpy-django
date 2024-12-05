from typing import Any

from django.forms import BooleanField, ChoiceField, Form, MultipleChoiceField


def convert_choice_fields(data: dict[str, Any], initialized_form: Form) -> None:
    choice_field_map = {
        field_name: {choice_value: choice_key for choice_key, choice_value in field.choices}
        for field_name, field in initialized_form.fields.items()
        if isinstance(field, ChoiceField)
    }
    multi_choice_fields = {
        field_name for field_name, field in initialized_form.fields.items() if isinstance(field, MultipleChoiceField)
    }

    # Choice fields submit their values as text, but Django choice keys are not always equal to their values.
    # Due to this, we need to convert the text into keys that Django would be happy with
    for choice_field_name, choice_map in choice_field_map.items():
        if choice_field_name in data:
            submitted_value = data[choice_field_name]
            if isinstance(submitted_value, list):
                data[choice_field_name] = [
                    choice_map.get(submitted_value_item, submitted_value_item)
                    for submitted_value_item in submitted_value
                ]
            elif choice_field_name in multi_choice_fields:
                data[choice_field_name] = [choice_map.get(submitted_value, submitted_value)]
            else:
                data[choice_field_name] = choice_map.get(submitted_value, submitted_value)


def convert_boolean_fields(data: dict[str, Any], initialized_form: Form) -> None:
    boolean_fields = {
        field_name for field_name, field in initialized_form.fields.items() if isinstance(field, BooleanField)
    }

    # Convert boolean field text into actual booleans
    for boolean_field_name in boolean_fields:
        data[boolean_field_name] = boolean_field_name in data
