from uuid import uuid4

import dill as pickle
from django import template
from django.urls import reverse

from reactpy_django import models
from reactpy_django.config import (
    REACTPY_DATABASE,
    REACTPY_RECONNECT_MAX,
    REACTPY_WEBSOCKET_URL,
)
from reactpy_django.types import ComponentParamData
from reactpy_django.utils import _register_component, func_has_params


REACTPY_WEB_MODULES_URL = reverse("reactpy:web_modules", args=["x"])[:-1][1:]
register = template.Library()


@register.inclusion_tag("reactpy/component.html")
def component(dotted_path: str, *args, **kwargs):
    """This tag is used to embed an existing ReactPy component into your HTML template.

    Args:
        dotted_path: The dotted path to the component to render.
        *args: The positional arguments to provide to the component.

    Keyword Args:
        **kwargs: The keyword arguments to provide to the component.

    Example ::

        {% load reactpy %}
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
            model = models.ComponentSession(uuid=uuid, params=pickle.dumps(params))
            model.full_clean()
            model.save(using=REACTPY_DATABASE)
    except TypeError as e:
        raise TypeError(
            f"The provided parameters are incompatible with component '{dotted_path}'."
        ) from e

    return {
        "class": class_,
        "reactpy_websocket_url": REACTPY_WEBSOCKET_URL,
        "reactpy_web_modules_url": REACTPY_WEB_MODULES_URL,
        "reactpy_reconnect_max": REACTPY_RECONNECT_MAX,
        "reactpy_mount_uuid": uuid,
        "reactpy_component_path": f"{dotted_path}/{uuid}/",
    }
