from dataclasses import dataclass
from inspect import iscoroutinefunction
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Sequence,
    Type,
    Union,
    overload,
)

from channels.db import database_sync_to_async
from idom.backend.types import Location
from idom.core.hooks import (
    Context,
    _EffectApplyFunc,
    create_context,
    use_context,
    use_effect,
)


if not TYPE_CHECKING:
    # make flake8 think that this variable exists
    ellipsis = type(...)


@dataclass
class IdomWebsocket:
    scope: dict
    close: Callable[[Optional[int]], Awaitable[None]]
    disconnect: Callable[[int], Awaitable[None]]
    view_id: str


WebsocketContext: Type[Context[Union[IdomWebsocket, None]]] = create_context(
    None, "WebSocketContext"
)


def use_location() -> Location:
    """Get the current route as a string"""
    # TODO: Use the browser's current page, rather than the WS route
    scope = use_scope()
    search = scope["query_string"].decode()
    return Location(scope["path"], f"?{search}" if search else "")


def use_scope() -> Dict:
    """Get the current ASGI scope dictionary"""
    return use_websocket().scope


def use_websocket() -> IdomWebsocket:
    """Get the current IdomWebsocket object"""
    websocket = use_context(WebsocketContext)
    if websocket is None:
        raise RuntimeError("No websocket. Are you running with a Django server?")
    return websocket


@overload
def use_sync_to_async(
    function: None = None,
    dependencies: Union[Sequence[Any], ellipsis, None] = ...,
) -> Callable[[_EffectApplyFunc], None]:
    ...


@overload
def use_sync_to_async(
    function: _EffectApplyFunc,
    dependencies: Union[Sequence[Any], ellipsis, None] = ...,
) -> None:
    ...


def use_sync_to_async(
    function: Optional[_EffectApplyFunc] = None,
    dependencies: Union[Sequence[Any], ellipsis, None] = ...,
) -> Optional[Callable[[_EffectApplyFunc], None]]:
    """This is a sync_to_async wrapper for `idom.hooks.use_effect`.
    See the full :ref:`Use Effect` docs for details

    Parameters:
        function:
            Applies the effect and can return a clean-up function
        dependencies:
            Dependencies for the effect. The effect will only trigger if the identity
            of any value in the given sequence changes (i.e. their :func:`id` is
            different). By default these are inferred based on local variables that are
            referenced by the given function.

    Returns:
        If a function is not provided:
            A decorator.
        Otherwise:
            `None`
    """
    if function and iscoroutinefunction(function):
        raise ValueError("use_sync_to_async cannot be used with async functions")
    sync_to_async_function = database_sync_to_async(function) if function else None
    return use_effect(sync_to_async_function, dependencies)
