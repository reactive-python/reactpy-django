import json
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

from django import template
from django.urls import reverse

from django_idom.config import IDOM_WEBSOCKET_URL, IDOM_WS_MAX_RECONNECT_TIMEOUT
from django_idom.utils import _register_component


IDOM_WEB_MODULES_URL = reverse("idom:web_modules", args=["x"])[:-1][1:]
register = template.Library()


@register.inclusion_tag("idom/component.html")
def component(dotted_path: str, **kwargs: Any):
    """This tag is used to embed an existing IDOM component into your HTML template.

    Args:
        dotted_path: The dotted path to the component to render.

    Keyword Args:
        **kwargs: The keyword arguments to pass to the component.

    Example ::

        {% load idom %}
        <!DOCTYPE html>
        <html>
        <body>
            {% component "example_project.my_app.components.hello_world" recipient="World" %}
        </body>
        </html>
    """
    _register_component(dotted_path)

    class_ = kwargs.pop("class", "")
    json_kwargs = json.dumps(kwargs, separators=(",", ":"))

    return {
        "class": class_,
        "idom_websocket_url": IDOM_WEBSOCKET_URL,
        "idom_web_modules_url": IDOM_WEB_MODULES_URL,
        "idom_ws_max_reconnect_timeout": IDOM_WS_MAX_RECONNECT_TIMEOUT,
        "idom_mount_uuid": uuid4().hex,
        "idom_component_id": dotted_path,
        "idom_component_params": urlencode({"kwargs": json_kwargs}),
    }
