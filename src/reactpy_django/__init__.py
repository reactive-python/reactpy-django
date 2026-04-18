import filecmp
import shutil
from pathlib import Path

import reactpy

from reactpy_django import (
    components,
    decorators,
    hooks,
    router,
    types,
    utils,
)
from reactpy_django.websocket.paths import REACTPY_WEBSOCKET_ROUTE

__version__ = "5.2.1"
__all__ = [
    "REACTPY_WEBSOCKET_ROUTE",
    "components",
    "decorators",
    "hooks",
    "router",
    "types",
    "utils",
]

# Copy ReactPy core's wheel to ReactPy-Django's static directory if
# any file within the SOURCE_DIR is not within the DEST_DIR (or is not identical)
SOURCE_DIR = Path(reactpy.__file__).parent / "static/wheels"
DEST_DIR = Path(__file__).parent.parent / "reactpy_django/static/reactpy_django/wheels"
if not DEST_DIR.exists() or any(
    not (DEST_DIR / file.name).exists() or not filecmp.cmp(file, DEST_DIR / file.name)
    for file in SOURCE_DIR.glob("reactpy-*-py3-none-any.whl")
):
    shutil.copytree(SOURCE_DIR, DEST_DIR, dirs_exist_ok=True)
