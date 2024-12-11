from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING
from uuid import uuid4

from django import template
from django.urls import NoReverseMatch, reverse

from reactpy_django import config as reactpy_config
from reactpy_django.exceptions import (
    ComponentCarrierError,
    ComponentDoesNotExistError,
    ComponentParamError,
    InvalidHostError,
    OfflineComponentMissingError,
)
from reactpy_django.pyscript.utils import PYSCRIPT_LAYOUT_HANDLER, extend_pyscript_config, render_pyscript_template
from reactpy_django.utils import (
    prerender_component,
    reactpy_to_string,
    save_component_params,
    str_to_bool,
    validate_component_args,
    validate_host,
)

if TYPE_CHECKING:
    from django.http import HttpRequest
    from reactpy.core.types import ComponentConstructor, ComponentType, VdomDict

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
    prerender: str = str(reactpy_config.REACTPY_PRERENDER),
    offline: str = "",
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
        host: The host to use for ReactPy connections. If set to `None`, \
            the host will be automatically configured. \
            Example values include: `localhost:8000`, `example.com`, `example.com/subdir`
        prerender: Configures whether to pre-render this component, which \
            enables SEO compatibility and reduces perceived latency.
        offline: The dotted path to the component to render when the client is offline.
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
    from reactpy_django.config import DJANGO_DEBUG

    request: HttpRequest | None = context.get("request")
    perceived_host = (request.get_host() if request else "").strip("/")
    host = (host or (next(reactpy_config.REACTPY_DEFAULT_HOSTS) if reactpy_config.REACTPY_DEFAULT_HOSTS else "")).strip(
        "/"
    )
    is_local = not host or host.startswith(perceived_host)
    uuid = str(uuid4())
    class_ = kwargs.pop("class", "")
    has_args = bool(args or kwargs)
    user_component: ComponentConstructor | None = None
    _prerender_html = ""
    _offline_html = ""

    # Validate the host
    if host and DJANGO_DEBUG:
        try:
            validate_host(host)
        except InvalidHostError as e:
            return failure_context(dotted_path, e)

    # Fetch the component
    if is_local:
        user_component = reactpy_config.REACTPY_REGISTERED_COMPONENTS.get(dotted_path)
        if not user_component:
            msg = f"Component '{dotted_path}' is not registered as a root component. "
            _logger.error(msg)
            return failure_context(dotted_path, ComponentDoesNotExistError(msg))

    # Validate the component args & kwargs
    if is_local and DJANGO_DEBUG:
        try:
            validate_component_args(user_component, *args, **kwargs)
        except ComponentParamError as e:
            _logger.exception(
                "The parameters you provided for component '%s' was incorrect.",
                dotted_path,
            )
            return failure_context(dotted_path, e)

    # Store args & kwargs in the database (fetched by our websocket later)
    if has_args:
        try:
            save_component_params(args, kwargs, uuid)
        except Exception as e:
            _logger.exception(
                "An unknown error has occurred while saving component parameters for '%s'.",
                dotted_path,
            )
            return failure_context(dotted_path, e)

    # Pre-render the component, if requested
    if str_to_bool(prerender):
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
        _prerender_html = prerender_component(user_component, args, kwargs, uuid, request)

    # Fetch the offline component's HTML, if requested
    if offline:
        offline_component = reactpy_config.REACTPY_REGISTERED_COMPONENTS.get(offline)
        if not offline_component:
            msg = f"Cannot render offline component '{offline}'. It is not registered as a component."
            _logger.error(msg)
            return failure_context(dotted_path, OfflineComponentMissingError(msg))
        if not request:
            msg = (
                "Cannot render an offline component without a HTTP request. Are you missing the "
                "request context processor in settings.py:TEMPLATES['OPTIONS']['context_processors']?"
            )
            _logger.error(msg)
            return failure_context(dotted_path, ComponentCarrierError(msg))
        _offline_html = prerender_component(offline_component, [], {}, uuid, request)

    # Return the template rendering context
    return {
        "reactpy_class": class_,
        "reactpy_uuid": uuid,
        "reactpy_host": host or perceived_host,
        "reactpy_url_prefix": reactpy_config.REACTPY_URL_PREFIX,
        "reactpy_component_path": f"{dotted_path}/{uuid}/{int(has_args)}/",
        "reactpy_resolved_web_modules_path": RESOLVED_WEB_MODULES_PATH,
        "reactpy_reconnect_interval": reactpy_config.REACTPY_RECONNECT_INTERVAL,
        "reactpy_reconnect_max_interval": reactpy_config.REACTPY_RECONNECT_MAX_INTERVAL,
        "reactpy_reconnect_backoff_multiplier": reactpy_config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER,
        "reactpy_reconnect_max_retries": reactpy_config.REACTPY_RECONNECT_MAX_RETRIES,
        "reactpy_prerender_html": _prerender_html,
        "reactpy_offline_html": _offline_html,
    }


@register.inclusion_tag("reactpy/pyscript_component.html", takes_context=True)
def pyscript_component(
    context: template.RequestContext,
    *file_paths: str,
    initial: str | VdomDict | ComponentType = "",
    root: str = "root",
):
    """
    Args:
        file_paths: File path to your client-side component. If multiple paths are \
            provided, the contents are automatically merged.

    Kwargs:
        initial: The initial HTML that is displayed prior to the PyScript component \
            loads. This can either be a string containing raw HTML, a \
            `#!python reactpy.html` snippet, or a non-interactive component.
        root: The name of the root component function.
    """
    if not file_paths:
        msg = "At least one file path must be provided to the 'pyscript_component' tag."
        raise ValueError(msg)

    uuid = uuid4().hex
    request: HttpRequest | None = context.get("request")
    initial = reactpy_to_string(initial, request=request, uuid=uuid)
    executor = render_pyscript_template(file_paths, uuid, root)

    return {
        "pyscript_executor": executor,
        "pyscript_uuid": uuid,
        "pyscript_initial_html": initial,
    }


@register.inclusion_tag("reactpy/pyscript_setup.html")
def pyscript_setup(
    *extra_py: str,
    extra_js: str | dict = "",
    config: str | dict = "",
):
    """
    Args:
        extra_py: Dependencies that need to be loaded on the page for \
            your PyScript components. Each dependency must be contained \
            within it's own string and written in Python requirements file syntax.

    Kwargs:
        extra_js: A JSON string or Python dictionary containing a vanilla \
            JavaScript module URL and the `name: str` to access it within \
            `pyscript.js_modules.*`.
        config: A JSON string or Python dictionary containing PyScript \
            configuration values.
    """
    from reactpy_django.config import DJANGO_DEBUG

    return {
        "pyscript_config": extend_pyscript_config(extra_py, extra_js, config),
        "pyscript_layout_handler": PYSCRIPT_LAYOUT_HANDLER,
        "django_debug": DJANGO_DEBUG,
    }


def failure_context(dotted_path: str, error: Exception):
    from reactpy_django.config import DJANGO_DEBUG

    return {
        "reactpy_failure": True,
        "django_debug": DJANGO_DEBUG,
        "reactpy_dotted_path": dotted_path,
        "reactpy_error": type(error).__name__,
    }
