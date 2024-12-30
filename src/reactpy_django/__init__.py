import contextlib

import nest_asyncio

from reactpy_django import (
    components,
    decorators,
    hooks,
    html,
    router,
    types,
    utils,
)
from reactpy_django.websocket.paths import REACTPY_WEBSOCKET_ROUTE

__version__ = "5.2.0"
__all__ = [
    "REACTPY_WEBSOCKET_ROUTE",
    "components",
    "decorators",
    "hooks",
    "html",
    "router",
    "types",
    "utils",
]

# Fixes bugs with REACTPY_BACKHAUL_THREAD + built-in asyncio event loops.
# Previously, Uvicorn could generate `assert f is self._write_fut` exceptions, and Daphne
# had jittery rendering behaviors. Demonstrated using our "Renders Per Second" test page.
with contextlib.suppress(ValueError):
    nest_asyncio.apply()
