from reactpy import component, html
from reactpy_django.router import django_router
from reactpy_router import route


@component
def my_component():
    return django_router(
        route("/router/", html.div("Example 1")),
        route("/router/any/<value>/", html.div("Example 2")),
        route("/router/integer/<int:value>/", html.div("Example 3")),
        route("/router/path/<path:value>/", html.div("Example 4")),
        route("/router/slug/<slug:value>/", html.div("Example 5")),
        route("/router/string/<str:value>/", html.div("Example 6")),
        route("/router/uuid/<uuid:value>/", html.div("Example 7")),
        route("/router/two_values/<int:value>/<str:value2>/", html.div("Example 9")),
    )
