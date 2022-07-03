from dataclasses import dataclass
from typing import Awaitable, Callable, Optional


@dataclass
class IdomWebsocket:
    scope: dict
    close: Callable[[Optional[int]], Awaitable[None]]
    disconnect: Callable[[int], Awaitable[None]]
    view_id: str


@dataclass
class AuthAttribute:
    anonymous: str = "is_anonymous"
    """Individuals that are not logged in."""

    authenticated: str = "is_authenticated"
    """Anyone logged in with a registered account."""

    active: str = "is_active"
    """A registered account that has not been deactivated."""

    staff: str = "is_staff"
    """Any account that is a staff member."""

    superuser: str = "is_superuser"
    """Any account that is a superuser."""
