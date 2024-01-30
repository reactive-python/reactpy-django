from reactpy import component, html, use_location
from reactpy_django.router import django_router
from reactpy_router import route, use_params, use_query


@component
def display_params(string: str):
    location = use_location()
    query = use_query()
    params = use_params()

    return html._(
        html.div({"id": "router-string"}, string),
        html.div(f"Params: {params}"),
        html.div(
            {"id": "router-path", "data-path": location.pathname},
            f"Path Name: {location.pathname}",
        ),
        html.div(f"Query String: {location.search}"),
        html.div(f"Query: {query}"),
    )


@component
def main():
    return django_router(
        route("/router/", display_params("Path 1")),
        route("/router/any/<value>/", display_params("Path 2")),
        route("/router/integer/<int:value>/", display_params("Path 3")),
        route("/router/path/<path:value>/", display_params("Path 4")),
        route("/router/slug/<slug:value>/", display_params("Path 5")),
        route("/router/string/<str:value>/", display_params("Path 6")),
        route("/router/uuid/<uuid:value>/", display_params("Path 7")),
        route("/router/", None, route("abc/", display_params("Path 8"))),
        route(
            "/router/two/<int:value>/<str:value2>/",
            display_params("Path 9"),
        ),
        route(
            "/router/star/",
            None,
            route("one/", display_params("Path 11")),
            route("*", display_params("Path 12")),
        ),
    )
