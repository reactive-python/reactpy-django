import asyncio
import functools
import os

from django.core.cache import caches
from django.http import HttpRequest, HttpResponse
from idom.config import IDOM_WED_MODULES_DIR

from .config import IDOM_WEB_MODULE_CACHE, IDOM_WEB_MODULE_LRU_CACHE_SIZE


if IDOM_WEB_MODULE_CACHE is None:

    def async_lru_cache(*lru_cache_args, **lru_cache_kwargs):
        def async_lru_cache_decorator(async_function):
            @functools.lru_cache(*lru_cache_args, **lru_cache_kwargs)
            def cached_async_function(*args, **kwargs):
                coroutine = async_function(*args, **kwargs)
                return asyncio.ensure_future(coroutine)

            return cached_async_function

        return async_lru_cache_decorator

    @async_lru_cache(IDOM_WEB_MODULE_LRU_CACHE_SIZE)
    async def web_modules_file(request: HttpRequest, file: str) -> HttpResponse:
        file_path = IDOM_WED_MODULES_DIR.current.joinpath(*file.split("/"))
        return HttpResponse(file_path.read_text(), content_type="text/javascript")

else:
    _web_module_cache = caches[IDOM_WEB_MODULE_CACHE]

    async def web_modules_file(request: HttpRequest, file: str) -> HttpResponse:
        file = IDOM_WED_MODULES_DIR.current.joinpath(*file.split("/")).absolute()
        last_modified_time = os.stat(file).st_mtime
        cache_key = f"{file}:{last_modified_time}"

        response = _web_module_cache.get(cache_key)
        if response is None:
            response = HttpResponse(file.read_text(), content_type="text/javascript")
            _web_module_cache.set(cache_key, response, timeout=None)

        return response
