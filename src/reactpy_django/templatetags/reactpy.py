from logging import getLogger
from uuid import uuid4

import dill as pickle
from django import template
from django.urls import NoReverseMatch, reverse

from reactpy_django import models
from reactpy_django.config import (
    REACTPY_DEBUG_MODE,
    REACTPY_RECONNECT_MAX,
    REACTPY_URL_PREFIX,
)
from reactpy_django.exceptions import ComponentDoesNotExistError, ComponentParamError
from reactpy_django.types import ComponentParamData
from reactpy_django.utils import (
    _register_component,
    check_component_args,
    func_has_args,
)

try:
    RESOLVED_WEB_MODULES_PATH = reverse("reactpy:web_modules", args=["/"]).strip("/")
except NoReverseMatch:
    RESOLVED_WEB_MODULES_PATH = ""
register = template.Library()
_logger = getLogger(__name__)


@register.inclusion_tag("reactpy/component.html")
def component(
    dotted_path: str, *args, ws_host: str = "", http_host: str = "", **kwargs
):
    """This tag is used to embed an existing ReactPy component into your HTML template.

    Args:
        dotted_path: The dotted path to the component to render.
        *args: The positional arguments to provide to the component.

    Keyword Args:
        ws_host: The host domain to use for the ReactPy websocket connection. If set to None, \
            the host will be fetched via JavaScript. \
            Note: You typically will not need to register the ReactPy websocket path on any \
            application(s) that do not perform component rendering.
        http_host: The host domain to use for the ReactPy HTTP connection. If set to None, \
            the host will be fetched via JavaScript. \
            Note: You typically will not need to register ReactPy HTTP paths on any \
            application(s) that do not perform component rendering.
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
            model.save()

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
        "reactpy_class": class_,
        "reactpy_uuid": uuid,
        "reactpy_ws_host": ws_host.strip("/"),
        "reactpy_http_host": http_host.strip("/"),
        "reactpy_url_prefix": REACTPY_URL_PREFIX,
        "reactpy_reconnect_max": REACTPY_RECONNECT_MAX,
        "reactpy_component_path": f"{dotted_path}/{uuid}/",
        "reactpy_resolved_web_modules_path": RESOLVED_WEB_MODULES_PATH,
    }


def failure_context(dotted_path: str, error: Exception):
    return {
        "reactpy_failure": True,
        "reactpy_debug_mode": REACTPY_DEBUG_MODE,
        "reactpy_dotted_path": dotted_path,
        "reactpy_error": type(error).__name__,
    }
