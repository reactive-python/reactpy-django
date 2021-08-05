import json
from urllib.parse import urlencode
from uuid import uuid4

from django import template

from django_idom.app_settings import IDOM_WEB_MODULES_URL, IDOM_WEBSOCKET_URL

from ..app_components import has_component


register = template.Library()


@register.inclusion_tag("idom/view.html")
def idom_view(_component_id_, **kwargs):
    if not has_component(_component_id_):
        raise ValueError(f"No component {_component_id_!r} exists")

    json_kwargs = json.dumps(kwargs, separators=(",", ":"))

    return {
        "idom_websocket_url": IDOM_WEBSOCKET_URL,
        "idom_web_modules_url": IDOM_WEB_MODULES_URL,
        "idom_mount_uuid": uuid4().hex,
        "idom_view_id": _component_id_,
        "idom_view_params": urlencode({"kwargs": json_kwargs}),
    }
