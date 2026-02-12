from __future__ import annotations

from django.urls.converters import get_converters

from typing import TYPE_CHECKING

from reactpy_router.resolvers import ReactPyResolver

if TYPE_CHECKING:
    from reactpy_router.types import Route


class DjangoResolver(ReactPyResolver):
    """A simple route resolver that uses regex to match paths"""
    converters = ReactPyResolver.converters | {
        name: {"regex": converter.regex, "func": converter.to_python} 
        for name, converter in get_converters().items()
    }
