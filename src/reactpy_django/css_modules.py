import re
from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict

import tinycss2
from tinycss2.ast import QualifiedRule

file_text = open("example.css", "r").read()


SquareBracketValues = TypedDict(
    "SquareBracketValues",
    {"key": str, "operator": str | None, "value": str | list | None},
)


@dataclass
class CssRule:
    """Represents a CSS selector.
    Examples of the parser's targets are shown below as docstrings."""

    tag: str | Literal["*"] | None = None
    """div, span"""
    id: str | None = None
    """#id1, #id2"""
    classes: list[str] = field(default_factory=list)
    """.class1, .class2"""
    attributes: list[SquareBracketValues] = field(default_factory=list)
    """[key=value], [key^=value]"""
    styles: dict[str, Any] = field(default_factory=dict)
    """color: red;"""
    psuedo_functions: list[str] = field(default_factory=list)
    """:not(), :nth-child()"""
    psuedo_elements: list[str] = field(default_factory=list)
    """:hover, :focus"""
    psuedo_classes: list[str] = field(default_factory=list)
    """::before, ::after"""

    next: list["CssRule"] = field(default_factory=list)
    """#current-selector #next-selector"""
    next_operator: str = " "
    """>, +, ~"""


@dataclass
class CssToPython:
    """Performs a best-effort conversion of a CSS file into a list of Python dictionaries."""

    content: str

    def convert(self) -> list[CssRule]:
        """Converts the CSS file into a list of CSS rule dictionaries."""
        self.parsed: list[QualifiedRule] = tinycss2.parse_stylesheet(
            self.content,
            skip_comments=True,
            skip_whitespace=True,
        )
        self.selectors: list[CssRule] = []

        for style in self.parsed:
            if style.type != "qualified-rule":
                continue
            selector = CssRule()

            # Determine what CSS rules are defined in the selector
            computed_rules = tinycss2.parse_declaration_list(
                style.content, skip_comments=True, skip_whitespace=True
            )
            for rule in computed_rules:
                selector.styles[rule.name] = self._parse_rule_value(rule.value)

            # Parse HTML tag name from the selector
            if style.prelude[0].type == "ident":
                selector.tag = style.prelude[0].value
            elif style.prelude[0].type == "literal" and style.prelude[0].value == "*":
                selector.tag = "*"

            # Parse all other attributes from the selector
            print(style.prelude)
            for count, token in enumerate(style.prelude):
                if token.type == "hash":
                    selector.id = selector.id or token.value
                elif token.type == "literal" and token.value == ".":
                    selector.classes.append(style.prelude[count + 1].value)
                elif token.type == "[] block" and len(token.content) == 1:
                    selector.attributes.append(
                        {
                            "key": token.content[0].value,
                            "operator": None,
                            "value": None,
                        }
                    )
                elif token.type == "[] block" and len(token.content) == 3:
                    selector.attributes.append(
                        {
                            "key": token.content[0].value,
                            "operator": token.content[1].value,
                            "value": token.content[2].value,
                        }
                    )
                # TODO: Once we reach an operator or whitespace, recursively parse the children then break
                # TODO: Split comma operators into separate selectors

            self.selectors.append(selector)

        return self.selectors

    @staticmethod
    def _flatten_whitespace(string: str) -> str:
        return re.sub(r"\s+", " ", string).strip()

    def _parse_rule_value(self, rule):
        """Parses a single TinyCSS rule and returns Python a data type."""
        rule = tinycss2.serialize(rule)
        rule = self._flatten_whitespace(rule)
        if rule.isnumeric():
            return int(rule)
        else:
            return rule


styles = CssToPython(file_text).convert()
for style in styles:
    print(style)
