"""Code within this module is designed to be run directly by PyScript, and is not
intended to be run in a Django environment.

Our template tag performs string substitutions to turn this file into valid PyScript."""

import asyncio

import js
from jsonpointer import set_pointer
from pyodide.ffi.wrappers import add_event_listener
from reactpy.core.layout import Layout


# User component is inserted below by regex replacement
def user_workspace_UUID():
    """Encapsulate the user's code with a completely unique function (workspace)
    to prevent overlapping imports and variable names between different components."""

    def root(): ...

    return root()


# ReactPy layout rendering starts here
class LayoutManagerUUID:
    """Encapsulate an entire layout manager with a completely unique class to prevent
    rendering bugs caused by the PyScript global interpreter."""

    @staticmethod
    def apply_update(update, root_model):
        if update["path"]:
            set_pointer(root_model, update["path"], update["model"])
        else:
            root_model.update(update["model"])

    def render(self, layout, model):
        container = js.document.getElementById("pyscript-UUID")
        container.innerHTML = ""
        self.build_element_tree(layout, container, model)

    def build_element_tree(self, layout, parent, model):
        if isinstance(model, str):
            parent.appendChild(js.document.createTextNode(model))
        elif isinstance(model, dict):
            if not model["tagName"]:
                for child in model.get("children", []):
                    self.build_element_tree(layout, parent, child)
                return
            tag = model["tagName"]
            attributes = model.get("attributes", {})
            children = model.get("children", [])
            element = js.document.createElement(tag)
            for key, value in attributes.items():
                if key == "style":
                    for style_key, style_value in value.items():
                        setattr(element.style, style_key, style_value)
                else:
                    element.setAttribute(key, value)
            for event_name, event_handler_model in model.get(
                "eventHandlers", {}
            ).items():
                self.create_event_handler(
                    layout, element, event_name, event_handler_model
                )
            for child in children:
                self.build_element_tree(layout, element, child)
            parent.appendChild(element)
        else:
            raise ValueError(f"Unknown model type: {type(model)}")

    @staticmethod
    def create_event_handler(layout, element, event_name, event_handler_model):
        target = event_handler_model["target"]

        def event_handler(*args):
            asyncio.create_task(
                layout.deliver({"type": "layout-event", "target": target, "data": args})
            )

        event_name = event_name.lstrip("on_").lower().replace("_", "")
        add_event_listener(element, event_name, event_handler)

    async def run(self):
        root_model = {}
        async with Layout(user_workspace_UUID()) as layout:
            while True:
                update = await layout.render()
                self.apply_update(update, root_model)
                self.render(layout, root_model)


# PyScript allows top-level await, which allows us to not throw errors on components
# that terminate early (such as hook-less components)
await LayoutManagerUUID().run()  # noqa: F704
