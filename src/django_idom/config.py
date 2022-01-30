from typing import Dict

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from idom.core.proto import ComponentConstructor


IDOM_REGISTERED_COMPONENTS: Dict[str, ComponentConstructor] = {}

IDOM_WEBSOCKET_URL = getattr(settings, "IDOM_WEBSOCKET_URL", "idom/")
IDOM_WS_MAX_RECONNECT_TIMEOUT = getattr(
    settings, "IDOM_WS_MAX_RECONNECT_TIMEOUT", 604800
)

# Determine if using Django caching or LRU cache
if "idom" in getattr(settings, "CACHES", {}):
    IDOM_CACHE = caches["idom"]
else:
    IDOM_CACHE = caches[DEFAULT_CACHE_ALIAS]
