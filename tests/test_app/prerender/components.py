from time import sleep

from reactpy import component, html

import reactpy_django

SLEEP_TIME = 0.25


@component
def prerender_string():
    scope = reactpy_django.hooks.use_scope()

    if scope.get("type") != "http":
        sleep(SLEEP_TIME)

    return "prerender_string: Fully Rendered" if scope.get("type") == "websocket" else "prerender_string: Prerendered"


@component
def prerender_vdom():
    scope = reactpy_django.hooks.use_scope()

    if scope.get("type") == "http":
        return html.div("prerender_vdom: Prerendered")

    return html.div("prerender_vdom: Fully Rendered")


@component
def prerender_component():
    scope = reactpy_django.hooks.use_scope()

    @component
    def inner(value):
        return html.div(value)

    if scope.get("type") == "http":
        return inner("prerender_component: Prerendered")

    return inner("prerender_component: Fully Rendered")


@component
def use_user():
    user = reactpy_django.hooks.use_user()
    scope = reactpy_django.hooks.use_scope()
    success = bool(user)

    if scope.get("type") == "http":
        return html.div({"id": "use-user-http", "data-success": success}, f"use_user: {user} (HTTP)")

    return html.div({"id": "use-user-ws", "data-success": success}, f"use_user: {user} (WebSocket)")


@component
def use_root_id():
    scope = reactpy_django.hooks.use_scope()
    root_id = reactpy_django.hooks.use_root_id()

    if scope.get("type") == "http":
        return html.div(
            {"id": "use-root-id-http", "data-value": root_id},
            f"use_root_id: {root_id} (HTTP)",
        )

    return html.div(
        {"id": "use-root-id-ws", "data-value": root_id},
        f"use_root_id: {root_id} (WebSocket)",
    )
