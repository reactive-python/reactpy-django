import os
from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import SuspiciousOperation
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseNotFound
from reactpy.config import REACTPY_WEB_MODULES_DIR

from reactpy_django.utils import FileAsyncIterator, ensure_async, render_view


def web_modules_file(request: HttpRequest, file: str) -> FileResponse:
    """Gets JavaScript required for ReactPy modules at runtime."""

    web_modules_dir = REACTPY_WEB_MODULES_DIR.current
    path = os.path.abspath(web_modules_dir.joinpath(file))

    # Prevent attempts to walk outside of the web modules dir
    if str(web_modules_dir) != os.path.commonpath((path, web_modules_dir)):
        msg = "Attempt to access a directory outside of REACTPY_WEB_MODULES_DIR."
        raise SuspiciousOperation(msg)

    return FileResponse(FileAsyncIterator(path), content_type="text/javascript")


async def view_to_iframe(request: HttpRequest, dotted_path: str) -> HttpResponse:
    """Returns a view that was registered by reactpy_django.components.view_to_iframe."""
    from reactpy_django.config import REACTPY_REGISTERED_IFRAME_VIEWS

    # Get the view
    registered_view = REACTPY_REGISTERED_IFRAME_VIEWS.get(dotted_path)
    if not registered_view:
        return HttpResponseNotFound()

    # Get args and kwargs from the request
    query = request.META.get("QUERY_STRING", "")
    kwargs = {k: v if len(v) > 1 else v[0] for k, v in parse_qs(query).items()}
    args = kwargs.pop("_args", [])

    # Render the view
    response = await render_view(registered_view, request, args, kwargs)

    # Ensure page can be rendered as an iframe
    response["X-Frame-Options"] = "SAMEORIGIN"
    return response


async def switch_user_session(request: HttpRequest, uuid: str) -> HttpResponse:
    """Switches the client's active session.

    Django's authentication design requires HTTP cookies to persist login via cookies.

    This is problematic since ReactPy is rendered via WebSockets, and browsers do not
    allow active WebSocket connections to modify HTTP cookies, which necessitates this
    view to exist."""
    from reactpy_django.models import AuthSession

    # TODO: Maybe just relogin the user instead of switching sessions?

    # Find out what session we're switching to
    auth_session = await AuthSession.objects.aget(uuid=uuid)

    # Validate the session
    if auth_session.expired:
        msg = "Session expired."
        raise SuspiciousOperation(msg)
    if not request.session.exists(auth_session.session_key):
        msg = "Session does not exist."
        raise SuspiciousOperation(msg)

    # Delete the existing session
    flush_method = getattr(request.session, "aflush", request.session.flush)
    await ensure_async(flush_method)()
    request.user = AnonymousUser()

    # Switch the client's session
    request.session = type(request.session)(auth_session.session_key)
    load_method = getattr(request.session, "aload", request.session.load)
    await ensure_async(load_method)()
    await auth_session.adelete()

    return HttpResponse(status=204)
