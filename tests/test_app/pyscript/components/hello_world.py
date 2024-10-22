from reactpy import component, html


@component
def root():
    return html.div({"id": "hello-world"}, "hello world")
