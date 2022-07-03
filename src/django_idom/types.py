from dataclasses import dataclass
from typing import Awaitable, Callable, Optional


@dataclass
class IdomWebsocket:
    scope: dict
    close: Callable[[Optional[int]], Awaitable[None]]
    disconnect: Callable[[int], Awaitable[None]]
    view_id: str


@dataclass
class AuthLevel:
    authenticated: str = "authenticated"
    """Anyone logged in with a registered account."""

    active: str = "active"
    """Any account that has not been deactivated."""

    staff: str = "staff"
    """Any account that is a staff member."""

    superuser: str = "superuser"
    """Any account that is a superuser."""
