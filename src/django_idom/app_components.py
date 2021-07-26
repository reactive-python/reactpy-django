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

    if not hasattr(idom_mod, "__all__"):
        logger.warning(
            f"'django_idom' expected module {idom_mod_name!r} to have an "
            "'__all__' attribute that lists its publically available components."
        )
        continue

    for component_name in idom_mod.__all__:
        try:
            component_constructor = getattr(idom_mod, component_name)
        except AttributeError:
            logger.warning(
                f"Module {idom_mod_name!r} has no attribute {component_name!r}"
            )
            continue

        if not callable(component_constructor):
            logger.warning(f"'{idom_mod_name}.{component_name}' is not a component")
            continue

        _LOADED_COMPONENTS[f"{app_mod_name}.{component_name}"] = component_constructor
