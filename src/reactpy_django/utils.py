from __future__ import annotations

import contextlib
import inspect
import logging
import os
import re
from datetime import datetime, timedelta
from fnmatch import fnmatch
from importlib import import_module
from inspect import iscoroutinefunction
from typing import Any, Callable, Sequence

from channels.db import database_sync_to_async
from django.core.cache import caches
from django.db.models import ManyToManyField, ManyToOneRel, prefetch_related_objects
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template import engines
from django.utils import timezone
from django.utils.encoding import smart_str
from django.views import View


_logger = logging.getLogger(__name__)
_component_tag = r"(?P<tag>component)"
_component_path = r"(?P<path>(\"[^\"'\s]+\")|('[^\"'\s]+'))"
_component_kwargs = r"(?P<kwargs>(.*?|\s*?)*)"
COMMENT_REGEX = re.compile(r"(<!--)(.|\s)*?(-->)")
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


def _register_component(dotted_path: str) -> Callable:
    """Adds a component to the mapping of registered components.
    This should only be called on startup to maintain synchronization during mulitprocessing.
    """
    from reactpy_django.config import REACTPY_REGISTERED_COMPONENTS

    if dotted_path in REACTPY_REGISTERED_COMPONENTS:
        return REACTPY_REGISTERED_COMPONENTS[dotted_path]

    REACTPY_REGISTERED_COMPONENTS[dotted_path] = import_dotted_path(dotted_path)
    _logger.debug("ReactPy has registered component %s", dotted_path)
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


class ComponentPreloader:
    """Preloads all ReactPy components found within Django templates.
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
        for component in components:
            try:
                _logger.info("ReactPy preloader has detected component %s", component)
                _register_component(component)
            except Exception:
                _logger.exception(
                    "\033[91m"
                    "ReactPy failed to register component '%s'! "
                    "This component path may not be valid, "
                    "or an exception may have occurred while importing."
                    "\033[0m",
                    component,
                )


def generate_obj_name(object: Any) -> str | None:
    """Makes a best effort to create a name for an object.
    Useful for JSON serialization of Python objects."""
    if hasattr(object, "__module__"):
        if hasattr(object, "__name__"):
            return f"{object.__module__}.{object.__name__}"
        if hasattr(object, "__class__"):
            return f"{object.__module__}.{object.__class__.__name__}"
    return None


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
        raise TypeError(
            f"Django query postprocessor expected a Model or QuerySet, got {data!r}.\n"
            "One of the following may have occurred:\n"
            "  - You are using a non-Django ORM.\n"
            "  - You are attempting to use `use_query` to fetch non-ORM data.\n\n"
            "If these situations seem correct, you may want to consider disabling the postprocessor via `QueryOptions`."
        )

    return data


def func_has_params(func: Callable, *args, **kwargs) -> bool:
    """Checks if a function has any args or kwarg parameters.

    Can optionally validate whether a set of args/kwargs would work on the given function.
    """
    signature = inspect.signature(func)

    # Check if the function has any args/kwargs
    if not args and not kwargs:
        return str(signature) != "()"

    # Check if the function has the given args/kwargs
    signature.bind(*args, **kwargs)
    return True


def create_cache_key(*args):
    """Creates a cache key string that starts with `reactpy_django` contains
    all *args separated by `:`."""

    if not args:
        raise ValueError("At least one argument is required to create a cache key.")

    return f"reactpy_django:{':'.join(str(arg) for arg in args)}"


def db_cleanup(immediate: bool = False):
    """Deletes expired component sessions from the database.
    This function may be expanded in the future to include additional cleanup tasks."""
    from .config import (
        REACTPY_CACHE,
        REACTPY_DATABASE,
        REACTPY_DEBUG_MODE,
        REACTPY_RECONNECT_MAX,
    )
    from .models import ComponentSession

    clean_started_at = datetime.now()
    cache_key: str = create_cache_key("last_cleaned")
    now_str: str = datetime.strftime(timezone.now(), DATE_FORMAT)
    cleaned_at_str: str = caches[REACTPY_CACHE].get(cache_key)
    cleaned_at: datetime = timezone.make_aware(
        datetime.strptime(cleaned_at_str or now_str, DATE_FORMAT)
    )
    clean_needed_by = cleaned_at + timedelta(seconds=REACTPY_RECONNECT_MAX)
    expires_by: datetime = timezone.now() - timedelta(seconds=REACTPY_RECONNECT_MAX)

    # Component params exist in the DB, but we don't know when they were last cleaned
    if not cleaned_at_str and ComponentSession.objects.using(REACTPY_DATABASE).all():
        _logger.warning(
            "ReactPy has detected component sessions in the database, "
            "but no timestamp was found in cache. This may indicate that "
            "the cache has been cleared."
        )

    # Delete expired component parameters
    # Use timestamps in cache (`cleaned_at_str`) as a no-dependency rate limiter
    if immediate or not cleaned_at_str or timezone.now() >= clean_needed_by:
        ComponentSession.objects.using(REACTPY_DATABASE).filter(
            last_accessed__lte=expires_by
        ).delete()
        caches[REACTPY_CACHE].set(cache_key, now_str, timeout=None)

    # Check if cleaning took abnormally long
    clean_duration = datetime.now() - clean_started_at
    if REACTPY_DEBUG_MODE and clean_duration.total_seconds() > 1:
        _logger.warning(
            "ReactPy has taken %s seconds to clean up expired component sessions. "
            "This may indicate a performance issue with your system, cache, or database.",
            clean_duration.total_seconds(),
        )
