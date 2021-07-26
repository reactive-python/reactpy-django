from django.conf import settings


IDOM_WEBSOCKET_URL = getattr(settings, "IDOM_WEBSOCKET_URL", "_idom/")
if not IDOM_WEBSOCKET_URL.endswith("/"):
    IDOM_WEBSOCKET_URL += "/"
