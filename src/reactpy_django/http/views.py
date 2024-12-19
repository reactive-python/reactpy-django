import os
from urllib.parse import parse_qs

from django.core.exceptions import SuspiciousOperation
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseNotFound
from reactpy.config import REACTPY_WEB_MODULES_DIR

from reactpy_django.utils import FileAsyncIterator, render_view


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
