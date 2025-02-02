from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from uuid import uuid4
import time
from common.game import Game, Player, GameState
from common.network_protocol import MessageType
from common.card import Card
from common.card_enums import CardColor, CardType
from server.event_manager import EventManager


@dataclass
class ChatMessage:
    player_id: str
    player_name: str
    content: str
    timestamp: float = field(default_factory=lambda: time.time())


class GameRoom:
    def __init__(
        self,
        room_id: Optional[str] = None,
        event_manager: Optional[EventManager] = None,
    ):
        self.room_id = room_id or str(uuid4())
        self.event_manager = event_manager or EventManager()
        self.game = Game(self.room_id)
        self.chat_history: List[ChatMessage] = []

    @property
    def is_full(self) -> bool:
        return len(self.game._players) >= self.game.MAX_PLAYERS

    @property
    def player_count(self) -> int:
        return len(self.game._players)

    async def add_player(self, player: Player) -> bool:
        try:
            if not self.is_full:
                self.game.add_player(player)
                await self._emit_room_update()
                return True
            return False
        except Exception:
            return False

    async def remove_player(self, player_id: str) -> None:
        self.game.remove_player(player_id)
        if self.player_count == 0:
            await self._emit_room_closed()
        else:
            await self._emit_room_update()

    async def start_game(self) -> bool:
        try:
            if self.player_count >= self.game.MIN_PLAYERS:
                self.game.start_game()
                await self._emit_game_started()
                return True
            return False
        except Exception:
            return False

    async def add_chat_message(
        self, player_id: str, player_name: str, content: str
    ) -> None:
        message = ChatMessage(player_id, player_name, content)
        self.chat_history.append(message)
        await self._emit_chat_message(message)

    def get_game_state(self) -> Dict[str, Any]:
        game_state = self.game.get_game_state()
        return game_state

    def get_player_state(self, player_id: str) -> Dict[str, Any]:
        game_state = self.get_game_state()
        player_view = self.game.get_player_view(player_id)
        game_state["your_hand"] = player_view.get("hand", [])

        return {
            "type": MessageType.GAME_STATE.name,
            "room_id": self.room_id,
            "state": game_state,
        }

    async def handle_player_action(
        self, player_id: str, action: str, data: dict
    ) -> bool:
        try:
            match action:
                case "play_card":
                    card = Card.from_dict(data["card"])
                    if card.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
                        chosen_color = data.get("chosen_color")
                        if not chosen_color:
                            return False

                    self.game.play_card(
                        player_id,
                        card,
                        (
                            CardColor[data["chosen_color"]]
                            if data.get("chosen_color")
                            else None
                        ),
                    )

                    if self.game.state == GameState.FINISHED:
                        await self._emit_game_ended()

                case "draw_card":
                    self.game.draw_card(player_id)
                case _:
                    return False

            await self._emit_game_update()
            return True
        except Exception:
            return False

    async def _emit_room_update(self) -> None:
        if self.event_manager:
            await self.event_manager.emit(
                "room_update",
                {
                    "type": MessageType.GAME_STATE.name,
                    "room_id": self.room_id,
                    "state": self.get_game_state(),
                },
            )

    async def _emit_game_update(self) -> None:
        if self.event_manager:
            await self.event_manager.emit(
                "game_update",
                {
                    "type": MessageType.GAME_STATE.name,
                    "room_id": self.room_id,
                    "state": self.get_game_state(),
                },
            )

    async def _emit_game_started(self) -> None:
        if self.event_manager:
            await self.event_manager.emit(
                "game_started",
                {
                    "type": MessageType.GAME_STARTED.name,
                    "room_id": self.room_id,
                    "state": self.get_game_state(),
                },
            )

    async def _emit_game_ended(self) -> None:
        if self.event_manager:
            winner = self.game.get_winner()
            await self.event_manager.emit(
                "game_ended",
                {
                    "type": MessageType.GAME_END.name,
                    "room_id": self.room_id,
                    "winner_id": winner.player_id if winner else None,
                    "state": self.get_game_state(),
                },
            )

    async def _emit_chat_message(self, message: ChatMessage) -> None:
        if self.event_manager:
            await self.event_manager.emit(
                "chat_message",
                {
                    "type": MessageType.CHAT_MESSAGE.name,
                    "room_id": self.room_id,
                    "player_id": message.player_id,
                    "player_name": message.player_name,
                    "content": message.content,
                    "timestamp": message.timestamp,
                },
            )

    async def _emit_room_closed(self) -> None:
        if self.event_manager:
            await self.event_manager.emit(
                "room_closed",
                {"type": MessageType.ROOM_CLOSED.name, "room_id": self.room_id},
            )
