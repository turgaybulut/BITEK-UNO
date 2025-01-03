from typing import Optional, Dict, Any
import asyncio
from uuid import uuid4
from client.websocket_client import WebSocketClient
from server.event_manager import EventManager
from common.network_protocol import (
    MessageType,
    GameState,
    AuthenticateMessage,
    CreateRoomMessage,
    JoinRoomMessage,
    PlayCardMessage,
    DrawCardMessage,
    ChatMessage,
)
from common.card import Card


class GameClient:
    def __init__(self, server_url: str, player_name: str):
        self.player_id = str(uuid4())
        self.player_name = player_name
        self.event_manager = EventManager()
        self.ws_client = WebSocketClient(server_url, self.event_manager)
        self.current_room_id: Optional[str] = None
        self.current_game_state: Optional[GameState] = None
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        self.event_manager.on(
            f"message_{MessageType.AUTHENTICATED.name}", self._handle_authenticated
        )
        self.event_manager.on(
            f"message_{MessageType.ROOM_CREATED.name}", self._handle_room_created
        )
        self.event_manager.on(
            f"message_{MessageType.ROOM_JOINED.name}", self._handle_room_joined
        )
        self.event_manager.on(
            f"message_{MessageType.ROOM_LEFT.name}", self._handle_room_left
        )
        self.event_manager.on(
            f"message_{MessageType.ROOM_CLOSED.name}", self._handle_room_closed
        )
        self.event_manager.on(
            f"message_{MessageType.GAME_STATE.name}", self._handle_game_state
        )
        self.event_manager.on(
            f"message_{MessageType.GAME_STARTED.name}", self._handle_game_started
        )
        self.event_manager.on(
            f"message_{MessageType.GAME_END.name}", self._handle_game_ended
        )
        self.event_manager.on(
            f"message_{MessageType.CHAT_MESSAGE.name}", self._handle_chat_message
        )
        self.event_manager.on(f"message_{MessageType.ERROR.name}", self._handle_error)
        self.event_manager.on(
            f"message_{MessageType.PLAYER_DISCONNECTED.name}",
            self._handle_player_disconnected,
        )
        self.event_manager.on(
            f"message_{MessageType.PLAYER_RECONNECTED.name}",
            self._handle_player_reconnected,
        )
        self.event_manager.on(
            f"message_{MessageType.ROOM_LIST.name}", self._handle_room_list
        )
        self.event_manager.on("connection_closed", self._handle_connection_closed)

    async def connect(self) -> bool:
        if await self.ws_client.connect():
            await self._authenticate()
            return True
        return False

    async def disconnect(self) -> None:
        await self.ws_client.disconnect()

    async def create_room(self) -> None:
        message: CreateRoomMessage = {
            "type": MessageType.CREATE_ROOM.name,
            "player_id": self.player_id,
        }
        await self.ws_client.send_message(message)

    async def join_room(self, room_id: str) -> None:
        message: JoinRoomMessage = {
            "type": MessageType.JOIN_ROOM.name,
            "room_id": room_id,
            "player_id": self.player_id,
        }
        await self.ws_client.send_message(message)

    async def leave_room(self) -> None:
        if not self.current_room_id:
            return

        await self.ws_client.send_message(
            {
                "type": MessageType.LEAVE_ROOM.name,
                "room_id": self.current_room_id,
                "player_id": self.player_id,
            }
        )
        self.current_room_id = None

    async def start_game(self) -> None:
        if not self.current_room_id:
            return

        await self.ws_client.send_message(
            {"type": MessageType.START_GAME.name, "room_id": self.current_room_id}
        )

    async def play_card(self, card: Card, chosen_color: Optional[str] = None) -> None:
        if not self.current_room_id:
            return

        message: PlayCardMessage = {
            "type": MessageType.PLAY_CARD.name,
            "room_id": self.current_room_id,
            "player_id": self.player_id,
            "card": card.to_dict(),
            "chosen_color": chosen_color,
        }
        await self.ws_client.send_message(message)

    async def draw_card(self) -> None:
        if not self.current_room_id:
            return

        message: DrawCardMessage = {
            "type": MessageType.DRAW_CARD.name,
            "room_id": self.current_room_id,
            "player_id": self.player_id,
        }
        await self.ws_client.send_message(message)

    async def send_chat_message(self, content: str) -> None:
        if not self.current_room_id:
            return

        message: ChatMessage = {
            "type": MessageType.CHAT_MESSAGE.name,
            "room_id": self.current_room_id,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "content": content,
            "timestamp": None,
        }
        await self.ws_client.send_message(message)

    async def _authenticate(self) -> None:
        message: AuthenticateMessage = {
            "type": MessageType.AUTHENTICATE.name,
            "player_id": self.player_id,
            "name": self.player_name,
        }
        await self.ws_client.send_message(message)

    async def _handle_authenticated(self, data: Dict[str, Any]) -> None:
        await self.event_manager.emit("client_authenticated", data)

    async def _handle_room_created(self, data: Dict[str, Any]) -> None:
        self.current_room_id = data["room_id"]
        self.current_game_state = data["state"]
        await self.event_manager.emit("room_created", data)

    async def _handle_room_joined(self, data: Dict[str, Any]) -> None:
        self.current_room_id = data["room_id"]
        self.current_game_state = data["state"]
        await self.event_manager.emit("room_joined", data)

    async def _handle_room_left(self, data: Dict[str, Any]) -> None:
        if data["room_id"] == self.current_room_id:
            self.current_room_id = None
            self.current_game_state = None
            await self.event_manager.emit("room_left", data)

    async def _handle_room_closed(self, data: Dict[str, Any]) -> None:
        if data["room_id"] == self.current_room_id:
            self.current_room_id = None
            self.current_game_state = None
            await self.event_manager.emit("room_closed", data)

    async def _handle_game_state(self, data: Dict[str, Any]) -> None:
        self.current_game_state = data["state"]
        await self.event_manager.emit("game_state_updated", data)

    async def _handle_game_started(self, data: Dict[str, Any]) -> None:
        self.current_game_state = data["state"]
        await self.event_manager.emit("game_started", data)

    async def _handle_game_ended(self, data: Dict[str, Any]) -> None:
        self.current_game_state = data["state"]
        await self.event_manager.emit("game_ended", data)

    async def _handle_chat_message(self, data: Dict[str, Any]) -> None:
        await self.event_manager.emit("chat_message_received", data)

    async def _handle_error(self, data: Dict[str, Any]) -> None:
        await self.event_manager.emit("error", data)

    async def _handle_player_disconnected(self, data: Dict[str, Any]) -> None:
        if data["room_id"] == self.current_room_id:
            await self.event_manager.emit(
                "player_disconnected",
                {"room_id": data["room_id"], "player_id": data["player_id"]},
            )

    async def _handle_player_reconnected(self, data: Dict[str, Any]) -> None:
        if data["room_id"] == self.current_room_id:
            await self.event_manager.emit(
                "player_reconnected",
                {"room_id": data["room_id"], "player_id": data["player_id"]},
            )

    async def _handle_room_list(self, data: Dict[str, Any]):
        await self.event_manager.emit("room_list_updated", data)

    async def _handle_connection_closed(self, _: Dict[str, Any]) -> None:
        self.current_room_id = None
        self.current_game_state = None
        await self.event_manager.emit("connection_closed", {})
