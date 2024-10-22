from reactpy import component, html, use_location
from reactpy_router import route, use_params, use_search_params
from reactpy_router.types import Route

from reactpy_django.router import django_router


@component
def display_params(string: str):
    location = use_location()
    search_params = use_search_params()
    url_params = use_params()

    return html._(
        html.div({"id": "router-string"}, string),
        html.div(
            {"id": "router-path", "data-path": location.pathname},
            f"path: {location.pathname}",
        ),
        html.div(f"url_params: {url_params}"),
        html.div(f"location.search: {location.search}"),
        html.div(f"search_params: {search_params}"),
    )


def show_route(path: str, *children: Route) -> Route:
    return route(path, display_params(path), *children)


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
    )
