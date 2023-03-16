from __future__ import annotations

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS
from django.db import DEFAULT_DB_ALIAS
from idom.config import IDOM_DEBUG_MODE
from idom.core.types import ComponentConstructor

from django_idom.types import AsyncPostprocessor, SyncPostprocessor, ViewComponentIframe
from django_idom.utils import import_dotted_path


# Not user configurable settings
IDOM_DEBUG_MODE.set_current(getattr(settings, "DEBUG"))
IDOM_REGISTERED_COMPONENTS: dict[str, ComponentConstructor] = {}
IDOM_VIEW_COMPONENT_IFRAMES: dict[str, ViewComponentIframe] = {}


# Configurable through Django settings.py
IDOM_WEBSOCKET_URL = getattr(
    settings,
    "IDOM_WEBSOCKET_URL",
    "idom/",
)
IDOM_RECONNECT_MAX = getattr(
    settings,
    "IDOM_RECONNECT_MAX",
    259200,  # Default to 3 days
)
IDOM_CACHE: str = getattr(
    settings,
    "IDOM_CACHE",
    DEFAULT_CACHE_ALIAS,
)
IDOM_DATABASE: str = getattr(
    settings,
    "IDOM_DATABASE",
    DEFAULT_DB_ALIAS,
)
IDOM_DEFAULT_QUERY_POSTPROCESSOR: AsyncPostprocessor | SyncPostprocessor | None = (
    import_dotted_path(
        getattr(
            settings,
            "IDOM_DEFAULT_QUERY_POSTPROCESSOR",
            "django_idom.utils.django_query_postprocessor",
        )
    )
)
