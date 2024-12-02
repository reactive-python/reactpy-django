from reactpy import component, html

from example.components import child_component


@component
def root():
    return html.div("This text is from the root component.", child_component())
