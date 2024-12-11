from __future__ import annotations

import json
import os
import textwrap
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any

import jsonpointer
import orjson
import reactpy
from django.templatetags.static import static

from reactpy_django.utils import create_cache_key

if TYPE_CHECKING:
    from collections.abc import Sequence


PYSCRIPT_COMPONENT_TEMPLATE = (Path(__file__).parent / "component_template.py").read_text(encoding="utf-8")
PYSCRIPT_LAYOUT_HANDLER = (Path(__file__).parent / "layout_handler.py").read_text(encoding="utf-8")
PYSCRIPT_DEFAULT_CONFIG: dict[str, Any] = {}


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
