from __future__ import annotations

from itertools import cycle
from typing import TYPE_CHECKING, Callable

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS
from django.db import DEFAULT_DB_ALIAS
from reactpy.config import REACTPY_ASYNC_RENDERING as _REACTPY_ASYNC_RENDERING
from reactpy.config import REACTPY_DEBUG_MODE as _REACTPY_DEBUG_MODE

from reactpy_django.utils import import_dotted_path

if TYPE_CHECKING:
    from django.views import View
    from reactpy.core.types import ComponentConstructor

    from reactpy_django.types import (
        AsyncPostprocessor,
        SyncPostprocessor,
    )

# Non-configurable values
REACTPY_REGISTERED_COMPONENTS: dict[str, ComponentConstructor] = {}
REACTPY_FAILED_COMPONENTS: set[str] = set()
REACTPY_REGISTERED_IFRAME_VIEWS: dict[str, Callable | View] = {}

# Configurable through Django settings.py
DJANGO_DEBUG = settings.DEBUG  # Snapshot of Django's DEBUG setting
_REACTPY_DEBUG_MODE.set_current(settings.DEBUG)
_REACTPY_ASYNC_RENDERING.set_current(getattr(settings, "REACTPY_ASYNC_RENDERING", _REACTPY_ASYNC_RENDERING.current))
REACTPY_URL_PREFIX: str = getattr(
    settings,
    "REACTPY_URL_PREFIX",
    "reactpy/",
).strip("/")
REACTPY_SESSION_MAX_AGE: int = getattr(
    settings,
    "REACTPY_SESSION_MAX_AGE",
    259200,  # Default to 3 days
)
REACTPY_AUTH_TOKEN_MAX_AGE: int = getattr(
    settings,
    "REACTPY_AUTH_TOKEN_MAX_AGE",
    30,  # Default to 30 seconds
)
REACTPY_CACHE: str = getattr(
    settings,
    "REACTPY_CACHE",
    DEFAULT_CACHE_ALIAS,
)
REACTPY_DATABASE: str = getattr(
    settings,
    "REACTPY_DATABASE",
    DEFAULT_DB_ALIAS,
)
_default_query_postprocessor = getattr(
    settings,
    "REACTPY_DEFAULT_QUERY_POSTPROCESSOR",
    "UNSET",
)
REACTPY_DEFAULT_QUERY_POSTPROCESSOR: AsyncPostprocessor | SyncPostprocessor | None
if _default_query_postprocessor is None:
    REACTPY_DEFAULT_QUERY_POSTPROCESSOR = None
else:
    REACTPY_DEFAULT_QUERY_POSTPROCESSOR = import_dotted_path(
        "reactpy_django.utils.django_query_postprocessor"
        if (_default_query_postprocessor == "UNSET" or not isinstance(_default_query_postprocessor, str))
        else _default_query_postprocessor
    )
REACTPY_AUTH_BACKEND: str | None = getattr(
    settings,
    "REACTPY_AUTH_BACKEND",
    None,
)
REACTPY_BACKHAUL_THREAD: bool = getattr(
    settings,
    "REACTPY_BACKHAUL_THREAD",
    False,
)
_default_hosts: list[str] | None = getattr(
    settings,
    "REACTPY_DEFAULT_HOSTS",
    None,
)
REACTPY_DEFAULT_HOSTS: cycle[str] | None = (
    cycle([host.strip("/") for host in _default_hosts if isinstance(host, str)]) if _default_hosts else None
)
REACTPY_RECONNECT_INTERVAL: int = getattr(
    settings,
    "REACTPY_RECONNECT_INTERVAL",
    750,  # Default to 0.75 seconds
)
REACTPY_RECONNECT_MAX_INTERVAL: int = getattr(
    settings,
    "REACTPY_RECONNECT_MAX_INTERVAL",
    60000,  # Default to 60 seconds
)
REACTPY_RECONNECT_MAX_RETRIES: int = getattr(
    settings,
    "REACTPY_RECONNECT_MAX_RETRIES",
    150,
)
REACTPY_RECONNECT_BACKOFF_MULTIPLIER: float | int = getattr(
    settings,
    "REACTPY_RECONNECT_BACKOFF_MULTIPLIER",
    1.25,  # Default to 25% backoff per connection attempt
)
REACTPY_PRERENDER: bool = getattr(
    settings,
    "REACTPY_PRERENDER",
    False,
)
REACTPY_AUTO_RELOGIN: bool = getattr(
    settings,
    "REACTPY_AUTO_RELOGIN",
    False,
)
REACTPY_CLEAN_INTERVAL: int | None = getattr(
    settings,
    "REACTPY_CLEAN_INTERVAL",
    604800,  # Default to 7 days
)
REACTPY_CLEAN_SESSIONS: bool = getattr(
    settings,
    "REACTPY_CLEAN_SESSIONS",
    True,
)
REACTPY_CLEAN_AUTH_TOKENS: bool = getattr(
    settings,
    "REACTPY_CLEAN_AUTH_TOKENS",
    True,
)
REACTPY_CLEAN_USER_DATA: bool = getattr(
    settings,
    "REACTPY_CLEAN_USER_DATA",
    True,
)
REACTPY_DEFAULT_FORM_TEMPLATE: str | None = getattr(
    settings,
    "REACTPY_DEFAULT_FORM_TEMPLATE",
    None,
)
