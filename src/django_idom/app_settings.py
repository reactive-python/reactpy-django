from pathlib import Path

from django.conf import settings


APP_DIR = Path(__file__).parent

TEMPLATE_FILE_PATHS = {
    file.stem: str(file.absolute())
    for file in (APP_DIR / "templates" / "idom").iterdir()
}

IDOM_BASE_URL = getattr(settings, "IDOM_BASE_URL", "_idom/")
IDOM_WEBSOCKET_URL = IDOM_BASE_URL + "websocket/"
IDOM_WEB_MODULES_URL = IDOM_BASE_URL + "web_module/"
