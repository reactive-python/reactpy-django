from __future__ import annotations

import contextlib
import logging
import os
import re
from fnmatch import fnmatch
from importlib import import_module
from inspect import iscoroutinefunction
from typing import Any, Callable, Sequence

from channels.db import database_sync_to_async
from django.http import HttpRequest, HttpResponse
from django.template import engines
from django.utils.encoding import smart_str
from django.views import View

from django_idom.config import IDOM_REGISTERED_COMPONENTS


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
        async_cbv = database_sync_to_async(view.as_view())  # type: ignore
        view_or_template_view = await async_cbv(request, *args, **kwargs)
        if getattr(view_or_template_view, "render", None):  # TemplateView
            response = await database_sync_to_async(view_or_template_view.render)()
        else:  # View
            response = view_or_template_view

    # Render Check 4: Sync function view
    else:
        response = await database_sync_to_async(view)(request, *args, **kwargs)

    return response


def _register_component(dotted_path: str) -> None:
    if dotted_path in IDOM_REGISTERED_COMPONENTS:
        return

    IDOM_REGISTERED_COMPONENTS[dotted_path] = _import_dotted_path(dotted_path)
    _logger.debug("IDOM has registered component %s", dotted_path)


def _import_dotted_path(dotted_path: str) -> Callable:
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
    def register_all(self):
        """Registers all IDOM components found within Django templates."""
        # Get all template folder paths
        paths = self._get_paths()
        # Get all HTML template files
        templates = self._get_templates(paths)
        # Get all components
        components = self._get_components(templates)
        # Register all components
        self._register_components(components)

    def _get_loaders(self):
        """Obtains currently configured template loaders."""
        template_source_loaders = []
        for e in engines.all():
            if hasattr(e, "engine"):
                template_source_loaders.extend(
                    e.engine.get_template_loaders(e.engine.loaders)  # type: ignore
                )
        loaders = []
        for loader in template_source_loaders:
            if hasattr(loader, "loaders"):
                loaders.extend(loader.loaders)
            else:
                loaders.append(loader)
        return loaders

    def _get_paths(self) -> set[str]:
        """Obtains a set of all template directories."""
        paths: set[str] = set()
        for loader in self._get_loaders():
            with contextlib.suppress(ImportError, AttributeError, TypeError):
                module = import_module(loader.__module__)
                get_template_sources = getattr(module, "get_template_sources", None)
                if get_template_sources is None:
                    get_template_sources = loader.get_template_sources
                paths.update(smart_str(origin) for origin in get_template_sources(""))
        return paths

    def _get_templates(self, paths: set[str]) -> set[str]:
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

    def _get_components(self, templates: set[str]) -> set[str]:
        """Obtains a set of all IDOM components by parsing HTML templates."""
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
                "IDOM did not find any components! "
                "You are either not using any IDOM components, "
                "using the template tag incorrectly, "
                "or your HTML templates are not registered with Django."
                "\033[0m"
            )
        return components

    def _register_components(self, components: set[str]) -> None:
        """Registers all IDOM components in an iterable."""
        for component in components:
            try:
                _logger.info("IDOM preloader has detected component %s", component)
                _register_component(component)
            except Exception:
                _logger.error(
                    "\033[91m"
                    "IDOM failed to register component '%s'! "
                    "This component path may not be valid, "
                    "or an exception may have occurred while importing."
                    "\033[0m",
                    component,
                )


def _generate_obj_name(object: Any) -> str | None:
    """Makes a best effort to create a name for an object.
    Useful for JSON serialization of Python objects."""
    if hasattr(object, "__module__"):
        if hasattr(object, "__name__"):
            return f"{object.__module__}.{object.__name__}"
        if hasattr(object, "__class__"):
            return f"{object.__module__}.{object.__class__.__name__}"
    return None
