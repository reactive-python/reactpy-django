from __future__ import annotations

from reactpy_router.resolvers import ReactPyResolver

from reactpy_django.router.converters import CONVERTERS


class DjangoResolver(ReactPyResolver):
    param_pattern = r"<(?P<type>\w+:)?(?P<name>\w+)>"
    converters = CONVERTERS
