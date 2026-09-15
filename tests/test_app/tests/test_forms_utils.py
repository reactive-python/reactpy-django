"""Unit tests for :func:`reactpy_django.forms.utils.convert_form_fields`."""

from __future__ import annotations

from unittest.mock import MagicMock

from django.forms import (
    BooleanField,
    CharField,
    Form,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    NullBooleanField,
)
from django.test import TestCase

from reactpy_django.forms.utils import convert_form_fields


class ConvertFormFieldsTests(TestCase):
    """Test that ``convert_form_fields`` normalises form data to the format
    Django expects."""

    def _make_form(self, **fields):
        """Helper: return an initialised form whose fields dict can be
        inspected without running full validation."""
        form = MagicMock(spec=Form)
        form.fields = fields
        return form

    # ── MultipleChoiceField / ModelMultipleChoiceField ────────────────

    def test_multi_choice_field_none_becomes_empty_list(self):
        """When a MultipleChoiceField has no selection (value is None),
        convert it to ``[]`` so Django's validator receives the type it expects."""
        form = self._make_form(
            choice=MultipleChoiceField(choices=[("1", "A"), ("2", "B")]),
        )
        data = {}
        convert_form_fields(data, form)
        assert data == {"choice": []}

    def test_multi_choice_field_single_value_becomes_list(self):
        """When a MultipleChoiceField receives a single value (from the
        client-side code before the duplicate-key fix), wrap it in a list."""
        form = self._make_form(
            choice=MultipleChoiceField(choices=[("1", "A"), ("2", "B")]),
        )
        data = {"choice": "1"}
        convert_form_fields(data, form)
        assert data == {"choice": ["1"]}

    def test_multi_choice_field_already_list_stays_list(self):
        """When a MultipleChoiceField already has a list value (the normal
        case after the client-side FormData fix), leave it unchanged."""
        form = self._make_form(
            choice=MultipleChoiceField(choices=[("1", "A"), ("2", "B")]),
        )
        data = {"choice": ["1", "2"]}
        convert_form_fields(data, form)
        assert data == {"choice": ["1", "2"]}

    def test_model_multi_choice_field_none_becomes_empty_list(self):
        """ModelMultipleChoiceField with no selection: same None → [] rule."""
        form = self._make_form(
            model_choice=ModelMultipleChoiceField(queryset=MagicMock()),
        )
        data = {}
        convert_form_fields(data, form)
        assert data == {"model_choice": []}

    def test_model_multi_choice_field_single_value_becomes_list(self):
        """ModelMultipleChoiceField with a single value: wrap in list."""
        form = self._make_form(
            model_choice=ModelMultipleChoiceField(queryset=MagicMock()),
        )
        data = {"model_choice": "1"}
        convert_form_fields(data, form)
        assert data == {"model_choice": ["1"]}

    def test_model_multi_choice_field_already_list_stays_list(self):
        """ModelMultipleChoiceField with list: unchanged."""
        form = self._make_form(
            model_choice=ModelMultipleChoiceField(queryset=MagicMock()),
        )
        data = {"model_choice": ["1", "2"]}
        convert_form_fields(data, form)
        assert data == {"model_choice": ["1", "2"]}

    # ── BooleanField ──────────────────────────────────────────────────

    def test_boolean_field_checked_becomes_true(self):
        """A present key (browser sends it when checked) → True."""
        form = self._make_form(flag=BooleanField())
        data = {"flag": "on"}
        convert_form_fields(data, form)
        assert data == {"flag": True}

    def test_boolean_field_unchecked_becomes_false(self):
        """An absent key (browser omits it when unchecked) → False."""
        form = self._make_form(flag=BooleanField())
        data = {}
        convert_form_fields(data, form)
        assert data == {"flag": False}

    def test_null_boolean_field_not_touched(self):
        """NullBooleanField is *not* converted — it has three states and
        should be handled by Django's own logic."""
        form = self._make_form(flag=NullBooleanField())
        data = {"flag": "unknown"}
        convert_form_fields(data, form)
        assert data == {"flag": "unknown"}

    # ── Other field types (pass-through) ──────────────────────────────

    def test_other_fields_passed_through(self):
        """Fields that aren't special-cased (e.g. CharField) are left
        exactly as they arrived."""
        form = self._make_form(chars=CharField())
        data = {"chars": "hello"}
        convert_form_fields(data, form)
        assert data == {"chars": "hello"}
