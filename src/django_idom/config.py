from typing import Dict

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from idom.core.proto import ComponentConstructor


IDOM_REGISTERED_COMPONENTS: Dict[str, ComponentConstructor] = {}

IDOM_BASE_URL = getattr(settings, "IDOM_BASE_URL", "_idom/")
IDOM_WEBSOCKET_URL = IDOM_BASE_URL + "websocket/"
IDOM_WEB_MODULES_URL = IDOM_BASE_URL + "web_module/"
IDOM_WS_MAX_RECONNECT_DELAY = getattr(settings, "IDOM_WS_MAX_RECONNECT_DELAY", 604800)

if "idom" in getattr(settings, "CACHES", {}):
    IDOM_CACHE = caches["idom"]
else:
    IDOM_CACHE = caches[DEFAULT_CACHE_ALIAS]
