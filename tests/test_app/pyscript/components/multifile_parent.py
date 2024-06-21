from typing import TYPE_CHECKING

from reactpy import component, html

if TYPE_CHECKING:
    from .multifile_child import child


@component
def root():
    return html.div({"id": "multifile-parent"}, "Multifile root", child())
