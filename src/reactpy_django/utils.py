from __future__ import annotations

import contextlib
import inspect
import logging
import os
import re
from datetime import timedelta
from fnmatch import fnmatch
from importlib import import_module
from inspect import iscoroutinefunction
from typing import Any, Callable, Sequence

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.db.models import ManyToManyField, ManyToOneRel, prefetch_related_objects
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template import engines
from django.utils import timezone
from django.utils.encoding import smart_str
from django.views import View
from reactpy.core.layout import Layout
from reactpy.types import ComponentConstructor

from reactpy_django.exceptions import ComponentDoesNotExistError, ComponentParamError

_logger = logging.getLogger(__name__)
_component_tag = r"(?P<tag>component)"
_component_path = r"(?P<path>\"[^\"'\s]+\"|'[^\"'\s]+')"
_component_kwargs = r"(?P<kwargs>[\s\S]*?)"
COMMENT_REGEX = re.compile(r"<!--[\s\S]*?-->")
COMPONENT_REGEX = re.compile(
    r"{%\s*"
    + _component_tag
    + r"\s*"
    + _component_path
    + r"\s*"
    + _component_kwargs
    + r"\s*%}"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


async def render_view(
    view: Callable | View,
    request: HttpRequest,
    args: Sequence,
    kwargs: dict,
) -> HttpResponse:
    """Ingests a Django view (class or function) and returns an HTTP response object."""
    # Render Check 1: Async function view
    if iscoroutinefunction(view) and callable(view):
        response = await view(request, *args, **kwargs)

    # Render Check 2: Async class view
    elif getattr(view, "view_is_async", False):
        # django-stubs does not support async views yet, so we have to ignore types here
        view_or_template_view = await view.as_view()(request, *args, **kwargs)  # type: ignore
        if getattr(view_or_template_view, "render", None):  # TemplateView
            response = await view_or_template_view.render()
        else:  # View
            response = view_or_template_view

    # Render Check 3: Sync class view
    elif getattr(view, "as_view", None):
        # MyPy does not know how to properly interpret this as a `View` type
        # And `isinstance(view, View)` does not work due to some weird Django internal shenanigans
        async_cbv = database_sync_to_async(view.as_view(), thread_sensitive=False)  # type: ignore
        view_or_template_view = await async_cbv(request, *args, **kwargs)
        if getattr(view_or_template_view, "render", None):  # TemplateView
            response = await database_sync_to_async(
                view_or_template_view.render, thread_sensitive=False
            )()
        else:  # View
            response = view_or_template_view

    # Render Check 4: Sync function view
    else:
        response = await database_sync_to_async(view, thread_sensitive=False)(
            request, *args, **kwargs
        )

    return response


def register_component(dotted_path: str) -> ComponentConstructor:
    """Adds a component to the list of known registered components."""
    from reactpy_django.config import (
        REACTPY_FAILED_COMPONENTS,
        REACTPY_REGISTERED_COMPONENTS,
    )

    if dotted_path in REACTPY_REGISTERED_COMPONENTS:
        return REACTPY_REGISTERED_COMPONENTS[dotted_path]

    try:
        REACTPY_REGISTERED_COMPONENTS[dotted_path] = import_dotted_path(dotted_path)
    except AttributeError as e:
        REACTPY_FAILED_COMPONENTS.add(dotted_path)
        raise ComponentDoesNotExistError(
            f"Error while fetching '{dotted_path}'. {(str(e).capitalize())}."
        ) from e
    return REACTPY_REGISTERED_COMPONENTS[dotted_path]


def import_dotted_path(dotted_path: str) -> Callable:
    """Imports a dotted path and returns the callable."""
    module_name, component_name = dotted_path.rsplit(".", 1)

    try:
        module = import_module(module_name)
    except ImportError as error:
        raise RuntimeError(
            f"Failed to import {module_name!r} while loading {component_name!r}"
        ) from error

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
                template_source_loaders.extend(
                    e.engine.get_template_loaders(e.engine.loaders)
                )
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
                    if not name.startswith(".")
                    and any(fnmatch(name, f"*{glob}") for glob in extensions)
                )

        return templates

    def get_components(self, templates: set[str]) -> set[str]:
        """Obtains a set of all ReactPy components by parsing HTML templates."""
        components: set[str] = set()
        for template in templates:
            with contextlib.suppress(Exception):
                with open(template, "r", encoding="utf-8") as template_file:
                    clean_template = COMMENT_REGEX.sub("", template_file.read())
                    regex_iterable = COMPONENT_REGEX.finditer(clean_template)
                    component_paths = [
                        match.group("path").replace('"', "").replace("'", "")
                        for match in regex_iterable
                    ]
                    components.update(component_paths)
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


def generate_obj_name(object: Any) -> str:
    """Makes a best effort to create a name for an object.
    Useful for JSON serialization of Python objects."""
    if hasattr(object, "__module__"):
        if hasattr(object, "__name__"):
            return f"{object.__module__}.{object.__name__}"
        if hasattr(object, "__class__"):
            return f"{object.__module__}.{object.__class__.__name__}"

    with contextlib.suppress(Exception):
        return str(object)
    return ""


def django_query_postprocessor(
    data: QuerySet | Model, many_to_many: bool = True, many_to_one: bool = True
) -> QuerySet | Model:
    """Recursively fetch all fields within a `Model` or `QuerySet` to ensure they are not performed lazily.

    Behaviors can be modified through `QueryOptions` within your `use_query` hook.

    Args:
        data: The `Model` or `QuerySet` to recursively fetch fields from.

    Keyword Args:
        many_to_many: Whether or not to recursively fetch `ManyToManyField` relationships.
        many_to_one: Whether or not to recursively fetch `ForeignKey` relationships.

    Returns:
        The `Model` or `QuerySet` with all fields fetched.
    """

    # `QuerySet`, which is an iterable of `Model`/`QuerySet` instances
    # https://github.com/typeddjango/django-stubs/issues/704
    if isinstance(data, QuerySet):  # type: ignore[misc]
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

            if many_to_one and type(field) == ManyToOneRel:  # noqa: #E721
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
        raise TypeError(
            f"Django query postprocessor expected a Model or QuerySet, got {data!r}.\n"
            "One of the following may have occurred:\n"
            "  - You are using a non-Django ORM.\n"
            "  - You are attempting to use `use_query` to fetch non-ORM data.\n\n"
            "If these situations seem correct, you may want to consider disabling the postprocessor via `QueryOptions`."
        )

    return data


def validate_component_args(func, *args, **kwargs):
    """
    Validate whether a set of args/kwargs would work on the given function.

    Raises `ComponentParamError` if the args/kwargs are invalid.
    """
    signature = inspect.signature(func)

    try:
        signature.bind(*args, **kwargs)
    except TypeError as e:
        name = generate_obj_name(func)
        raise ComponentParamError(
            f"Invalid args for '{name}'. {str(e).capitalize()}."
        ) from e


def create_cache_key(*args):
    """Creates a cache key string that starts with `reactpy_django` contains
    all *args separated by `:`."""

    if not args:
        raise ValueError("At least one argument is required to create a cache key.")

    return f"reactpy_django:{':'.join(str(arg) for arg in args)}"


def delete_expired_sessions(immediate: bool = False):
    """Deletes expired component sessions from the database.
    As a performance optimization, this is only run once every REACTPY_SESSION_MAX_AGE seconds.
    """
    from .config import REACTPY_DEBUG_MODE, REACTPY_SESSION_MAX_AGE
    from .models import ComponentSession, Config

    config = Config.load()
    start_time = timezone.now()
    cleaned_at = config.cleaned_at
    clean_needed_by = cleaned_at + timedelta(seconds=REACTPY_SESSION_MAX_AGE)

    # Delete expired component parameters
    if immediate or timezone.now() >= clean_needed_by:
        expiration_date = timezone.now() - timedelta(seconds=REACTPY_SESSION_MAX_AGE)
        ComponentSession.objects.filter(last_accessed__lte=expiration_date).delete()
        config.cleaned_at = timezone.now()
        config.save()

    # Check if cleaning took abnormally long
    if REACTPY_DEBUG_MODE:
        clean_duration = timezone.now() - start_time
        if clean_duration.total_seconds() > 1:
            _logger.warning(
                "ReactPy has taken %s seconds to clean up expired component sessions. "
                "This may indicate a performance issue with your system, cache, or database.",
                clean_duration.total_seconds(),
            )


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
