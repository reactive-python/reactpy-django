from dataclasses import dataclass
from typing import Callable, Tuple

from django.views.generic import View
from idom.core.component import Component


@dataclass
class ViewToComponentIframe:
    middleware: list[Callable | str]
    view: View | Callable
    component: Component | object
    args: Tuple
    kwargs: dict
