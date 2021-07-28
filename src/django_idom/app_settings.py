from pathlib import Path

from django.conf import settings


APP_DIR = Path(__file__).parent

TEMPLATE_FILE_PATHS = {
    file.stem: str(file.absolute())
    for file in (APP_DIR / "templates" / "idom").iterdir()
}

IDOM_WEBSOCKET_URL = getattr(settings, "IDOM_WEBSOCKET_URL", "_idom/")
if not IDOM_WEBSOCKET_URL.endswith("/"):
    IDOM_WEBSOCKET_URL += "/"
