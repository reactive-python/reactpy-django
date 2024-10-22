from __future__ import annotations

from reactpy_router.resolvers import StarletteResolver
from reactpy_router.types import ConversionInfo, Route

from reactpy_django.router.converters import CONVERTERS


class DjangoResolver(StarletteResolver):
    """A simple route resolver that uses regex to match paths"""

    def __init__(
        self,
        route: Route,
        param_pattern=r"<(?P<type>\w+:)?(?P<name>\w+)>",
        converters: dict[str, ConversionInfo] | None = None,
    ) -> None:
        super().__init__(
            route=route,
            param_pattern=param_pattern,
            converters=converters or CONVERTERS,
        )
