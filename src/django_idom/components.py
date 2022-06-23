import os

from django.contrib.staticfiles.finders import find
from idom import component, html

from django_idom.config import IDOM_CACHE


@component
def static_css(static_path: str):
    """Fetches a CSS static file for use within IDOM. This allows for deferred CSS loading."""
    return html.style(_cached_static_contents(static_path, "css_contents"))


@component
def static_js(static_path: str):
    """Fetches a JS static file for use within IDOM. This allows for deferred JS loading."""
    return html.script(_cached_static_contents(static_path, "js_contents"))


def _cached_static_contents(static_path: str, cache_name: str):
    # Try to find the file within Django's static files
    abs_path = find(static_path)
    if not abs_path:
        raise FileNotFoundError(
            f"Could not find static file {static_path} within Django's static files."
        )

    # Fetch the file from cache, if available
    last_modified_time = os.stat(abs_path).st_mtime
    cache_key = f"django_idom:{cache_name}:{static_path}"
    file_contents = IDOM_CACHE.get(cache_key, version=last_modified_time)
    if file_contents is None:
        with open(abs_path, encoding="utf-8") as static_file:
            file_contents = static_file.read()
        IDOM_CACHE.delete(cache_key)
        IDOM_CACHE.set(
            cache_key, file_contents, timeout=None, version=last_modified_time
        )

    return file_contents
