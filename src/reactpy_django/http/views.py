import os
from urllib.parse import parse_qs

from aiofile import async_open
from django.core.cache import caches
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from reactpy.config import REACTPY_WEB_MODULES_DIR

from reactpy_django.utils import create_cache_key, render_view


async def web_modules_file(request: HttpRequest, file: str) -> HttpResponse:
    """Gets JavaScript required for ReactPy modules at runtime. These modules are
    returned from cache if available."""
    from reactpy_django.config import REACTPY_CACHE

    web_modules_dir = REACTPY_WEB_MODULES_DIR.current
    path = os.path.abspath(web_modules_dir.joinpath(file))

    # Prevent attempts to walk outside of the web modules dir
    if str(web_modules_dir) != os.path.commonpath((path, web_modules_dir)):
        raise SuspiciousOperation(
            "Attempt to access a directory outside of REACTPY_WEB_MODULES_DIR."
        )

    # Fetch the file from cache, if available
    last_modified_time = os.stat(path).st_mtime
    cache_key = create_cache_key("web_modules", path)
    file_contents = await caches[REACTPY_CACHE].aget(
        cache_key, version=int(last_modified_time)
    )
    if file_contents is None:
        async with async_open(path, "r") as fp:
            file_contents = await fp.read()
        await caches[REACTPY_CACHE].adelete(cache_key)
        await caches[REACTPY_CACHE].aset(
            cache_key, file_contents, timeout=604800, version=int(last_modified_time)
        )
    return HttpResponse(file_contents, content_type="text/javascript")


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
