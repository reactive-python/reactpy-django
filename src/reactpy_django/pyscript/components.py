from __future__ import annotations

from uuid import uuid4

from reactpy import component, hooks, html
from reactpy.types import ComponentType, VdomDict

from reactpy_django.html import pyscript
from reactpy_django.pyscript.utils import render_pyscript_template
from reactpy_django.utils import vdom_or_component_to_string


@component
def _pyscript_component(
    *file_paths: str,
    initial: str | VdomDict | ComponentType = "",
    root: str = "root",
):
    rendered, set_rendered = hooks.use_state(False)
    uuid_ref = hooks.use_ref(uuid4().hex.replace("-", ""))
    uuid = uuid_ref.current
    initial = vdom_or_component_to_string(initial, uuid=uuid)
    executor = render_pyscript_template(file_paths, uuid, root)

    if not rendered:
        # FIXME: This is needed to properly re-render PyScript during a WebSocket
        # disconnection / reconnection. There may be a better way to do this in the future.
        set_rendered(True)
        return None

    return html._(
        html.div(
            {"id": f"pyscript-{uuid}", "className": "pyscript", "data-uuid": uuid},
            initial,
        ),
        pyscript({"async": ""}, executor),
    )
