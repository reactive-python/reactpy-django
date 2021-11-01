import logging
import os
import re
from fnmatch import fnmatch
from importlib import import_module
from typing import Set

from django.template import engines
from django.utils.encoding import smart_str

from django_idom.config import IDOM_REGISTERED_COMPONENTS


COMPONENT_REGEX = re.compile(r"{% *idom_component ((\"[^\"']*\")|('[^\"']*')).*?%}")
_logger = logging.getLogger(__name__)


def _register_component(full_component_name: str) -> None:
    if full_component_name in IDOM_REGISTERED_COMPONENTS:
        return

    module_name, component_name = full_component_name.rsplit(".", 1)

    try:
        module = import_module(module_name)
    except ImportError as error:
        raise RuntimeError(
            f"Failed to import {module_name!r} while loading {component_name!r}"
        ) from error

    try:
        component = getattr(module, component_name)
    except AttributeError as error:
        raise RuntimeError(
            f"Module {module_name!r} has no component named {component_name!r}"
        ) from error

    IDOM_REGISTERED_COMPONENTS[full_component_name] = component


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
                    e.engine.get_template_loaders(e.engine.loaders)
                )
        loaders = []
        for loader in template_source_loaders:
            if hasattr(loader, "loaders"):
                loaders.extend(loader.loaders)
            else:
                loaders.append(loader)
        return loaders

    def _get_paths(self) -> Set:
        """Obtains a set of all template directories."""
        paths = set()
        for loader in self._get_loaders():
            try:
                module = import_module(loader.__module__)
                get_template_sources = getattr(module, "get_template_sources", None)
                if get_template_sources is None:
                    get_template_sources = loader.get_template_sources
                paths.update(smart_str(origin) for origin in get_template_sources(""))
            except (ImportError, AttributeError, TypeError):
                pass

        return paths

    def _get_templates(self, paths: Set) -> Set:
        """Obtains a set of all HTML template paths."""
        extensions = [".html"]
        templates = set()
        for path in paths:
            for root, dirs, files in os.walk(path, followlinks=False):
                templates.update(
                    os.path.join(root, name)
                    for name in files
                    if not name.startswith(".")
                    and any(fnmatch(name, "*%s" % glob) for glob in extensions)
                )

        return templates

    def _get_components(self, templates: Set) -> Set:
        """Obtains a set of all IDOM components by parsing HTML templates."""
        components = set()
        for template in templates:
            try:
                with open(template, "r", encoding="utf-8") as template_file:
                    match = COMPONENT_REGEX.findall(template_file.read())
                    if not match:
                        continue
                    components.update(
                        [group[0].replace('"', "").replace("'", "") for group in match]
                    )
            except Exception:
                pass

        return components

    def _register_components(self, components: Set) -> None:
        """Registers all IDOM components in an iterable."""
        for component in components:
            try:
                _register_component(component)
                _logger.info("IDOM has registered component %s", component)
            except Exception:
                _logger.warning("IDOM failed to register component %s", component)
