from typing import Dict, Type, Union

from idom.backend.types import Location
from idom.core.hooks import Context, create_context, use_context

from django_idom.types import IdomWebsocket


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
