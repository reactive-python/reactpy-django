from typing import Dict

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS
from idom.core.proto import ComponentConstructor


IDOM_REGISTERED_COMPONENTS: Dict[str, ComponentConstructor] = {}

IDOM_WEBSOCKET_URL = getattr(settings, "IDOM_WEBSOCKET_URL", "idom/")
IDOM_WS_MAX_RECONNECT_DELAY = getattr(settings, "IDOM_WS_MAX_RECONNECT_DELAY", 604800)

# Determine if using Django caching or LRU cache
_CACHES = getattr(settings, "CACHES", {})
if _CACHES:
    if "idom_web_modules" in getattr(settings, "CACHES", {}):
        IDOM_WEB_MODULE_CACHE = "idom_web_modules"
    else:
        IDOM_WEB_MODULE_CACHE = DEFAULT_CACHE_ALIAS
else:
    IDOM_WEB_MODULE_CACHE = None


# LRU cache size, if not using Django caching
IDOM_WEB_MODULE_LRU_CACHE_SIZE = getattr(
    settings, "IDOM_WEB_MODULE_LRU_CACHE_SIZE", None
)
