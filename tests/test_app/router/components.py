from uuid import uuid4

from reactpy import component, html, use_location, use_state
from reactpy_router import link, route, use_params, use_search_params
from reactpy_router.types import Route

from reactpy_django.router import django_router


@component
def display_params(string: str):
    location = use_location()
    search_params = use_search_params()
    url_params = use_params()

    return html(
        html.div({"id": "router-string"}, string),
        html.div(
            {"id": "router-path", "data-path": location.path},
            f"path: {location.path}",
        ),
        html.div(f"url_params: {url_params}"),
        html.div(f"location.query_string: {location.query_string}"),
        html.div(f"search_params: {search_params}"),
    )


def show_route(path: str, *children: Route) -> Route:
    return route(path, display_params(path), *children)


@component
def next_page():
    url_params = use_params()
    state, set_state = use_state(uuid4)
    page = url_params.get("page", 0)
    next_page = page + 1
    return html.fragment(
        display_params("/router/next/<int:page>/"),
        html.div({"id": "router-uuid", "data-uuid": state.hex}, f"UUID: {state.hex}"),
        html.button(
            link({"to": f"/router/next/{next_page}/"}, "Next Page"),
        ),
    )


@component
def main():
    return django_router(
        show_route("/router/", show_route("subroute/")),
        show_route("/router/unspecified/<value>/"),
        show_route("/router/integer/<int:value>/"),
        show_route("/router/path/<path:value>/"),
        show_route("/router/slug/<slug:value>/"),
        show_route("/router/string/<str:value>/"),
        show_route("/router/uuid/<uuid:value>/"),
        show_route("/router/any/<any:name>"),
        show_route("/router/two/<int:value>/<str:value2>/"),
        route("/router/next/<int:page>/", next_page()),
    )
