import os

from django import template


register = template.Library()


@register.simple_tag
def check_async_unsafe():
    return bool(os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE", None))
