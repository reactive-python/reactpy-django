from __future__ import annotations

from django.urls.converters import get_converters

from typing import TYPE_CHECKING

from reactpy_router.resolvers import ReactPyResolver

from reactpy_django.router.converters import CONVERTERS

if TYPE_CHECKING:
    from reactpy_router.types import Route


class DjangoResolver(ReactPyResolver):
    """A simple route resolver that uses regex to match paths"""
    param_pattern=r"<(?P<type>\w+:)?(?P<name>\w+)>"
    converters = CONVERTERS
