from __future__ import annotations

from pathlib import Path

from reactpy import web

HttpRequest = web.export(
    web.module_from_file("reactpy-django", file=Path(__file__).parent / "static" / "reactpy_django" / "client.js"),
    ("HttpRequest"),
)
