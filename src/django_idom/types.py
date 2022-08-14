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
    middleware: Union[List[Union[Callable, str]], None]
    view: Union[View, Callable]
    component: Union[Component, object]
    args: Tuple
    kwargs: dict
