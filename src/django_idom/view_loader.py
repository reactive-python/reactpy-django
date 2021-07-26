import logging
from importlib import import_module
from pathlib import Path
from typing import Dict

from django.conf import settings
from idom.core.proto import ComponentConstructor


ALL_VIEWS: Dict[str, ComponentConstructor] = {}
logger = logging.getLogger(__name__)

for app_name in settings.INSTALLED_APPS:
    app_mod = import_module(app_name)
    if not hasattr(app_mod, "idom"):
        continue

    for idom_view_path in Path(app_mod.__file__).iterdir():
        if idom_view_path.suffix == ".py" and idom_view_path.is_file():
            idom_view_mod_name = ".".join([app_name, "idom", idom_view_path.stem])
            idom_view_mod = import_module(idom_view_mod_name)

            if hasattr(idom_view_mod, "Root") and callable(idom_view_mod.Root):
                ALL_VIEWS[idom_view_mod_name] = idom_view_mod.Root
            else:
                logger.warning(
                    f"Expected module {idom_view_mod_name} to expose a 'Root' "
                    " attribute that is an IDOM component."
                )
