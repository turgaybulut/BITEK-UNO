from typing import Dict, Optional
import asyncio
from server.event_manager import EventManager
from server.websocket_server import WebSocketServer
from common.game_room import GameRoom
from common.game import Player
from common.network_protocol import MessageType


class GameServer:
    def __init__(self, host: str, port: int):
        self.event_manager = EventManager()
        self.ws_server = WebSocketServer(host, port, self.event_manager)
        self.active_rooms: Dict[str, GameRoom] = {}
        self.player_room_map: Dict[str, str] = {}
        self._setup_event_handlers()

    async def start(self):
        await self.ws_server.start()

    async def stop(self):
        await self.ws_server.stop()

    def _setup_event_handlers(self):
        self.event_manager.on(
            f"message_{MessageType.CREATE_ROOM.name}", self._handle_create_room
        )
        self.event_manager.on(
            f"message_{MessageType.JOIN_ROOM.name}", self._handle_join_room
        )
        self.event_manager.on(
            f"message_{MessageType.LEAVE_ROOM.name}", self._handle_leave_room
        )
        self.event_manager.on(
            f"message_{MessageType.START_GAME.name}", self._handle_start_game
        )
        self.event_manager.on(
            f"message_{MessageType.PLAY_CARD.name}", self._handle_play_card
        )
        self.event_manager.on(
            f"message_{MessageType.DRAW_CARD.name}", self._handle_draw_card
        )
        self.event_manager.on(
            f"message_{MessageType.CHAT_MESSAGE.name}", self._handle_chat_message
        )
        self.event_manager.on("player_disconnected", self._handle_player_disconnect)
        self.event_manager.on("room_update", self._handle_room_update)
        self.event_manager.on("game_update", self._handle_game_update)
        self.event_manager.on("chat_message", self._handle_chat_broadcast)
        self.event_manager.on("room_closed", self._handle_room_closed)

    async def _handle_create_room(self, client_id: str, message: dict):
        player_id = message.get("player_id")
        if not player_id:
            return

        room = GameRoom(event_manager=self.event_manager)
        self.active_rooms[room.room_id] = room

        client_session = self.ws_server.clients.get(client_id)
        if client_session:
            player = Player(player_id, client_session.name)
            if room.add_player(player):
                self.player_room_map[player_id] = room.room_id
                self.ws_server.add_to_room(client_id, room.room_id)

                await self.ws_server.send_to_client(
                    client_id,
                    {
                        "type": MessageType.ROOM_CREATED.name,
                        "room_id": room.room_id,
                        "state": room.get_player_state(player_id)["state"],
                    },
                )

    async def _handle_join_room(self, client_id: str, message: dict):
        room_id = message.get("room_id")
        player_id = message.get("player_id")

        if not room_id or not player_id or room_id not in self.active_rooms:
            await self.ws_server.send_to_client(
                client_id,
                {"type": MessageType.ERROR.name, "message": "Invalid room ID"},
            )
            return

        room = self.active_rooms[room_id]
        client_session = self.ws_server.clients.get(client_id)

        if client_session:
            player = Player(player_id, client_session.name)
            if room.add_player(player):
                self.player_room_map[player_id] = room.room_id
                self.ws_server.add_to_room(client_id, room.room_id)

                await self.ws_server.send_to_client(
                    client_id,
                    {
                        "type": MessageType.ROOM_JOINED.name,
                        "room_id": room.room_id,
                        "state": room.get_player_state(player_id)["state"],
                    },
                )
            else:
                await self.ws_server.send_to_client(
                    client_id,
                    {"type": MessageType.ERROR.name, "message": "Room is full"},
                )

    async def _handle_leave_room(self, client_id: str, message: dict):
        room_id = message.get("room_id")
        player_id = message.get("player_id")

        if room_id in self.active_rooms and player_id:
            room = self.active_rooms[room_id]
            room.remove_player(player_id)
            self.ws_server.remove_from_room(client_id)
            self.player_room_map.pop(player_id, None)

            await self.ws_server.send_to_client(
                client_id, {"type": MessageType.ROOM_LEFT.name, "room_id": room_id}
            )

            if room.player_count == 0:
                await self._handle_room_closed({"room_id": room_id})

    async def _handle_start_game(self, client_id: str, message: dict):
        room_id = message.get("room_id")
        if room_id in self.active_rooms:
            room = self.active_rooms[room_id]
            if room.start_game():
                # Game started successfully - notification will be handled by room events
                pass
            else:
                await self.ws_server.send_to_client(
                    client_id,
                    {
                        "type": MessageType.ERROR.name,
                        "message": "Cannot start game - minimum players not met",
                    },
                )

    async def _handle_play_card(self, client_id: str, message: dict):
        room_id = message.get("room_id")
        player_id = message.get("player_id")
        card = message.get("card")
        chosen_color = message.get("chosen_color")

        if room_id in self.active_rooms and player_id:
            room = self.active_rooms[room_id]
            success = room.handle_player_action(
                player_id, "play_card", {"card": card, "chosen_color": chosen_color}
            )

            if not success:
                await self.ws_server.send_to_client(
                    client_id,
                    {"type": MessageType.ERROR.name, "message": "Invalid card play"},
                )

    async def _handle_draw_card(self, client_id: str, message: dict):
        room_id = message.get("room_id")
        player_id = message.get("player_id")

        if room_id in self.active_rooms and player_id:
            room = self.active_rooms[room_id]
            room.handle_player_action(player_id, "draw_card", {})

    async def _handle_chat_message(self, client_id: str, message: dict):
        room_id = message.get("room_id")
        player_id = message.get("player_id")
        content = message.get("content")

        if room_id in self.active_rooms and player_id and content:
            room = self.active_rooms[room_id]
            client_session = self.ws_server.clients.get(client_id)
            if client_session:
                room.add_chat_message(player_id, client_session.name, content)

    async def _handle_player_disconnect(self, player_id: str, room_id: str):
        if room_id in self.active_rooms:
            room = self.active_rooms[room_id]
            room.remove_player(player_id)

            await self.ws_server.broadcast_to_room(
                room_id,
                {
                    "type": MessageType.PLAYER_DISCONNECTED.name,
                    "room_id": room_id,
                    "player_id": player_id,
                },
            )

    async def _handle_room_update(self, data: dict):
        room_id = data["room_id"]
        if room_id in self.active_rooms:
            await self.ws_server.broadcast_to_room(
                room_id,
                {
                    "type": MessageType.GAME_STATE.name,
                    "room_id": room_id,
                    "state": data["state"],
                },
            )

    async def _handle_game_update(self, data: dict):
        await self._handle_room_update(data)

    async def _handle_chat_broadcast(self, data: dict):
        room_id = data["room_id"]
        if room_id in self.active_rooms:
            await self.ws_server.broadcast_to_room(
                room_id,
                {
                    "type": MessageType.CHAT_MESSAGE.name,
                    "room_id": data["room_id"],
                    "player_id": data["player_id"],
                    "player_name": data["player_name"],
                    "content": data["content"],
                    "timestamp": data["timestamp"],
                },
            )

    async def _handle_room_closed(self, data: dict):
        room_id = data["room_id"]
        if room_id in self.active_rooms:
            await self.ws_server.broadcast_to_room(
                room_id, {"type": MessageType.ROOM_CLOSED.name, "room_id": room_id}
            )
            del self.active_rooms[room_id]
            # Clean up player mappings
            self.player_room_map = {
                pid: rid for pid, rid in self.player_room_map.items() if rid != room_id
            }
