import logging
from importlib import import_module
from typing import Dict

from django.conf import settings
from idom.core.proto import ComponentConstructor

from .app_settings import IDOM_IGNORE_INSTALLED_APPS


_logger = logging.getLogger(__name__)
_LOADED_COMPONENTS: Dict[str, ComponentConstructor] = {}


def get_component(name: str) -> ComponentConstructor:
    return _LOADED_COMPONENTS[name]


def has_component(name: str) -> bool:
    return name in _LOADED_COMPONENTS


for app_mod_name in settings.INSTALLED_APPS:
    if app_mod_name in IDOM_IGNORE_INSTALLED_APPS:
        _logger.debug(f"{app_mod_name!r} skipped by IDOM_IGNORE_INSTALLED_APPS")
        continue

    idom_mod_name = f"{app_mod_name}.idom"

    try:
        idom_mod = import_module(idom_mod_name)
    except ImportError:
        _logger.debug(f"Skipping {idom_mod_name!r} - does not exist")
        continue

    if not hasattr(idom_mod, "components"):
        _logger.warning(
            f"'django_idom' expected module {idom_mod_name!r} to have an "
            "'components' attribute that lists its publically available components."
        )
        continue

    for component_value in idom_mod.components:
        if isinstance(component_value, str):
            component_name = component_value
            component_constructor = getattr(idom_mod, component_name)
        else:
            component_constructor = component_value

            try:
                component_name = getattr(component_constructor, "__name__")
            except AttributeError:
                raise ValueError(
                    f"Component constructor {component_constructor} has no attribute '__name__'"
                )

        if not callable(component_constructor):
            raise ValueError(
                f"{component_constructor} is not a callable component constructor"
            )

        full_component_name = f"{app_mod_name}.{component_name}"

        if full_component_name in _LOADED_COMPONENTS:
            raise ValueError(
                f"Component constructor named {component_name!r} has already been "
                f"declared by the app {app_mod_name!r}"
            )

        _LOADED_COMPONENTS[f"{app_mod_name}.{component_name}"] = component_constructor
