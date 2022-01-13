import os

from aiofile import async_open
from django.core.cache import caches
from django.http import HttpRequest, HttpResponse
from idom.config import IDOM_WED_MODULES_DIR

from .config import IDOM_CACHE


idom_cache = caches[IDOM_CACHE]


async def web_modules_file(request: HttpRequest, file: str) -> HttpResponse:
    """Gets a web modules file. Web modules files  from cache"""
    path = IDOM_WED_MODULES_DIR.current.joinpath(*file.split("/")).absolute()
    last_modified_time = os.stat(path).st_mtime
    cache_key = f"django_idom:web_module:{path}"
    response = await idom_cache.aget(cache_key, version=last_modified_time)
    if response is None:
        async with async_open(path, "r") as fp:
            response = HttpResponse(await fp.read(), content_type="text/javascript")
        await idom_cache.adelete(cache_key)
        await idom_cache.aset(
            cache_key, response, timeout=None, version=last_modified_time
        )
    return response
