from __future__ import annotations

from itertools import cycle

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS
from django.db import DEFAULT_DB_ALIAS
from reactpy.config import REACTPY_DEBUG_MODE
from reactpy.core.types import ComponentConstructor

from reactpy_django.types import (
    AsyncPostprocessor,
    SyncPostprocessor,
    ViewComponentIframe,
)
from reactpy_django.utils import import_dotted_path

# Non-configurable values
REACTPY_DEBUG_MODE.set_current(getattr(settings, "DEBUG"))
REACTPY_REGISTERED_COMPONENTS: dict[str, ComponentConstructor] = {}
REACTPY_FAILED_COMPONENTS: set[str] = set()
REACTPY_VIEW_COMPONENT_IFRAMES: dict[str, ViewComponentIframe] = {}


# Remove in a future release
REACTPY_WEBSOCKET_URL = getattr(
    settings,
    "REACTPY_WEBSOCKET_URL",
    "reactpy/",
)

# Configurable through Django settings.py
REACTPY_URL_PREFIX: str = getattr(
    settings,
    "REACTPY_URL_PREFIX",
    REACTPY_WEBSOCKET_URL,
).strip("/")
REACTPY_SESSION_MAX_AGE: int = getattr(
    settings,
    "REACTPY_SESSION_MAX_AGE",
    259200,  # Default to 3 days
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
        if (
            _default_query_postprocessor == "UNSET"
            or not isinstance(_default_query_postprocessor, str)
        )
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
    cycle([host.strip("/") for host in _default_hosts if isinstance(host, str)])
    if _default_hosts
    else None
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
