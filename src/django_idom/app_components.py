import logging
from importlib import import_module
from typing import Dict

from django.conf import settings
from idom.core.proto import ComponentConstructor


logger = logging.getLogger(__name__)
_LOADED_COMPONENTS: Dict[str, ComponentConstructor] = {}


def get_component(name: str) -> ComponentConstructor:
    return _LOADED_COMPONENTS[name]


def has_component(name: str) -> bool:
    return name in _LOADED_COMPONENTS


for app_mod_name in settings.INSTALLED_APPS:
    idom_mod_name = f"{app_mod_name}.idom"

    try:
        idom_mod = import_module(idom_mod_name)
    except ImportError:
        logger.debug(f"Skipping {idom_mod_name!r} - does not exist")
        continue

    if not hasattr(idom_mod, "components"):
        logger.warning(
            f"'django_idom' expected module {idom_mod_name!r} to have an "
            "'components' attribute that lists its publically available components."
        )
        continue

    for component_constructor in idom_mod.components:
        if not callable(component_constructor):
            logger.warning(
                f"{component_constructor} is not a callable component constructor"
            )
            continue

        try:
            component_name = getattr(component_constructor, "__name__")
        except AttributeError:
            logger.warning(
                f"Component constructor {component_constructor} has not attribute '__name__'"
            )
            continue

        _LOADED_COMPONENTS[f"{app_mod_name}.{component_name}"] = component_constructor
