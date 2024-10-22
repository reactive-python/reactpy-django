from reactpy import component, html


@component
def child():
    return html.div({"id": "multifile-child"}, "Multifile child")
