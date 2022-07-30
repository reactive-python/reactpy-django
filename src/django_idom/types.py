from dataclasses import dataclass
from typing import Awaitable, Callable, Optional


@dataclass
class IdomWebsocket:
    scope: dict
    close: Callable[[Optional[int]], Awaitable[None]]
    disconnect: Callable[[int], Awaitable[None]]
    view_id: str
