from typing import Optional
from client.game_client import GameClient
from client.ui.game_ui import GameUI
from common.card import Card
from common.card_enums import CardColor


class UICoordinator:
    def __init__(self, game_client: GameClient, game_ui: GameUI):
        self.game_client = game_client
        self.game_ui = game_ui
        self._setup_ui_handlers()
        self._setup_client_handlers()

    def _setup_ui_handlers(self) -> None:
        self.game_ui.on_card_played = self._handle_card_played
        self.game_ui.on_card_drawn = self._handle_card_drawn
        self.game_ui.on_color_selected = self._handle_color_selected
        self.game_ui.on_chat_message = self._handle_chat_message
        self.game_ui.on_start_game = self._handle_start_game
        self.game_ui.on_create_room = self._handle_create_room
        self.game_ui.on_join_room = self._handle_join_room
        self.game_ui.on_leave_room = self._handle_leave_room

    def _setup_client_handlers(self) -> None:
        self.game_client.event_manager.on(
            "client_authenticated", self._handle_authenticated
        )
        self.game_client.event_manager.on("room_created", self._handle_room_created)
        self.game_client.event_manager.on("room_joined", self._handle_room_joined)
        self.game_client.event_manager.on("game_state_updated", self._handle_game_state)
        self.game_client.event_manager.on("game_started", self._handle_game_started)
        self.game_client.event_manager.on("game_ended", self._handle_game_ended)
        self.game_client.event_manager.on(
            "chat_message_received", self._handle_chat_received
        )
        self.game_client.event_manager.on(
            "player_disconnected", self._handle_player_disconnected
        )
        self.game_client.event_manager.on(
            "player_reconnected", self._handle_player_reconnected
        )
        self.game_client.event_manager.on("error", self._handle_error)
        self.game_client.event_manager.on(
            "connection_closed", self._handle_connection_closed
        )

    async def _handle_card_played(
        self, card: Card, color: Optional[CardColor] = None
    ) -> None:
        await self.game_client.play_card(card, color.name if color else None)

    async def _handle_card_drawn(self) -> None:
        await self.game_client.draw_card()

    async def _handle_color_selected(self, color: CardColor) -> None:
        if self.game_ui.pending_wild_card:
            await self.game_client.play_card(self.game_ui.pending_wild_card, color.name)
            self.game_ui.pending_wild_card = None

    async def _handle_chat_message(self, message: str) -> None:
        await self.game_client.send_chat_message(message)

    async def _handle_start_game(self) -> None:
        await self.game_client.start_game()

    async def _handle_create_room(self) -> None:
        await self.game_client.create_room()

    async def _handle_join_room(self, room_id: str) -> None:
        await self.game_client.join_room(room_id)

    async def _handle_leave_room(self) -> None:
        await self.game_client.leave_room()

    async def _handle_authenticated(self, data: dict) -> None:
        self.game_ui.show_room_controls()

    async def _handle_room_created(self, data: dict) -> None:
        self.game_ui.update_room_state(data["state"])
        self.game_ui.show_game_setup()

    async def _handle_room_joined(self, data: dict) -> None:
        self.game_ui.update_room_state(data["state"])
        self.game_ui.show_game_setup()

    async def _handle_game_state(self, data: dict) -> None:
        self.game_ui.update_game_state(data["state"])

    async def _handle_game_started(self, data: dict) -> None:
        self.game_ui.update_game_state(data["state"])
        self.game_ui.show_game_board()

    async def _handle_game_ended(self, data: dict) -> None:
        self.game_ui.update_game_state(data["state"])
        winner_id = data.get("winner_id")
        if winner_id:
            self.game_ui.show_winner(winner_id)
        self.game_ui.show_game_end()

    async def _handle_chat_received(self, data: dict) -> None:
        self.game_ui.add_chat_message(
            data["player_name"], data["content"], data["timestamp"]
        )

    async def _handle_error(self, data: dict) -> None:
        self.game_ui.show_error(data["message"])

    async def _handle_player_disconnected(self, data: dict) -> None:
        self.game_ui.update_player_connection(data["player_id"], False)
        self.game_ui.show_player_disconnected(data["player_id"])

    async def _handle_player_reconnected(self, data: dict) -> None:
        self.game_ui.update_player_connection(data["player_id"], True)
        self.game_ui.show_player_reconnected(data["player_id"])

    async def _handle_connection_closed(self, _: dict) -> None:
        self.game_ui.show_connection_lost()
        self.game_ui.show_reconnect_prompt()
