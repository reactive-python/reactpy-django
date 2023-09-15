from time import sleep

import reactpy_django
from reactpy import component, html


@component
def preload_string():
    scope = reactpy_django.hooks.use_scope()

    sleep(0.5)
    return (
        "preload_string: Fully Rendered"
        if scope.get("type") == "websocket"
        else "preload_string: Preloaded"
    )


@component
def preload_vdom():
    scope = reactpy_django.hooks.use_scope()

    if scope.get("type") == "http":
        return html.div("preload_vdom: Preloaded")

    return html.div("preload_vdom: Fully Rendered")


@component
def preload_component():
    scope = reactpy_django.hooks.use_scope()

    @component
    def inner(value):
        return html.div(value)

    if scope.get("type") == "http":
        return inner("preload_component: Preloaded")

    return inner("preload_component: Fully Rendered")
