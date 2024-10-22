from typing import TYPE_CHECKING

from reactpy import component, html

if TYPE_CHECKING:
    from .child import child_component


@component
def root():
    return html.div("This text is from the root component.", child_component())
