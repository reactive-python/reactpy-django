from __future__ import annotations

from logging import getLogger
from uuid import uuid4

import dill as pickle
from django import template
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse

from reactpy_django import config, models
from reactpy_django.exceptions import (
    ComponentDoesNotExistError,
    ComponentParamError,
    InvalidHostError,
)
from reactpy_django.types import ComponentParamData
from reactpy_django.utils import check_component_args, func_has_args

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
    host = (
        host
        or (next(config.REACTPY_DEFAULT_HOSTS) if config.REACTPY_DEFAULT_HOSTS else "")
    ).strip("/")

    # Check if this this component needs to rendered by the current ASGI app
    use_current_app = not host or host.startswith(perceived_host)

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

    # Fetch the component if needed
    if use_current_app:
        user_component = config.REACTPY_REGISTERED_COMPONENTS.get(dotted_path)
        if not user_component:
            msg = f"Component '{dotted_path}' is not registered as a root component. "
            _logger.error(msg)
            return failure_context(dotted_path, ComponentDoesNotExistError(msg))

    # Store the component's args/kwargs in the database, if needed
    # These will be fetched by the websocket consumer later
    try:
        if use_current_app:
            check_component_args(user_component, *args, **kwargs)
            if func_has_args(user_component):
                save_component_params(args, kwargs, uuid)
        # Can't guarantee args will match up if the component is rendered by a different app.
        # So, we just store any provided args/kwargs in the database.
        elif args or kwargs:
            save_component_params(args, kwargs, uuid)
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
        "reactpy_url_prefix": config.REACTPY_URL_PREFIX,
        "reactpy_reconnect_max": config.REACTPY_RECONNECT_MAX,
        "reactpy_component_path": f"{dotted_path}/{uuid}/",
        "reactpy_resolved_web_modules_path": RESOLVED_WEB_MODULES_PATH,
    }


def failure_context(dotted_path: str, error: Exception):
    return {
        "reactpy_failure": True,
        "reactpy_debug_mode": config.REACTPY_DEBUG_MODE,
        "reactpy_dotted_path": dotted_path,
        "reactpy_error": type(error).__name__,
    }


def save_component_params(args, kwargs, uuid):
    params = ComponentParamData(args, kwargs)
    model = models.ComponentSession(uuid=uuid, params=pickle.dumps(params))
    model.full_clean()
    model.save()
