from __future__ import annotations

import logging
import sys

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


_logger = logging.getLogger(__name__)


# Not user configurable settings
REACTPY_DEBUG_MODE.set_current(getattr(settings, "DEBUG"))
REACTPY_REGISTERED_COMPONENTS: dict[str, ComponentConstructor] = {}
REACTPY_VIEW_COMPONENT_IFRAMES: dict[str, ViewComponentIframe] = {}


# Configurable through Django settings.py
REACTPY_WEBSOCKET_URL = getattr(
    settings,
    "REACTPY_WEBSOCKET_URL",
    "reactpy/",
)
REACTPY_RECONNECT_MAX = getattr(
    settings,
    "REACTPY_RECONNECT_MAX",
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
REACTPY_DEFAULT_QUERY_POSTPROCESSOR: AsyncPostprocessor | SyncPostprocessor | None = (
    import_dotted_path(
        getattr(
            settings,
            "REACTPY_DEFAULT_QUERY_POSTPROCESSOR",
            "reactpy_django.utils.django_query_postprocessor",
        )
    )
)
REACTPY_AUTH_BACKEND: str | None = getattr(
    settings,
    "REACTPY_AUTH_BACKEND",
    None,
)
REACTPY_BACKHAUL_THREAD: bool = getattr(
    settings,
    "REACTPY_BACKHAUL_THREAD",
    True,
)

# Settings checks (separate from Django checks)
if (
    sys.platform == "linux"
    and sys.argv
    and sys.argv[0].endswith("daphne")
    and REACTPY_BACKHAUL_THREAD
):
    _logger.warning(
        "ReactPy is running on Linux with Daphne, but REACTPY_BACKHAUL_THREAD is set "
        "to True. This configuration is known to be unstable. Either set "
        "REACTPY_BACKHAUL_THREAD to False, or run ReactPy with a different ASGI server."
    )
