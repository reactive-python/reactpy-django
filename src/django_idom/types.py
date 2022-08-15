from dataclasses import dataclass
from typing import Awaitable, Callable, Iterable, Optional, Union

from django.views.generic import View


@dataclass
class IdomWebsocket:
    scope: dict
    close: Callable[[Optional[int]], Awaitable[None]]
    disconnect: Callable[[int], Awaitable[None]]
    view_id: str


@dataclass
class ViewComponentIframe:
    view: Union[View, Callable]
    args: Iterable
    kwargs: dict
