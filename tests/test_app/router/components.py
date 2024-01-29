from reactpy import component, html, use_location
from reactpy_django.router import django_router
from reactpy_router import route, use_params, use_query


@component
def display_params(*args):
    params = use_params()
    return html._(
        html.div(f"Params: {params}"),
        *args,
    )


@component
def main():
    location = use_location()
    query = use_query()

    route_info = html._(
        html.div(
            {"id": "router-path", "data-path": location.pathname},
            f"Path Name: {location.pathname}",
        ),
        html.div(f"Query String: {location.search}"),
        html.div(f"Query: {query}"),
    )

    return django_router(
        route("/router/", html.div("Path 1", route_info)),
        route("/router/any/<value>/", display_params("Path 2", route_info)),
        route("/router/integer/<int:value>/", display_params("Path 3", route_info)),
        route("/router/path/<path:value>/", display_params("Path 4", route_info)),
        route("/router/slug/<slug:value>/", display_params("Path 5", route_info)),
        route("/router/string/<str:value>/", display_params("Path 6", route_info)),
        route("/router/uuid/<uuid:value>/", display_params("Path 7", route_info)),
        route("/router/", None, route("abc/", display_params("Path 8", route_info))),
        route(
            "/router/two/<int:value>/<str:value2>/",
            display_params("Path 9", route_info),
        ),
        route(
            "/router/multi-tier-route/",
            display_params("Path 10", route_info),
            route("one/", display_params("Path 11", route_info)),
            route("two/", display_params("Path 12", route_info)),
            route("*", display_params("Path 13", route_info)),
        ),
        route(
            "/router/star-in-middle/*/",
            display_params("Path 14", route_info),
            route("one/", display_params("Path 15", route_info)),
            route("two/", display_params("Path 16", route_info)),
        ),
    )
