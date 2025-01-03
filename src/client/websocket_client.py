from typing import Optional, Dict, Any
import json
import asyncio
import websockets
from websockets.asyncio.client import ClientConnection
from server.event_manager import EventManager
from client.logger import ClientLogger


class WebSocketClient:
    def __init__(self, uri: str, event_manager: EventManager):
        self.uri = uri
        self.event_manager = event_manager
        self.websocket: Optional[ClientConnection] = None
        self.connected = False
        self.logger = ClientLogger("WebSocketClient")

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
                except json.JSONDecodeError:
                    self.logger.log_error(f"Invalid JSON received: {message}")
                    continue
                except Exception as e:
                    self.logger.log_error(f"Error processing message: {e}")
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
