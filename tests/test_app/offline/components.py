from reactpy import component, html


@component
def online():
    return html.div(
        {"id": "online"},
        "This is the ONLINE component. "
        "Shut down your webserver and check if the offline component appears.",
    )


@component
def offline():
    return html.div({"id": "offline"}, "Offline")
