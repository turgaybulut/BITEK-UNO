from typing import Optional
from client.game_client import GameClient
from client.ui.game_ui import GameUI
from common.card import Card
from common.card_enums import CardColor, CardType


class UICoordinator:
    def __init__(self, game_client: GameClient, game_ui: GameUI):
        self.game_client = game_client
        self.game_ui = game_ui
        self._setup_ui_handlers()
        self._setup_client_handlers()

    def _setup_ui_handlers(self) -> None:
        self.game_ui.set_on_login(self._handle_login)
        self.game_ui.set_on_create_room(self._handle_create_room)
        self.game_ui.set_on_join_room(self._handle_join_room)
        self.game_ui.set_on_leave_room(self._handle_leave_room)
        self.game_ui.set_on_start_game(self._handle_start_game)
        self.game_ui.set_on_refresh_rooms(self._handle_refresh_rooms)
        self.game_ui.set_on_chat_message(self._handle_chat_message)
        self.game_ui.set_on_card_played(self._handle_card_played)
        self.game_ui.set_on_card_drawn(self._handle_card_drawn)
        self.game_ui.set_on_color_selected(self._handle_color_selected)

    def _setup_client_handlers(self) -> None:
        self.game_client.event_manager.on(
            "client_authenticated", self._handle_authenticated
        )
        self.game_client.event_manager.on(
            "connection_closed", self._handle_connection_closed
        )
        self.game_client.event_manager.on("error", self._handle_error)
        self.game_client.event_manager.on(
            "room_list_updated", self._handle_room_list_updated
        )
        self.game_client.event_manager.on("room_created", self._handle_room_created)
        self.game_client.event_manager.on("room_joined", self._handle_room_joined)
        self.game_client.event_manager.on("room_left", self._handle_room_left)
        self.game_client.event_manager.on("game_started", self._handle_game_started)
        self.game_client.event_manager.on("room_closed", self._handle_room_closed)
        self.game_client.event_manager.on(
            "chat_message_received", self._handle_chat_received
        )
        self.game_client.event_manager.on("game_state_updated", self._handle_game_state)
        self.game_client.event_manager.on("game_ended", self._handle_game_ended)
        self.game_client.event_manager.on(
            "player_disconnected", self._handle_player_disconnected
        )
        self.game_client.event_manager.on(
            "player_reconnected", self._handle_player_reconnected
        )

    async def _handle_login(self, username: str):
        try:
            self.game_client.player_name = username
            success = await self.game_client.connect()
            if not success:
                self.game_ui.show_error("Failed to connect to server")
        except Exception as e:
            self.game_ui.show_error(f"Connection error: {str(e)}")

    async def _handle_card_played(
        self, card: Card, chosen_color: Optional[CardColor] = None
    ) -> None:
        try:
            await self.game_client.play_card(
                card, chosen_color.name if chosen_color else None
            )
        except Exception as e:
            self.game_ui.show_error(f"Failed to play card: {str(e)}")

    async def _handle_card_drawn(self) -> None:
        try:
            await self.game_client.draw_card()
        except Exception as e:
            self.game_ui.show_error(f"Failed to draw card: {str(e)}")

    async def _handle_color_selected(self, color: CardColor) -> None:
        if self.game_ui.game_room and self.game_ui.game_room.pending_wild_card:
            await self._handle_card_played(
                self.game_ui.game_room.pending_wild_card, color
            )
            self.game_ui.game_room.pending_wild_card = None

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

    async def _handle_refresh_rooms(self) -> None:
        await self.game_client.request_room_list()

    async def _handle_authenticated(self, data: dict) -> None:
        self.game_ui.show_room_selection()
        await self._handle_refresh_rooms()

    async def _handle_room_created(self, data: dict) -> None:
        self.game_ui.show_game_room(is_host=True)

    async def _handle_room_joined(self, data: dict) -> None:
        self.game_ui.show_game_room(is_host=False)

    async def _handle_room_left(self, data: dict) -> None:
        self.game_ui.show_room_selection()
        await self._handle_refresh_rooms()

    async def _handle_room_closed(self, data: dict) -> None:
        self.game_ui.show_error("Room has been closed!")
        self.game_ui.show_room_selection()
        await self._handle_refresh_rooms()

    async def _handle_game_state(self, data: dict) -> None:
        if self.game_ui.game_room:
            game_state = data["state"]
            game_state["your_player_id"] = self.game_client.player_id
            self.game_ui.update_game_state(game_state)

    async def _handle_game_started(self, data: dict) -> None:
        if self.game_ui.game_room:
            self.game_ui.add_system_message("Game started!")
            game_state = data["state"]
            game_state["your_player_id"] = self.game_client.player_id
            self.game_ui.update_game_state(game_state)

    async def _handle_game_ended(self, data: dict) -> None:
        winner_id = data.get("winner_id")
        if winner_id and self.game_ui.game_room:
            winner_name = next(
                (p["name"] for p in data["state"]["players"] if p["id"] == winner_id),
                "Unknown Player",
            )
            self.game_ui.show_winner(winner_name)

    async def _handle_chat_received(self, data: dict) -> None:
        self.game_ui.add_chat_message(
            data["player_name"], data["content"], data["timestamp"]
        )

    async def _handle_error(self, data: dict) -> None:
        self.game_ui.show_error(data["message"])

    async def _handle_player_disconnected(self, data: dict) -> None:
        if self.game_ui.game_room:
            player_id = data["player_id"]
            player_name = next(
                (p["name"] for p in data["state"]["players"] if p["id"] == player_id),
                "Unknown Player",
            )
            self.game_ui.add_system_message(f"{player_name} disconnected")

    async def _handle_player_reconnected(self, data: dict) -> None:
        if self.game_ui.game_room:
            player_id = data["player_id"]
            player_name = next(
                (p["name"] for p in data["state"]["players"] if p["id"] == player_id),
                "Unknown Player",
            )
            self.game_ui.add_system_message(f"{player_name} reconnected")

    async def _handle_room_list_updated(self, data: dict):
        self.game_ui.update_room_list(data["rooms"])

    async def _handle_connection_closed(self, _: dict) -> None:
        self.game_ui.show_connection_lost()
