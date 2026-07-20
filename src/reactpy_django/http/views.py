import os
from urllib.parse import parse_qs

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


async def auth_manager(request: HttpRequest, uuid: str) -> HttpResponse:
    """Switches the client's active auth session to match ReactPy's session.

    This view exists because ReactPy is rendered via WebSockets, and browsers do not
    allow active WebSocket connections to modify cookies. Django's authentication
    design requires HTTP cookies to persist state changes.
    """
    from reactpy_django.models import AuthToken

    # Find out what session the client wants to switch to
    token = await AuthToken.objects.aget(value=uuid)

    # CHECK: Token has expired?
    if token.expired:
        msg = "Session expired."
        await token.adelete()
        raise SuspiciousOperation(msg)

    # CHECK: Token does not exist?
    exists_method = getattr(request.session, "aexists", request.session.exists)
    if not await ensure_async(exists_method)(token.session_key):
        msg = "Attempting to switch to a session that does not exist."
        raise SuspiciousOperation(msg)

    # CHECK: Client already using the correct session key?
    if request.session.session_key == token.session_key:
        await token.adelete()
        return HttpResponse(status=204)

    # Switch the client's session
    request.session = type(request.session)(session_key=token.session_key)
    load_method = getattr(request.session, "aload", request.session.load)
    await ensure_async(load_method)()
    request.session.modified = True
    save_method = getattr(request.session, "asave", request.session.save)
    await ensure_async(save_method)()
    await token.adelete()
    return HttpResponse(status=204)
