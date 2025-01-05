import tkinter as tk
from typing import Dict, Optional, Callable, Any, Coroutine, List
import asyncio
from client.ui.chat_box import ChatBox
from client.ui.game_board import GameBoard
from client.ui.player_hand import PlayerHand
from common.card import Card
from common.card_enums import CardColor, CardType


class GameRoomSection:
    def __init__(
        self, parent: tk.Widget, styles: Dict[str, str], is_host: bool = False
    ):
        self.parent = parent
        self.styles = styles
        self.is_host = is_host

        self.on_leave_room: Optional[Callable[[], Coroutine]] = None
        self.on_start_game: Optional[Callable[[], Coroutine]] = None
        self.on_chat_message: Optional[Callable[[str], Coroutine]] = None
        self.on_card_played: Optional[
            Callable[[Card, Optional[CardColor]], Coroutine]
        ] = None
        self.on_card_drawn: Optional[Callable[[], Coroutine]] = None
        self.on_color_selected: Optional[Callable[[CardColor], Coroutine]] = None

        self.pending_wild_card: Optional[Card] = None
        self._create_widgets()

    def _create_widgets(self):
        self.frame = tk.Frame(self.parent, bg=self.styles["bg_color"])
        self.frame.place(relwidth=1, relheight=1)

        self._create_game_area()
        self._create_side_panel()

    def _create_game_area(self):
        game_area = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        game_area.place(relx=0.02, rely=0.02, relwidth=0.66, relheight=0.96)

        self.game_board = GameBoard(game_area, self.styles)
        self.game_board.frame.pack(fill="both", expand=True, pady=(0, 10))

        self.player_hand = PlayerHand(game_area, self.styles)
        self.player_hand.frame.pack(fill="x", pady=10)
        self.player_hand.on_card_clicked = self._handle_card_click

    def _create_side_panel(self):
        side_panel = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        side_panel.place(relx=0.7, rely=0.02, relwidth=0.28, relheight=0.96)

        tk.Label(
            side_panel,
            text="Game Room",
            font=("Arial", 16, "bold"),
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
        ).pack(pady=10)

        self.chat_box = ChatBox(side_panel, self.styles)
        self.chat_box.on_message_sent = self.on_chat_message

        self._create_controls(side_panel)

    def _create_controls(self, parent: tk.Widget):
        controls = tk.Frame(parent, bg=self.styles["frame_bg"])
        controls.pack(side="bottom", fill="x", pady=10)

        self.draw_button = tk.Button(
            controls,
            text="Draw Card",
            command=lambda: asyncio.create_task(self._handle_draw_card()),
            bg=self.styles["button_bg"],
            fg=self.styles["button_fg"],
            state="disabled",
        )
        self.draw_button.pack(side="left", padx=5)

        tk.Button(
            controls,
            text="Leave Room",
            command=lambda: self.on_leave_room
            and asyncio.create_task(self.on_leave_room()),
            bg=self.styles["button_bg"],
            fg=self.styles["button_fg"],
        ).pack(side="left", padx=5)

        if self.is_host:
            tk.Button(
                controls,
                text="Start Game",
                command=lambda: self.on_start_game
                and asyncio.create_task(self.on_start_game()),
                bg=self.styles["button_bg"],
                fg=self.styles["button_fg"],
            ).pack(side="right", padx=5)

    def _create_color_selector(self):
        selector = tk.Toplevel(self.frame)
        selector.title("Select Color")
        selector.geometry("200x200")
        selector.transient(self.frame)
        selector.grab_set()

        for color in [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]:
            btn = tk.Button(
                selector,
                text=color.name,
                bg=color.name.lower(),
                fg="white" if color in [CardColor.BLUE, CardColor.GREEN] else "black",
                command=lambda c=color: self._handle_color_selection(c, selector),
            )
            btn.pack(fill="x", padx=10, pady=5)

    async def _handle_card_click(self, card: Card):
        if not self.on_card_played:
            return

        if card.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            self.pending_wild_card = card
            self._create_color_selector()
        else:
            await self.on_card_played(card, None)

    async def _handle_draw_card(self):
        if self.on_card_drawn:
            await self.on_card_drawn()

    def _handle_color_selection(self, color: CardColor, selector: tk.Toplevel):
        selector.destroy()
        if self.pending_wild_card and self.on_card_played:
            asyncio.create_task(self.on_card_played(self.pending_wild_card, color))
            self.pending_wild_card = None

    def update_game_state(self, game_state: Dict[str, Any]):
        if game_state["state"] == "PLAYING":
            self.draw_button.config(state="normal")
            self.game_board.update_state(game_state)
            self.player_hand.update_hand(game_state.get("your_hand", []))

            is_current_player = game_state["current_player_id"] == game_state.get(
                "your_player_id"
            )
            self.draw_button.config(state="normal" if is_current_player else "disabled")
            self.player_hand.set_interactive(is_current_player)
            if is_current_player:
                top_card = Card.from_dict(game_state["top_card"])
                playable_cards = self._get_playable_cards(
                    top_card,
                    [Card.from_dict(card) for card in game_state["your_hand"]],
                    (
                        CardColor[game_state["current_color"]]
                        if game_state.get("current_color")
                        else None
                    ),
                )
                # self.player_hand.highlight_playable_cards(playable_cards)
        else:
            self.draw_button.config(state="disabled")
            self.player_hand.set_interactive(False)

    def show_winner(self, winner_name: str):
        self.chat_box.add_system_message(f"{winner_name} has won the game!")

    def _get_playable_cards(
        self, top_card: Card, hand: List[Card], current_color: CardColor
    ) -> List[Card]:
        return [
            card
            for card in hand
            if card.can_be_played_on(
                top_card,
                (
                    current_color
                    if card.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]
                    else None
                ),
            )
        ]

    def destroy(self):
        if hasattr(self, "frame"):
            self.frame.destroy()
