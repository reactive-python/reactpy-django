from logging import getLogger
from uuid import uuid4

import dill as pickle
from django import template
from django.urls import reverse

from reactpy_django import models
from reactpy_django.config import (
    REACTPY_DATABASE,
    REACTPY_DEBUG_MODE,
    REACTPY_RECONNECT_MAX,
    REACTPY_WEBSOCKET_URL,
)
from reactpy_django.exceptions import ComponentDoesNotExistError, ComponentParamError
from reactpy_django.types import ComponentParamData
from reactpy_django.utils import (
    _register_component,
    check_component_args,
    func_has_args,
)


REACTPY_WEB_MODULES_URL = reverse("reactpy:web_modules", args=["x"])[:-1][1:]
register = template.Library()
_logger = getLogger(__name__)


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

    # Register the component if needed
    try:
        component = _register_component(dotted_path)
        uuid = uuid4().hex
        class_ = kwargs.pop("class", "")
        kwargs.pop("key", "")  # `key` is effectively useless for the root node

    except Exception as e:
        if isinstance(e, ComponentDoesNotExistError):
            _logger.error(str(e))
        else:
            _logger.exception(
                "An unknown error has occurred while registering component '%s'.",
                dotted_path,
            )
        return failure_context(dotted_path, e)

    # Store the component's args/kwargs in the database if needed
    # This will be fetched by the websocket consumer later
    try:
        check_component_args(component, *args, **kwargs)
        if func_has_args(component):
            params = ComponentParamData(args, kwargs)
            model = models.ComponentSession(uuid=uuid, params=pickle.dumps(params))
            model.full_clean()
            model.save(using=REACTPY_DATABASE)

    except Exception as e:
        if isinstance(e, ComponentParamError):
            _logger.error(str(e))
        else:
            _logger.exception(
                "An unknown error has occurred while saving component params for '%s'.",
                dotted_path,
            )
        return failure_context(dotted_path, e)

    # Return the template rendering context
    return {
        "class": class_,
        "reactpy_websocket_url": REACTPY_WEBSOCKET_URL,
        "reactpy_web_modules_url": REACTPY_WEB_MODULES_URL,
        "reactpy_reconnect_max": REACTPY_RECONNECT_MAX,
        "reactpy_mount_uuid": uuid,
        "reactpy_component_path": f"{dotted_path}/{uuid}/",
    }


def failure_context(dotted_path: str, error: Exception):
    return {
        "reactpy_failure": True,
        "reactpy_debug_mode": REACTPY_DEBUG_MODE,
        "reactpy_dotted_path": dotted_path,
        "reactpy_error": type(error).__name__,
    }
