from reactpy import component, html


@component
def online():
    return html.div(
        "This is the ONLINE component. "
        "Try shutting down your webserver and checking if the offline component appears."
    )


@component
def offline():
    return html.div({"id": "offline-success"}, "Offline")
