from dataclasses import dataclass
from typing import Awaitable, Callable, List, Optional, Tuple, Union

from django.views.generic import View
from idom.core.component import Component


@dataclass
class IdomWebsocket:
    scope: dict
    close: Callable[[Optional[int]], Awaitable[None]]
    disconnect: Callable[[int], Awaitable[None]]
    view_id: str


@dataclass
class ViewComponentIframe:
    view: Union[View, Callable]
    args: Tuple
    kwargs: dict
