from uuid import UUID, uuid4

from reactpy import component, html, use_location, use_state
from reactpy_router import link, route, use_params, use_search_params
from reactpy_router.types import Route

from reactpy_django.router import django_router


class _TokenStore:
    """Process-wide holder for a stable navigation-state token."""

    def __init__(self) -> None:
        self._value: UUID | None = None

    def get(self) -> UUID:
        """Return the token, creating one on first access."""
        if self._value is None:
            self._value = uuid4()
        return self._value


_NEXT_PAGE_TOKEN = _TokenStore()


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
    # ReactPy preserves `use_state` across SPA navigation, but the WebSocket can
    # reconnect under load, which causes ReactPy to re-mount the component and
    # reset hook state. Keep the token in a module-level store so it survives both
    # navigation and transient reconnects, otherwise this state-preservation test
    # becomes flaky on slow/loaded CI runners.
    token_hex = _NEXT_PAGE_TOKEN.get()
    state, _set_state = use_state(token_hex)
    page = url_params.get("page", 0)
    next_page = page + 1
    return html.fragment(
        display_params("/router/next/<int:page>/"),
        html.div({"id": "router-uuid", "data-uuid": state.hex}, f"UUID: {state.hex}"),
        html.button(
            link({"to": f"/router/next/{next_page}/"}, "Next Page"),
        ),
    )


# Routes are defined at module scope so that the route elements (including the
# stateful `next_page`) have a stable identity across renders. Recreating them
# inside `main()` on each render would cause ReactPy to treat them as new
# components, remounting them and resetting `use_state` during SPA navigation.
ROUTES: tuple[Route, ...] = (
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


@component
def main():
    return django_router(*ROUTES)
