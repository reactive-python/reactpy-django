import os

from django.core.cache import caches
from django.http import HttpRequest, HttpResponse
from idom.config import IDOM_WED_MODULES_DIR

from .config import IDOM_CACHE


idom_cache = caches[IDOM_CACHE]


async def web_modules_file(request: HttpRequest, file: str) -> HttpResponse:
    """Gets a web modules file. Web modules files  from cache"""
    path = IDOM_WED_MODULES_DIR.current.joinpath(*file.split("/")).absolute()
    last_modified_time = os.stat(path).st_mtime
    cache_key = f"django_idom:{path}"
    response = idom_cache.get(cache_key, version=last_modified_time)
    if response is None:
        response = HttpResponse(path.read_text(), content_type="text/javascript")
        idom_cache.delete(cache_key)
        idom_cache.set(cache_key, response, timeout=None, version=last_modified_time)
    return response
