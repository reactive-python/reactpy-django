from typing import Dict

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS
from idom.core.proto import ComponentConstructor


IDOM_REGISTERED_COMPONENTS: Dict[str, ComponentConstructor] = {}

IDOM_BASE_URL = getattr(settings, "IDOM_BASE_URL", "_idom/")
IDOM_WEBSOCKET_URL = IDOM_BASE_URL + "websocket/"
IDOM_WEB_MODULES_URL = IDOM_BASE_URL + "web_module/"
IDOM_WS_MAX_RECONNECT_DELAY = getattr(settings, "IDOM_WS_MAX_RECONNECT_DELAY", 604800)

_CACHES = getattr(settings, "CACHES", {})
if _CACHES:
    if "idom_web_modules" in getattr(settings, "CACHES", {}):
        IDOM_WEB_MODULE_CACHE = "idom_web_modules"
    else:
        IDOM_WEB_MODULE_CACHE = DEFAULT_CACHE_ALIAS
else:
    IDOM_WEB_MODULE_CACHE = None


# the LRU cache size for the route serving IDOM_WEB_MODULES_DIR files
IDOM_WEB_MODULE_LRU_CACHE_SIZE = getattr(
    settings, "IDOM_WEB_MODULE_LRU_CACHE_SIZE", None
)
