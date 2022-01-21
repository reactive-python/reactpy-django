import os

from aiofile import async_open
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest, HttpResponse
from idom.config import IDOM_WED_MODULES_DIR

from django_idom.config import IDOM_CACHE


async def web_modules_file(request: HttpRequest, file: str) -> HttpResponse:
    """Gets JavaScript required for IDOM modules at runtime. These modules are
    returned from cache if available."""
    web_modules_dir = IDOM_WED_MODULES_DIR.current
    path = web_modules_dir.joinpath(*file.split("/")).absolute()

    # Prevent attempts to walk outside of the web modules dir
    if str(web_modules_dir) != os.path.commonpath((path, web_modules_dir)):
        raise SuspiciousOperation(
            "Attempt to access a directory outside of IDOM_WED_MODULES_DIR."
        )

    # Fetch the file from cache, if available
    last_modified_time = os.stat(path).st_mtime
    cache_key = f"django_idom:web_module:{str(path).lstrip(str(web_modules_dir))}"
    response = await IDOM_CACHE.aget(cache_key, version=last_modified_time)
    if response is None:
        async with async_open(path, "r") as fp:
            response = HttpResponse(await fp.read(), content_type="text/javascript")
        await IDOM_CACHE.adelete(cache_key)
        await IDOM_CACHE.aset(
            cache_key, response, timeout=None, version=last_modified_time
        )
    return response
