"""Code within this module is designed to be run directly by PyScript, and is not
intended to be run in a Django environment.

Our template tag performs string substitutions to turn this file into valid PyScript."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from reactpy_django.pyscript.layout_manager import ReactPyLayoutManager


# User component is inserted below by regex replacement
def user_workspace_UUID():
    """Encapsulate the user's code with a completely unique function (workspace)
    to prevent overlapping imports and variable names between different components."""

    def root(): ...

    return root()


# PyScript allows top-level await, which allows us to not throw errors on components
# that terminate early (such as hook-less components)
await ReactPyLayoutManager("UUID").run(user_workspace_UUID)  # noqa: F704
