import contextlib

import nest_asyncio

from reactpy_django import checks, components, decorators, hooks, types, utils
from reactpy_django.websocket.paths import REACTPY_WEBSOCKET_PATH

__version__ = "3.3.1"
__all__ = [
    "REACTPY_WEBSOCKET_PATH",
    "hooks",
    "components",
    "decorators",
    "types",
    "utils",
    "checks",
]
# Built-in asyncio event loops can create `assert f is self._write_fut` exceptions
# while we are using our backhaul thread with Uvicorn, so we use this patch to fix this.
# This also resolves jittery rendering behaviors within Daphne. Can be demonstrated
# using our "Renders Per Second" test page.
with contextlib.suppress(ValueError):
    nest_asyncio.apply()
