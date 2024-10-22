# mypy: disable-error-code=attr-defined
import asyncio


class ReactPyLayoutHandler:
    """Encapsulate the entire layout handler with a class to prevent overlapping
    variable names between user code.

    This code is designed to be run directly by PyScript, and is not intended to be run
    in a normal Python environment.
    """

    def __init__(self, uuid):
        self.uuid = uuid

    @staticmethod
    def update_model(update, root_model):
        """Apply an update ReactPy's internal DOM model."""
        from jsonpointer import set_pointer

        if update["path"]:
            set_pointer(root_model, update["path"], update["model"])
        else:
            root_model.update(update["model"])

    def render_html(self, layout, model):
        """Submit ReactPy's internal DOM model into the HTML DOM."""
        from pyscript.js_modules import morphdom

        import js

        # Create a new container to render the layout into
        container = js.document.getElementById(f"pyscript-{self.uuid}")
        temp_root_container = container.cloneNode(False)
        self.build_element_tree(layout, temp_root_container, model)

        # Use morphdom to update the DOM
        morphdom.default(container, temp_root_container)

        # Remove the cloned container to prevent memory leaks
        temp_root_container.remove()

    def build_element_tree(self, layout, parent, model):
        """Recursively build an element tree, starting from the root component."""
        import js

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
                elif key == "className":
                    element.className = value
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
        """Create an event handler for an element. This function is used as an
        adapter between ReactPy and browser events."""
        from pyodide.ffi.wrappers import add_event_listener

        target = event_handler_model["target"]

        def event_handler(*args):
            asyncio.create_task(
                layout.deliver({"type": "layout-event", "target": target, "data": args})
            )

        event_name = event_name.lstrip("on_").lower().replace("_", "")
        add_event_listener(element, event_name, event_handler)

    @staticmethod
    def delete_old_workspaces():
        """To prevent memory leaks, we must delete all user generated Python code when
        it is no longer in use (removed from the page). To do this, we compare what
        UUIDs exist on the DOM, versus what UUIDs exist within the PyScript global
        interpreter."""
        import js

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

    async def run(self, workspace_function):
        """Run the layout handler. This function is main executor for all user generated code."""
        from reactpy.core.layout import Layout

        self.delete_old_workspaces()
        root_model: dict = {}

        async with Layout(workspace_function()) as root_layout:
            while True:
                update = await root_layout.render()
                self.update_model(update, root_model)
                self.render_html(root_layout, root_model)
