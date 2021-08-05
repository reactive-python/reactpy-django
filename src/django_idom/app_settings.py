from pathlib import Path

from django.conf import settings


IDOM_IGNORE_INSTALLED_APPS = set(getattr(settings, "IDOM_IGNORE_INSTALLED_APPS", []))

IDOM_BASE_URL = getattr(settings, "IDOM_BASE_URL", "_idom/")
IDOM_WEBSOCKET_URL = IDOM_BASE_URL + "websocket/"
IDOM_WEB_MODULES_URL = IDOM_BASE_URL + "web_module/"
