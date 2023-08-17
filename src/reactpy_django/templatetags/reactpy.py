from __future__ import annotations

from logging import getLogger
from uuid import uuid4

import dill as pickle
from django import template
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse

from reactpy_django import models
from reactpy_django.config import (
    REACTPY_DEBUG_MODE,
    REACTPY_RECONNECT_MAX,
    REACTPY_URL_PREFIX,
)
from reactpy_django.exceptions import (
    ComponentDoesNotExistError,
    ComponentParamError,
    InvalidHostError,
)
from reactpy_django.types import ComponentParamData
from reactpy_django.utils import (
    check_component_args,
    func_has_args,
    register_component,
)

try:
    RESOLVED_WEB_MODULES_PATH = reverse("reactpy:web_modules", args=["/"]).strip("/")
except NoReverseMatch:
    RESOLVED_WEB_MODULES_PATH = ""
register = template.Library()
_logger = getLogger(__name__)


@register.inclusion_tag("reactpy/component.html", takes_context=True)
def component(
    context: template.RequestContext,
    dotted_path: str,
    *args,
    host: str | None = None,
    **kwargs,
):
    """This tag is used to embed an existing ReactPy component into your HTML template.

    Args:
        dotted_path: The dotted path to the component to render.
        *args: The positional arguments to provide to the component.

    Keyword Args:
        host: The host to use for the ReactPy connections. If set to `None`, \
            the host will be automatically configured. \
            Example values include: `localhost:8000`, `example.com`, `example.com/subdir`
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

    # Determine the host
    request: HttpRequest | None = context.get("request")
    perceived_host = (request.get_host() if request else "").strip("/")
    host = (host or "").strip("/")

    # Create context variables
    uuid = uuid4().hex
    class_ = kwargs.pop("class", "")
    kwargs.pop("key", "")  # `key` is effectively useless for the root node

    # Fail if user has a method in their host
    if host.find("://") != -1:
        protocol = host.split("://")[0]
        msg = (
            f"Invalid host provided to component. Contains a protocol '{protocol}://'."
        )
        _logger.error(msg)
        return failure_context(dotted_path, InvalidHostError(msg))

    # Only handle this component if host is unset, or the hosts match
    if not host or (host == perceived_host):
        # Register the component if needed
        try:
            component = register_component(dotted_path)
        except Exception as e:
            if isinstance(e, ComponentDoesNotExistError):
                _logger.error(str(e))
            else:
                _logger.exception(
                    "An unknown error has occurred while registering component '%s'.",
                    dotted_path,
                )
            return failure_context(dotted_path, e)

        # Store the component's args/kwargs in the database, if needed
        # These will be fetched by the websocket consumer later
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
        "reactpy_host": host or perceived_host,
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
