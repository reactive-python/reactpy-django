import contextlib

import nest_asyncio

from reactpy_django import checks, components, decorators, hooks, router, types, utils
from reactpy_django.websocket.paths import (
    REACTPY_WEBSOCKET_PATH,
    REACTPY_WEBSOCKET_ROUTE,
)

__version__ = "3.6.0"
__all__ = [
    "REACTPY_WEBSOCKET_PATH",
    "REACTPY_WEBSOCKET_ROUTE",
    "hooks",
    "components",
    "decorators",
    "types",
    "utils",
    "checks",
    "router",
]

# Fixes bugs with REACTPY_BACKHAUL_THREAD + built-in asyncio event loops.
# Previously, Uvicorn could generate `assert f is self._write_fut` exceptions, and Daphne
# had jittery rendering behaviors. Demonstrated using our "Renders Per Second" test page.
with contextlib.suppress(ValueError):
    nest_asyncio.apply()
