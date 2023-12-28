from __future__ import annotations

from distutils.util import strtobool
from logging import getLogger
from uuid import uuid4

import dill as pickle
from django import template
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse
from reactpy.backend.hooks import ConnectionContext
from reactpy.backend.types import Connection, Location
from reactpy.core.types import ComponentConstructor
from reactpy.utils import vdom_to_html

from reactpy_django import config, models
from reactpy_django.exceptions import (
    ComponentCarrierError,
    ComponentDoesNotExistError,
    ComponentParamError,
    InvalidHostError,
)
from reactpy_django.types import ComponentParams
from reactpy_django.utils import SyncLayout, validate_component_args

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
    prerender: str = str(config.REACTPY_PRERENDER),
    **kwargs,
):
    """This tag is used to embed an existing ReactPy component into your HTML template.

    Args:
        dotted_path: The dotted path to the component to render.
        *args: The positional arguments to provide to the component.

    Keyword Args:
        class: The HTML class to apply to the top-level component div.
        key: Force the component's root node to use a specific key value. Using \
            key within a template tag is effectively useless.
        host: The host to use for the ReactPy connections. If set to `None`, \
            the host will be automatically configured. \
            Example values include: `localhost:8000`, `example.com`, `example.com/subdir`
        prerender: Configures whether to pre-render this component, which \
            enables SEO compatibility and reduces perceived latency.
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
    request: HttpRequest | None = context.get("request")
    perceived_host = (request.get_host() if request else "").strip("/")
    host = (
        host
        or (next(config.REACTPY_DEFAULT_HOSTS) if config.REACTPY_DEFAULT_HOSTS else "")
    ).strip("/")
    is_local = not host or host.startswith(perceived_host)
    uuid = uuid4().hex
    class_ = kwargs.pop("class", "")
    component_has_args = args or kwargs
    user_component: ComponentConstructor | None = None
    _prerender_html = ""

    # Validate the host
    if host and config.REACTPY_DEBUG_MODE:
        try:
            validate_host(host)
        except InvalidHostError as e:
            return failure_context(dotted_path, e)

    # Fetch the component
    if is_local:
        user_component = config.REACTPY_REGISTERED_COMPONENTS.get(dotted_path)
        if not user_component:
            msg = f"Component '{dotted_path}' is not registered as a root component. "
            _logger.error(msg)
            return failure_context(dotted_path, ComponentDoesNotExistError(msg))

    # Validate the component args & kwargs
    if is_local and config.REACTPY_DEBUG_MODE:
        try:
            validate_component_args(user_component, *args, **kwargs)
        except ComponentParamError as e:
            _logger.error(str(e))
            return failure_context(dotted_path, e)

    # Store args & kwargs in the database (fetched by our websocket later)
    if component_has_args:
        try:
            save_component_params(args, kwargs, uuid)
        except Exception as e:
            _logger.exception(
                "An unknown error has occurred while saving component params for '%s'.",
                dotted_path,
            )
            return failure_context(dotted_path, e)

    # Pre-render the component, if requested
    if strtobool(prerender):
        if not is_local:
            msg = "Cannot pre-render non-local components."
            _logger.error(msg)
            return failure_context(dotted_path, ComponentDoesNotExistError(msg))
        if not user_component:
            msg = "Cannot pre-render component that is not registered."
            _logger.error(msg)
            return failure_context(dotted_path, ComponentDoesNotExistError(msg))
        if not request:
            msg = (
                "Cannot pre-render component without a HTTP request. Are you missing the "
                "request context processor in settings.py:TEMPLATES['OPTIONS']['context_processors']?"
            )
            _logger.error(msg)
            return failure_context(dotted_path, ComponentCarrierError(msg))
        _prerender_html = prerender_component(user_component, args, kwargs, request)

    # Return the template rendering context
    return {
        "reactpy_class": class_,
        "reactpy_uuid": uuid,
        "reactpy_host": host or perceived_host,
        "reactpy_url_prefix": config.REACTPY_URL_PREFIX,
        "reactpy_component_path": f"{dotted_path}/{uuid}/"
        if component_has_args
        else f"{dotted_path}/",
        "reactpy_resolved_web_modules_path": RESOLVED_WEB_MODULES_PATH,
        "reactpy_reconnect_interval": config.REACTPY_RECONNECT_INTERVAL,
        "reactpy_reconnect_max_interval": config.REACTPY_RECONNECT_MAX_INTERVAL,
        "reactpy_reconnect_backoff_multiplier": config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER,
        "reactpy_reconnect_max_retries": config.REACTPY_RECONNECT_MAX_RETRIES,
        "reactpy_prerender_html": _prerender_html,
    }


def failure_context(dotted_path: str, error: Exception):
    return {
        "reactpy_failure": True,
        "reactpy_debug_mode": config.REACTPY_DEBUG_MODE,
        "reactpy_dotted_path": dotted_path,
        "reactpy_error": type(error).__name__,
    }


def save_component_params(args, kwargs, uuid):
    params = ComponentParams(args, kwargs)
    model = models.ComponentSession(uuid=uuid, params=pickle.dumps(params))
    model.full_clean()
    model.save()


def validate_host(host: str):
    if "://" in host:
        protocol = host.split("://")[0]
        msg = (
            f"Invalid host provided to component. Contains a protocol '{protocol}://'."
        )
        _logger.error(msg)
        raise InvalidHostError(msg)


def prerender_component(
    user_component: ComponentConstructor, args, kwargs, request: HttpRequest
):
    search = request.GET.urlencode()
    with SyncLayout(
        ConnectionContext(
            user_component(*args, **kwargs),
            value=Connection(
                scope=getattr(request, "scope", {}),
                location=Location(
                    pathname=request.path, search=f"?{search}" if search else ""
                ),
                carrier=request,
            ),
        )
    ) as layout:
        vdom_tree = layout.render()["model"]

    return vdom_to_html(vdom_tree)
