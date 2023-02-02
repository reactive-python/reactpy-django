from uuid import uuid4

import dill as pickle
from django import template
from django.urls import reverse

from django_idom import models
from django_idom.config import IDOM_RECONNECT_MAX, IDOM_WEBSOCKET_URL
from django_idom.types import ComponentParamData
from django_idom.utils import _register_component, func_has_params


IDOM_WEB_MODULES_URL = reverse("idom:web_modules", args=["x"])[:-1][1:]
register = template.Library()


@register.inclusion_tag("idom/component.html")
def component(dotted_path: str, *args, **kwargs):
    """This tag is used to embed an existing IDOM component into your HTML template.

    Args:
        dotted_path: The dotted path to the component to render.
        *args: The positional arguments to provide to the component.

    Keyword Args:
        **kwargs: The keyword arguments to provide to the component.

    Example ::

        {% load idom %}
        <!DOCTYPE html>
        <html>
        <body>
            {% component "example_project.my_app.components.hello_world" recipient="World" %}
        </body>
        </html>
    """
    component = _register_component(dotted_path)
    uuid = uuid4().hex
    class_ = kwargs.pop("class", "")
    kwargs.pop("key", "")  # `key` is effectively useless for the root node

    # Store the component's args/kwargs in the database if needed
    # This will be fetched by the websocket consumer later
    try:
        if func_has_params(component, *args, **kwargs):
            params = ComponentParamData(args, kwargs)
            model = models.ComponentParams(uuid=uuid, data=pickle.dumps(params))
            model.full_clean()
            model.save()
    except TypeError as e:
        raise TypeError(
            f"The provided parameters are incompatible with component '{dotted_path}'."
        ) from e

    return {
        "class": class_,
        "idom_websocket_url": IDOM_WEBSOCKET_URL,
        "idom_web_modules_url": IDOM_WEB_MODULES_URL,
        "idom_reconnect_max": IDOM_RECONNECT_MAX,
        "idom_mount_uuid": uuid,
        "idom_component_path": f"{dotted_path}/{uuid}/",
    }
