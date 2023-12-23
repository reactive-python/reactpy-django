from __future__ import annotations

import re
from typing import Any

from reactpy_router.core import create_router
from reactpy_router.simple import ConverterMapping
from reactpy_router.types import Route

from reactpy_django.router.converters import CONVERTERS

PARAM_PATTERN = re.compile(r"<(?P<type>\w+:)?(?P<name>\w+)>")


# TODO: Make reactpy_router's SimpleResolver generic enough to where we don't have to define our own
class DjangoResolver:
    """A simple route resolver that uses regex to match paths"""

    def __init__(self, route: Route) -> None:
        self.element = route.element
        self.pattern, self.converters = parse_path(route.path)
        self.key = self.pattern.pattern

    def resolve(self, path: str) -> tuple[Any, dict[str, Any]] | None:
        match = self.pattern.match(path)
        if match:
            return (
                self.element,
                {k: self.converters[k](v) for k, v in match.groupdict().items()},
            )
        return None


# TODO: Make reactpy_router's parse_path generic enough to where we don't have to define our own
def parse_path(path: str) -> tuple[re.Pattern[str], ConverterMapping]:
    pattern = "^"
    last_match_end = 0
    converters: ConverterMapping = {}
    for match in PARAM_PATTERN.finditer(path):
        param_name = match.group("name")
        param_type = (match.group("type") or "str").strip(":")
        try:
            param_conv = CONVERTERS[param_type]
        except KeyError as e:
            raise ValueError(
                f"Unknown conversion type {param_type!r} in {path!r}"
            ) from e
        pattern += re.escape(path[last_match_end : match.start()])
        pattern += f"(?P<{param_name}>{param_conv['regex']})"
        converters[param_name] = param_conv["func"]
        last_match_end = match.end()
    pattern += f"{re.escape(path[last_match_end:])}$"
    return re.compile(pattern), converters


django_router = create_router(DjangoResolver)
