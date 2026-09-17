"""Unit tests for the form VDOM transforms in :mod:`reactpy_django.forms.transforms`.

``set_value_prop_on_select_element`` is coupled to ReactPy's built-in
``RequiredTransforms.select_element_to_reactjs`` transform: that transform
strips the ``selected`` attribute from each ``<option>`` and records the chosen
value(s) as ``defaultValue`` on the parent ``<select>`` element. These tests
exercise the reactpy-django transform both against hand-built trees and, where
relevant, against the output of the built-in ReactPy transform so the coupling
is covered by a regression test.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from reactpy_django.forms.transforms import set_value_prop_on_select_element


class SetValuePropOnSelectElementTests(SimpleTestCase):
    """Test selection restoration on ``<select>`` elements for Preact."""

    def _option(self, value: str, selected: bool = False) -> dict:
        attr = {"value": value}
        if selected:
            attr["selected"] = True
        return {"tagName": "option", "attributes": attr, "children": [value]}

    def _select(self, options: list[dict], multiple: bool = False) -> dict:
        attrs = {}
        if multiple:
            attrs["multiple"] = True
        return {"tagName": "select", "attributes": attrs, "children": options}

    def test_single_select_restores_selected_on_matching_option(self) -> None:
        """A single-choice select's chosen option gets ``selected`` re-applied."""
        # Simulate post-builtin-transform state: `defaultValue` on the select,
        # `value` on each option, `selected` already stripped off the options.
        tree = self._select([
            self._option("1"),
            self._option("2"),
            self._option("3"),
        ])
        tree["attributes"]["defaultValue"] = "2"

        set_value_prop_on_select_element(tree)

        option_attrs = [c["attributes"] for c in tree["children"]]
        assert option_attrs[0].get("selected") is None
        assert option_attrs[1].get("selected") is True
        assert option_attrs[2].get("selected") is None

    def test_multi_select_restores_all_selected_options(self) -> None:
        """A multi-select restores ``selected`` on every matching option."""
        tree = self._select(
            [
                self._option("1"),
                self._option("2"),
                self._option("3"),
            ],
            multiple=True,
        )
        tree["attributes"]["defaultValue"] = ["1", "3"]

        set_value_prop_on_select_element(tree)

        option_attrs = [c["attributes"] for c in tree["children"]]
        assert option_attrs[0].get("selected") is True
        assert option_attrs[1].get("selected") is None
        assert option_attrs[2].get("selected") is True

    def test_empty_selection_leaves_options_unselected(self) -> None:
        """When there is no selection, no option gets ``selected`` re-applied."""
        tree = self._select([self._option("1"), self._option("2")])

        set_value_prop_on_select_element(tree)

        option_attrs = [c["attributes"] for c in tree["children"]]
        assert option_attrs[0].get("selected") is None
        assert option_attrs[1].get("selected") is None

    def test_string_default_value_wrapped_for_multi_select(self) -> None:
        """A single ``defaultValue`` string is handled for a multi-select."""
        tree = self._select(
            [self._option("1"), self._option("2")],
            multiple=True,
        )
        tree["attributes"]["defaultValue"] = "2"

        set_value_prop_on_select_element(tree)

        option_attrs = [c["attributes"] for c in tree["children"]]
        assert option_attrs[0].get("selected") is None
        assert option_attrs[1].get("selected") is True

    def test_default_value_coerces_multiple_to_bool(self) -> None:
        """The ``multiple`` attribute is coerced to a boolean on the select."""
        tree = self._select([self._option("1")])
        tree["attributes"]["multiple"] = "true"

        set_value_prop_on_select_element(tree)

        assert tree["attributes"]["multiple"] is True

    def test_non_select_nodes_are_left_unchanged(self) -> None:
        """The transform is a no-op for nodes that are not ``<select>``."""
        tree = {"tagName": "div", "attributes": {}, "children": []}

        result = set_value_prop_on_select_element(tree)

        assert result is tree
        assert tree["attributes"] == {}
