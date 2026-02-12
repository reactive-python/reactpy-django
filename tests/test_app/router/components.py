from reactpy import component, html, use_location
from reactpy_router import route, use_params, use_search_params
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
def main():
    return django_router(
        show_route("/router/", show_route("subroute/")),
        show_route("/router/unspecified/{value}/"),
        show_route("/router/integer/{value:int}/"),
        show_route("/router/path/{value:path}/"),
        show_route("/router/slug/{value:slug}/"),
        show_route("/router/string/{value:str}/"),
        show_route("/router/uuid/{value:uuid}/"),
        show_route("/router/any/{name:any}"),
        show_route("/router/two/{value:int}/{value2:str}/"),
    )
