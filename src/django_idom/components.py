import inspect
from typing import Any, Optional

from idom.core.component import component as component_deco

from .config import IDOM_REGISTERED_COMPONENTS


def register_component(
    component: Optional[Any] = None,
    is_render_function: bool = True,
    module_name: Optional[str] = None,
) -> Any:
    module_name = module_name or _get_outer_frame_module_name()
    if module_name is None:
        raise ValueError("Could not infer module name - provide it explicitely")

    def setup(component: Any) -> Any:
        if is_render_function:
            component = component_deco(component)

        try:
            component_name = component.__name__
        except AttributeError:
            raise AttributeError("Component constructor must have a __name__ attribute")

        IDOM_REGISTERED_COMPONENTS[f"{module_name}.{component_name}"] = component

        return component

    if component is not None:
        return setup(component)
    else:
        return setup


def _get_outer_frame_module_name() -> Optional[str]:
    frame = inspect.currentframe()

    if frame is None:
        return None

    for i in range(2):
        frame = frame.f_back
        if frame is None:
            return None

    return frame.f_globals.get("__name__")
