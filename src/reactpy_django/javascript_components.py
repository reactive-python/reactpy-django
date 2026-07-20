from __future__ import annotations

from pathlib import Path

from reactpy import reactjs

HttpRequest = reactjs.component_from_file(
    Path(__file__).parent / "static" / "reactpy_django" / "index.js",
    "HttpRequest",
    name="reactpy-django",
)
