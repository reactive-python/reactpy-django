import json
import sys
from importlib import import_module
from urllib.parse import urlencode
from uuid import uuid4

from django import template

from django_idom.config import (
    IDOM_REGISTERED_COMPONENTS,
    IDOM_WEB_MODULES_URL,
    IDOM_WEBSOCKET_URL,
)


register = template.Library()


@register.inclusion_tag("idom/view.html")
def idom_component(_component_id_, **kwargs):
    _register_component(_component_id_)

    json_kwargs = json.dumps(kwargs, separators=(",", ":"))

    return {
        "idom_websocket_url": IDOM_WEBSOCKET_URL,
        "idom_web_modules_url": IDOM_WEB_MODULES_URL,
        "idom_mount_uuid": uuid4().hex,
        "idom_component_id": _component_id_,
        "idom_component_params": urlencode({"kwargs": json_kwargs}),
    }


def _register_component(full_component_name: str) -> None:
    module_name, component_name = full_component_name.rsplit(".", 1)

    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        try:
            module = import_module(module_name)
        except ImportError as error:
            raise RuntimeError(
                f"Failed to import {module_name!r} while loading {component_name!r}"
            ) from error

    try:
        component = getattr(module, component_name)
    except AttributeError as error:
        raise RuntimeError(
            f"Module {module_name!r} has no component named {component_name!r}"
        ) from error

    IDOM_REGISTERED_COMPONENTS[full_component_name] = component
