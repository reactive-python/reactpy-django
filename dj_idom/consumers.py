"""Anything used to construct a websocket endpoint"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class CommandConsumer(AsyncJsonWebsocketConsumer):
    """Websocket communication."""

    # INITIAL CONNECTION
    async def connect(self):
        """When the browser attempts to connect to the server."""
        # Accept the connection
        await self.accept()

    # RECEIVING COMMANDS
    async def receive_json(self, content, **kwargs):
        """When the browser attempts to send a message to the server."""
        pass
