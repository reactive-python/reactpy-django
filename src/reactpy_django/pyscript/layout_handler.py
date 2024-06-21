import asyncio
from typing import Coroutine

import js
from jsonpointer import set_pointer
from pyodide.ffi.wrappers import add_event_listener
from reactpy.core.layout import Layout


class ReactPyLayoutHandler:
    """Encapsulate the entire layout handler with a class to prevent overlapping
    variable names between user code.

    This code is designed to be run directly by PyScript, and is not intended to be run
    in a standard Python environment.
    """

    def __init__(self, uuid):
        self.uuid = uuid

    @staticmethod
    def apply_update(update, root_model):
        if update["path"]:
            set_pointer(root_model, update["path"], update["model"])
        else:
            root_model.update(update["model"])

    def render(self, layout, model):
        container = js.document.getElementById(f"pyscript-{self.uuid}")
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

    @staticmethod
    def delete_old_workspaces():
        dom_workspaces = js.document.querySelectorAll(".pyscript")
        dom_uuids = {element.dataset.uuid for element in dom_workspaces}
        python_uuids = {
            value.split("_")[-1]
            for value in globals()
            if value.startswith("user_workspace_")
        }

        # Delete the workspace if it exists at the moment when we check
        for uuid in python_uuids - dom_uuids:
            task_name = f"task_{uuid}"
            if task_name in globals():
                task: asyncio.Task = globals()[task_name]
                task.cancel()
                del globals()[task_name]
            else:
                print(f"Warning: Could not auto delete PyScript task {task_name}")

            workspace_name = f"user_workspace_{uuid}"
            if workspace_name in globals():
                del globals()[workspace_name]
            else:
                print(
                    f"Warning: Could not auto delete PyScript workspace {workspace_name}"
                )

    async def run(self, workspace_function: Coroutine):
        self.delete_old_workspaces()
        root_model = {}

        async with Layout(workspace_function()) as layout:
            while True:
                update = await layout.render()
                self.apply_update(update, root_model)
                self.render(layout, root_model)
