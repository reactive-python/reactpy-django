from reactpy import component, html


@component
def child_component():
    return html.div("This is a child component from a different file.")
