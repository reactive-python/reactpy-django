import os

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
    path = os.path.abspath(web_modules_dir.joinpath(*file.split("/")))

    # Prevent attempts to walk outside of the web modules dir
    if str(web_modules_dir) != os.path.commonpath((path, web_modules_dir)):
        raise SuspiciousOperation(
            "Attempt to access a directory outside of REACTPY_WEB_MODULES_DIR."
        )

    # Fetch the file from cache, if available
    last_modified_time = os.stat(path).st_mtime
    cache_key = create_cache_key("web_module", str(path).lstrip(str(web_modules_dir)))
    response = await caches[REACTPY_CACHE].aget(
        cache_key, version=int(last_modified_time)
    )
    if response is None:
        async with async_open(path, "r") as fp:
            response = HttpResponse(await fp.read(), content_type="text/javascript")
        await caches[REACTPY_CACHE].adelete(cache_key)
        await caches[REACTPY_CACHE].aset(
            cache_key, response, timeout=None, version=int(last_modified_time)
        )
    return response


async def view_to_component_iframe(
    request: HttpRequest, view_path: str
) -> HttpResponse:
    """Returns a view that was registered by view_to_component.
    This view is intended to be used as iframe, for compatibility purposes."""
    from reactpy_django.config import REACTPY_VIEW_COMPONENT_IFRAMES

    # Get the view from REACTPY_REGISTERED_IFRAMES
    iframe = REACTPY_VIEW_COMPONENT_IFRAMES.get(view_path)
    if not iframe:
        return HttpResponseNotFound()

    # Render the view
    response = await render_view(iframe.view, request, iframe.args, iframe.kwargs)

    # Ensure page can be rendered as an iframe
    response["X-Frame-Options"] = "SAMEORIGIN"
    return response
