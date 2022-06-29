from dataclasses import dataclass
from typing import Callable, Tuple, Union

from django.views.generic import View
from idom.core.component import Component


@dataclass
class ViewComponentIframe:
    middleware: Union[list[Union[Callable, str]], None]
    view: Union[View, Callable]
    component: Union[Component, object]
    args: Tuple
    kwargs: dict
