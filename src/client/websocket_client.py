from typing import Optional, Dict, Any, Callable, Awaitable
import json
import asyncio
import websockets
from websockets.asyncio.client import ClientConnection
from common.network_protocol import MessageType
from server.event_manager import EventManager


class WebSocketClient:
    def __init__(self, uri: str, event_manager: EventManager):
        self.uri = uri
        self.event_manager = event_manager
        self.websocket: Optional[ClientConnection] = None
        self.connected = False
        self._message_handlers: Dict[
            str, Callable[[Dict[str, Any]], Awaitable[None]]
        ] = {}

    async def connect(self) -> bool:
        try:
            self.websocket = await websockets.connect(
                self.uri,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10,
                max_size=10 * 1024 * 1024,
                compression=None,
                max_queue=32,
            )
            self.connected = True
            asyncio.create_task(self._message_loop())
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            return False

    async def disconnect(self) -> None:
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.connected = False

    async def send_message(self, message: Dict[str, Any]) -> None:
        if not self.connected or not self.websocket:
            raise ConnectionError("WebSocket is not connected")

        try:
            await self.websocket.send(json.dumps(message))
        except Exception:
            self.connected = False
            await self.disconnect()
            raise

    def register_handler(
        self, message_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        self._message_handlers[message_type] = handler

    def unregister_handler(self, message_type: str) -> None:
        self._message_handlers.pop(message_type, None)

    async def _message_loop(self) -> None:
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type")

                    if message_type:
                        await self.event_manager.emit(f"message_{message_type}", data)

                        if message_type in self._message_handlers:
                            await self._message_handlers[message_type](data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")
                    continue
                except Exception as e:
                    print(f"Error processing message: {e}")
                    await self.event_manager.emit("error", {"message": str(e)})
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
            self.connected = False
            await self.event_manager.emit("connection_closed", {"code": e.code})
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            await self.event_manager.emit("error", {"message": str(e)})
        finally:
            self.connected = False
            await self.disconnect()
