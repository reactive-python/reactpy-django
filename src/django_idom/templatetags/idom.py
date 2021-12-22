import json
from urllib.parse import urlencode
from uuid import uuid4

from django import template

from django_idom.config import (
    IDOM_WEB_MODULES_URL,
    IDOM_WEBSOCKET_URL,
    IDOM_WS_MAX_RECONNECT_DELAY,
)
from django_idom.utils import _register_component


register = template.Library()


@register.inclusion_tag("idom/component.html")
def idom_component(_component_id_, **kwargs):
    _register_component(_component_id_)

    class_ = kwargs.pop("class", "")
    json_kwargs = json.dumps(kwargs, separators=(",", ":"))

    return {
        "class": class_,
        "idom_websocket_url": IDOM_WEBSOCKET_URL,
        "idom_web_modules_url": IDOM_WEB_MODULES_URL,
        "idom_ws_max_reconnect_delay": IDOM_WS_MAX_RECONNECT_DELAY,
        "idom_mount_uuid": uuid4().hex,
        "idom_component_id": _component_id_,
        "idom_component_params": urlencode({"kwargs": json_kwargs}),
    }
