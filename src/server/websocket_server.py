from dataclasses import dataclass
from typing import Dict, Set, Optional, Any
import asyncio
import json
import websockets
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed
from server.event_manager import EventManager
from server.logger import server_logger, Direction
from common.network_protocol import MessageType


@dataclass
class ClientSession:
    ws: ClientConnection
    player_id: str
    room_id: Optional[str] = None
    name: str = ""
    is_authenticated: bool = False


class WebSocketServer:
    def __init__(self, host: str, port: int, event_manager: EventManager):
        self.host = host
        self.port = port
        self.event_manager = event_manager
        self.clients: Dict[str, ClientSession] = {}
        self.room_clients: Dict[str, Set[str]] = {}
        self.server = None

    async def start(self):
        self.server = await websockets.serve(
            self._handle_connection,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10,
            close_timeout=10,
            max_size=10 * 1024 * 1024,
            compression=None,
            max_queue=32,
        )
        print(f"Server started at ws://{self.host}:{self.port}")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any]) -> None:
        if room_id not in self.room_clients:
            return

        msg_str = json.dumps(message)
        tasks = []
        for client_id in self.room_clients[room_id]:
            if client_id in self.clients:
                try:
                    tasks.append(self.clients[client_id].ws.send(msg_str))
                except Exception:
                    continue
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        msg_str = json.dumps(message)
        tasks = []
        for client_id, client in self.clients.items():
            try:
                tasks.append(client.ws.send(msg_str))
            except Exception:
                continue
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> None:
        if client_id in self.clients:
            try:
                server_logger.log_message(
                    Direction.OUTGOING, message["type"], client_id
                )
                await self.clients[client_id].ws.send(json.dumps(message))
            except Exception:
                await self._handle_client_disconnect(client_id)

    async def _handle_connection(self, websocket: ClientConnection):
        client_id = str(id(websocket))
        server_logger.log_connection(client_id)
        try:
            self.clients[client_id] = ClientSession(ws=websocket, player_id="")
            print(f"New connection: {client_id}")
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(client_id, data)
                except json.JSONDecodeError:
                    await self.send_to_client(
                        client_id,
                        {
                            "type": MessageType.ERROR.name,
                            "message": "Invalid message format",
                        },
                    )
                except Exception as e:
                    print(f"Error processing message: {e}")
                    await self.send_to_client(
                        client_id, {"type": MessageType.ERROR.name, "message": str(e)}
                    )
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected (normal): {client_id}")
        except Exception as e:
            print(f"Client disconnected (error): {client_id} - {str(e)}")
        finally:
            await self._cleanup_client(client_id)

    async def _process_message(self, client_id: str, message: Dict[str, Any]):
        msg_type = message.get("type")
        if not msg_type:
            await self.send_to_client(
                client_id,
                {
                    "type": MessageType.ERROR.name,
                    "message": "Message type not specified",
                },
            )
            return

        server_logger.log_message(Direction.INCOMING, msg_type, client_id)
        if msg_type == MessageType.AUTHENTICATE.name:
            await self._handle_authentication(client_id, message)
        elif not self.clients[client_id].is_authenticated:
            await self.send_to_client(
                client_id,
                {"type": MessageType.ERROR.name, "message": "Authentication required"},
            )
            return
        else:
            await self.event_manager.emit(f"message_{msg_type}", client_id, message)

    async def _handle_authentication(self, client_id: str, message: Dict[str, Any]):
        player_id = message.get("player_id")
        name = message.get("name")

        if not player_id or not name:
            await self.send_to_client(
                client_id,
                {
                    "type": MessageType.ERROR.name,
                    "message": "Invalid authentication data",
                },
            )
            return

        session = self.clients[client_id]
        session.player_id = player_id
        session.name = name
        session.is_authenticated = True

        await self.send_to_client(
            client_id, {"type": MessageType.AUTHENTICATED.name, "player_id": player_id}
        )

    async def _handle_client_disconnect(self, client_id: str):
        if client_id not in self.clients:
            return

        session = self.clients[client_id]
        if session.room_id:
            if session.room_id in self.room_clients:
                self.room_clients[session.room_id].remove(client_id)
                if not self.room_clients[session.room_id]:
                    del self.room_clients[session.room_id]

            await self.event_manager.emit(
                "player_disconnected", session.player_id, session.room_id
            )

    async def _cleanup_client(self, client_id: str):
        if client_id in self.clients:
            try:
                session = self.clients[client_id]
                if session.room_id:
                    await self.event_manager.emit(
                        "player_disconnected", session.player_id, session.room_id
                    )
                await self.clients[client_id].ws.close()
            except:
                pass
            finally:
                del self.clients[client_id]

    def add_to_room(self, client_id: str, room_id: str):
        if client_id not in self.clients:
            raise ValueError("Invalid client ID")

        self.clients[client_id].room_id = room_id
        if room_id not in self.room_clients:
            self.room_clients[room_id] = set()
        self.room_clients[room_id].add(client_id)

    def remove_from_room(self, client_id: str):
        if client_id not in self.clients:
            return

        session = self.clients[client_id]
        if session.room_id:
            if session.room_id in self.room_clients:
                self.room_clients[session.room_id].remove(client_id)
                if not self.room_clients[session.room_id]:
                    del self.room_clients[session.room_id]
            session.room_id = None
