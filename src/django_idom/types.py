from dataclasses import dataclass
from typing import Callable, Tuple

from django.views.generic import View
from idom.core.component import Component


@dataclass
class ViewComponentIframe:
    middleware: list[Callable | str] | None
    view: View | Callable
    component: Component | object
    args: Tuple
    kwargs: dict
