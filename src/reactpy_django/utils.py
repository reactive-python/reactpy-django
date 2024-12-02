from __future__ import annotations

import contextlib
import inspect
import json
import logging
import os
import re
import textwrap
from asyncio import iscoroutinefunction
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from fnmatch import fnmatch
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable
from uuid import UUID, uuid4

import dill
import jsonpointer
import orjson
import reactpy
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.db.models import ManyToManyField, ManyToOneRel, prefetch_related_objects
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template import engines
from django.templatetags.static import static
from django.utils.encoding import smart_str
from reactpy import vdom_to_html
from reactpy.backend.hooks import ConnectionContext
from reactpy.backend.types import Connection, Location
from reactpy.core.layout import Layout

from reactpy_django.exceptions import (
    ComponentDoesNotExistError,
    ComponentParamError,
    InvalidHostError,
    ViewDoesNotExistError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from django.views import View
    from reactpy.types import ComponentConstructor

_logger = logging.getLogger(__name__)
_TAG_PATTERN = r"(?P<tag>component)"
_PATH_PATTERN = r"""(?P<path>"[^"'\s]+"|'[^"'\s]+')"""
_OFFLINE_KWARG_PATTERN = rf"""(\s*offline\s*=\s*{_PATH_PATTERN.replace(r"<path>", r"<offline_path>")})"""
_GENERIC_KWARG_PATTERN = r"""(\s*.*?)"""
COMMENT_REGEX = re.compile(r"<!--[\s\S]*?-->")
COMPONENT_REGEX = re.compile(
    r"{%\s*"
    + _TAG_PATTERN
    + r"\s*"
    + _PATH_PATTERN
    + rf"({_OFFLINE_KWARG_PATTERN}|{_GENERIC_KWARG_PATTERN})*?"
    + r"\s*%}"
)
PYSCRIPT_COMPONENT_TEMPLATE = (Path(__file__).parent / "pyscript" / "component_template.py").read_text(encoding="utf-8")
PYSCRIPT_LAYOUT_HANDLER = (Path(__file__).parent / "pyscript" / "layout_handler.py").read_text(encoding="utf-8")
PYSCRIPT_DEFAULT_CONFIG: dict[str, Any] = {}
FILE_ASYNC_ITERATOR_THREAD = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ReactPy-Django-FileAsyncIterator")


async def render_view(
    view: Callable | View,
    request: HttpRequest,
    args: Sequence,
    kwargs: dict,
) -> HttpResponse:
    """Ingests a Django view (class or function) and returns an HTTP response object."""
    # Convert class-based view to function-based view
    if getattr(view, "as_view", None):
        view = view.as_view()

    # Async function view
    if iscoroutinefunction(view):
        response = await view(request, *args, **kwargs)

    # Sync function view
    else:
        response = await database_sync_to_async(view)(request, *args, **kwargs)

    # TemplateView
    if getattr(response, "render", None):
        response = await database_sync_to_async(response.render)()

    return response


def register_component(component: ComponentConstructor | str):
    """Adds a component to the list of known registered components.

    Args:
        component: The component to register. Can be a component function or dotted path to a component.

    """
    from reactpy_django.config import (
        REACTPY_FAILED_COMPONENTS,
        REACTPY_REGISTERED_COMPONENTS,
    )

    dotted_path = component if isinstance(component, str) else generate_obj_name(component)
    try:
        REACTPY_REGISTERED_COMPONENTS[dotted_path] = import_dotted_path(dotted_path)
    except AttributeError as e:
        REACTPY_FAILED_COMPONENTS.add(dotted_path)
        msg = f"Error while fetching '{dotted_path}'. {(str(e).capitalize())}."
        raise ComponentDoesNotExistError(msg) from e


def register_iframe(view: Callable | View | str):
    """Registers a view to be used as an iframe component.

    Args:
        view: The view to register. Can be a function or class based view, or a dotted path to a view.
    """
    from reactpy_django.config import REACTPY_REGISTERED_IFRAME_VIEWS

    if hasattr(view, "view_class"):
        view = view.view_class
    dotted_path = view if isinstance(view, str) else generate_obj_name(view)
    try:
        REACTPY_REGISTERED_IFRAME_VIEWS[dotted_path] = import_dotted_path(dotted_path)
    except AttributeError as e:
        msg = f"Error while fetching '{dotted_path}'. {(str(e).capitalize())}."
        raise ViewDoesNotExistError(msg) from e


def import_dotted_path(dotted_path: str) -> Callable:
    """Imports a dotted path and returns the callable."""
    module_name, component_name = dotted_path.rsplit(".", 1)

    try:
        module = import_module(module_name)
    except ImportError as error:
        msg = f"Failed to import {module_name!r} while loading {component_name!r}"
        raise RuntimeError(msg) from error

    return getattr(module, component_name)


class RootComponentFinder:
    """Searches Django templates to find and register all root components.
    This should only be `run` once on startup to maintain synchronization during mulitprocessing.
    """

    def run(self):
        """Registers all ReactPy components found within Django templates."""
        # Get all template folder paths
        paths = self.get_paths()
        # Get all HTML template files
        templates = self.get_templates(paths)
        # Get all components
        components = self.get_components(templates)
        # Register all components
        self.register_components(components)

    def get_loaders(self):
        """Obtains currently configured template loaders."""
        template_source_loaders = []
        for e in engines.all():
            if hasattr(e, "engine"):
                template_source_loaders.extend(e.engine.get_template_loaders(e.engine.loaders))
        loaders = []
        for loader in template_source_loaders:
            if hasattr(loader, "loaders"):
                loaders.extend(loader.loaders)
            else:
                loaders.append(loader)
        return loaders

    def get_paths(self) -> set[str]:
        """Obtains a set of all template directories."""
        paths: set[str] = set()
        for loader in self.get_loaders():
            with contextlib.suppress(ImportError, AttributeError, TypeError):
                module = import_module(loader.__module__)
                get_template_sources = getattr(module, "get_template_sources", None)
                if get_template_sources is None:
                    get_template_sources = loader.get_template_sources
                paths.update(smart_str(origin) for origin in get_template_sources(""))
        return paths

    def get_templates(self, paths: set[str]) -> set[str]:
        """Obtains a set of all HTML template paths."""
        extensions = [".html"]
        templates: set[str] = set()
        for path in paths:
            for root, _, files in os.walk(path, followlinks=False):
                templates.update(
                    os.path.join(root, name)
                    for name in files
                    if not name.startswith(".") and any(fnmatch(name, f"*{glob}") for glob in extensions)
                )

        return templates

    def get_components(self, templates: set[str]) -> set[str]:
        """Obtains a set of all ReactPy components by parsing HTML templates."""
        components: set[str] = set()
        for template in templates:
            with contextlib.suppress(Exception), open(template, encoding="utf-8") as template_file:
                clean_template = COMMENT_REGEX.sub("", template_file.read())
                regex_iterable = COMPONENT_REGEX.finditer(clean_template)
                new_components: list[str] = []
                for match in regex_iterable:
                    new_components.append(match.group("path").replace('"', "").replace("'", ""))
                    offline_path = match.group("offline_path")
                    if offline_path:
                        new_components.append(offline_path.replace('"', "").replace("'", ""))
                components.update(new_components)
        if not components:
            _logger.warning(
                "\033[93m"
                "ReactPy did not find any components! "
                "You are either not using any ReactPy components, "
                "using the template tag incorrectly, "
                "or your HTML templates are not registered with Django."
                "\033[0m"
            )
        return components

    def register_components(self, components: set[str]) -> None:
        """Registers all ReactPy components in an iterable."""
        if components:
            _logger.debug("Auto-detected ReactPy root components:")
        for component in components:
            try:
                _logger.debug("\t+ %s", component)
                register_component(component)
            except Exception:
                _logger.exception(
                    "\033[91m"
                    "ReactPy failed to register component '%s'!\n"
                    "This component path may not be valid, "
                    "or an exception may have occurred while importing.\n"
                    "See the traceback below for more information."
                    "\033[0m",
                    component,
                )


def generate_obj_name(obj: Any) -> str:
    """Makes a best effort to create a name for an object.
    Useful for JSON serialization of Python objects."""

    # First attempt: Create a dotted path by inspecting dunder methods
    if hasattr(obj, "__module__"):
        if hasattr(obj, "__name__"):
            return f"{obj.__module__}.{obj.__name__}"
        if hasattr(obj, "__class__") and hasattr(obj.__class__, "__name__"):
            return f"{obj.__module__}.{obj.__class__.__name__}"

    # Second attempt: String representation
    with contextlib.suppress(Exception):
        return str(obj)

    # Fallback: Empty string
    return ""


def django_query_postprocessor(
    data: QuerySet | Model, many_to_many: bool = True, many_to_one: bool = True
) -> QuerySet | Model:
    """Recursively fetch all fields within a `Model` or `QuerySet` to ensure they are not performed lazily.

    Behavior can be modified through `postprocessor_kwargs` within your `use_query` hook.

    Args:
        data: The `Model` or `QuerySet` to recursively fetch fields from.

    Keyword Args:
        many_to_many: Whether or not to recursively fetch `ManyToManyField` relationships.
        many_to_one: Whether or not to recursively fetch `ForeignKey` relationships.

    Returns:
        The `Model` or `QuerySet` with all fields fetched.
    """

    # `QuerySet`, which is an iterable containing `Model`/`QuerySet` objects.
    if isinstance(data, QuerySet):
        for model in data:
            django_query_postprocessor(
                model,
                many_to_many=many_to_many,
                many_to_one=many_to_one,
            )

    # `Model` instances
    elif isinstance(data, Model):
        prefetch_fields: list[str] = []
        for field in data._meta.get_fields():
            # Force the query to execute
            getattr(data, field.name, None)

            if many_to_one and type(field) == ManyToOneRel:
                prefetch_fields.append(field.related_name or f"{field.name}_set")

            elif many_to_many and isinstance(field, ManyToManyField):
                prefetch_fields.append(field.name)

        if prefetch_fields:
            prefetch_related_objects([data], *prefetch_fields)
            for field_str in prefetch_fields:
                django_query_postprocessor(
                    getattr(data, field_str).get_queryset(),
                    many_to_many=many_to_many,
                    many_to_one=many_to_one,
                )

    # Unrecognized type
    else:
        msg = (
            f"Django query postprocessor expected a Model or QuerySet, got {data!r}.\n"
            "One of the following may have occurred:\n"
            "  - You are using a non-Django ORM.\n"
            "  - You are attempting to use `use_query` to fetch non-ORM data.\n\n"
            "If these situations apply, you may want to disable the postprocessor."
        )
        raise TypeError(msg)

    return data


def validate_component_args(func, *args, **kwargs):
    """
    Validate whether a set of args/kwargs would work on the given component.

    Raises `ComponentParamError` if the args/kwargs are invalid.
    """
    signature = inspect.signature(func)

    try:
        signature.bind(*args, **kwargs)
    except TypeError as e:
        name = generate_obj_name(func)
        msg = f"Invalid args for '{name}'. {str(e).capitalize()}."
        raise ComponentParamError(msg) from e


def create_cache_key(*args):
    """Creates a cache key string that starts with `reactpy_django` contains
    all *args separated by `:`."""

    if not args:
        msg = "At least one argument is required to create a cache key."
        raise ValueError(msg)

    return f"reactpy_django:{':'.join(str(arg) for arg in args)}"


class SyncLayout(Layout):
    """Sync adapter for ReactPy's `Layout`. Allows it to be used in Django template tags.
    This can be removed when Django supports async template tags.
    """

    def __enter__(self):
        async_to_sync(self.__aenter__)()
        return self

    def __exit__(self, *_):
        async_to_sync(self.__aexit__)(*_)

    def render(self):
        return async_to_sync(super().render)()


def get_pk(model):
    """Returns the value of the primary key for a Django model."""
    return getattr(model, model._meta.pk.name)


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in {"y", "yes", "t", "true", "on", "1"}:
        return 1
    if val in {"n", "no", "f", "false", "off", "0"}:
        return 0
    msg = f"invalid truth value {val}"
    raise ValueError(msg)


def prerender_component(
    user_component: ComponentConstructor,
    args: Sequence,
    kwargs: Mapping,
    uuid: str | UUID,
    request: HttpRequest,
) -> str:
    """Prerenders a ReactPy component and returns the HTML string."""
    search = request.GET.urlencode()
    scope = getattr(request, "scope", {})
    scope["reactpy"] = {"id": str(uuid)}

    with SyncLayout(
        ConnectionContext(
            user_component(*args, **kwargs),
            value=Connection(
                scope=scope,
                location=Location(pathname=request.path, search=f"?{search}" if search else ""),
                carrier=request,
            ),
        )
    ) as layout:
        vdom_tree = layout.render()["model"]

    return vdom_to_html(vdom_tree)


def vdom_or_component_to_string(
    vdom_or_component: Any, request: HttpRequest | None = None, uuid: str | None = None
) -> str:
    """Converts a VdomDict or component to an HTML string. If a string is provided instead, it will be
    automatically returned."""
    if isinstance(vdom_or_component, dict):
        return vdom_to_html(vdom_or_component)

    if hasattr(vdom_or_component, "render"):
        if not request:
            request = HttpRequest()
            request.method = "GET"
        if not uuid:
            uuid = uuid4().hex
        return prerender_component(vdom_or_component, [], {}, uuid, request)

    if isinstance(vdom_or_component, str):
        return vdom_or_component

    msg = f"Invalid type for vdom_or_component: {type(vdom_or_component)}. Expected a VdomDict, component, or string."
    raise ValueError(msg)


def render_pyscript_template(file_paths: Sequence[str], uuid: str, root: str):
    """Inserts the user's code into the PyScript template using pattern matching."""
    from django.core.cache import caches

    from reactpy_django.config import REACTPY_CACHE

    # Create a valid PyScript executor by replacing the template values
    executor = PYSCRIPT_COMPONENT_TEMPLATE.replace("UUID", uuid)
    executor = executor.replace("return root()", f"return {root}()")

    # Fetch the user's PyScript code
    all_file_contents: list[str] = []
    for file_path in file_paths:
        # Try to get user code from cache
        cache_key = create_cache_key("pyscript", file_path)
        last_modified_time = os.stat(file_path).st_mtime
        file_contents: str = caches[REACTPY_CACHE].get(cache_key, version=int(last_modified_time))
        if file_contents:
            all_file_contents.append(file_contents)

        # If not cached, read from file system
        else:
            file_contents = Path(file_path).read_text(encoding="utf-8").strip()
            all_file_contents.append(file_contents)
            caches[REACTPY_CACHE].set(cache_key, file_contents, version=int(last_modified_time))

    # Prepare the PyScript code block
    user_code = "\n".join(all_file_contents)  # Combine all user code
    user_code = user_code.replace("\t", "    ")  # Normalize the text
    user_code = textwrap.indent(user_code, "    ")  # Add indentation to match template

    # Insert the user code into the PyScript template
    return executor.replace("    def root(): ...", user_code)


def extend_pyscript_config(extra_py: Sequence, extra_js: dict | str, config: dict | str) -> str:
    """Extends ReactPy's default PyScript config with user provided values."""
    # Lazily set up the initial config in to wait for Django's static file system
    if not PYSCRIPT_DEFAULT_CONFIG:
        PYSCRIPT_DEFAULT_CONFIG.update({
            "packages": [
                f"reactpy=={reactpy.__version__}",
                f"jsonpointer=={jsonpointer.__version__}",
                "ssl",
            ],
            "js_modules": {"main": {static("reactpy_django/morphdom/morphdom-esm.js"): "morphdom"}},
        })

    # Extend the Python dependency list
    pyscript_config = deepcopy(PYSCRIPT_DEFAULT_CONFIG)
    pyscript_config["packages"].extend(extra_py)

    # Extend the JavaScript dependency list
    if extra_js and isinstance(extra_js, str):
        pyscript_config["js_modules"]["main"].update(json.loads(extra_js))
    elif extra_js and isinstance(extra_js, dict):
        pyscript_config["js_modules"]["main"].update(extra_py)

    # Update the config
    if config and isinstance(config, str):
        pyscript_config.update(json.loads(config))
    elif config and isinstance(config, dict):
        pyscript_config.update(config)
    return orjson.dumps(pyscript_config).decode("utf-8")


def save_component_params(args, kwargs, uuid) -> None:
    """Saves the component parameters to the database.
    This is used within our template tag in order to propogate
    the parameters between the HTTP and WebSocket stack."""
    from reactpy_django import models
    from reactpy_django.types import ComponentParams

    params = ComponentParams(args, kwargs)
    model = models.ComponentSession(uuid=uuid, params=dill.dumps(params))
    model.full_clean()
    model.save()


def validate_host(host: str) -> None:
    """Validates the host string to ensure it does not contain a protocol."""
    if "://" in host:
        protocol = host.split("://")[0]
        msg = f"Invalid host provided to component. Contains a protocol '{protocol}://'."
        _logger.error(msg)
        raise InvalidHostError(msg)


class FileAsyncIterator:
    """Async iterator that yields chunks of data from the provided async file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    async def __aiter__(self):
        file_opened = False
        try:
            file_handle = FILE_ASYNC_ITERATOR_THREAD.submit(open, self.file_path, "rb").result()
            file_opened = True
            while True:
                chunk = FILE_ASYNC_ITERATOR_THREAD.submit(file_handle.read, 8192).result()
                if not chunk:
                    break
                yield chunk
        finally:
            if file_opened:
                file_handle.close()
