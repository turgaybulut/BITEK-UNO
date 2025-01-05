import tkinter as tk
from typing import Dict, List, Optional, Callable, Coroutine, Any
import asyncio
from common.card import Card
from common.card_enums import CardType, CardColor


class CardButton(tk.Button):
    def __init__(
        self,
        parent: tk.Widget,
        card: Card,
        styles: Dict[str, str],
        on_click: Callable[[Card], None],
    ):
        self.card = card

        if card.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            bg_color = "black"
            fg_color = "white"
            text = card.type.name.replace("_", "\n")
        else:
            bg_color = card.color.name.lower()
            fg_color = (
                "white" if card.color in [CardColor.BLUE, CardColor.GREEN] else "black"
            )
            text = str(card.value) if card.type == CardType.NUMBER else card.type.name

        super().__init__(
            parent,
            text=text,
            font=("Arial", 12),
            bg=bg_color,
            fg=fg_color,
            width=8,
            height=4,
            relief="raised",
            command=lambda: on_click(card),
        )


class PlayerHand:
    def __init__(self, parent: tk.Widget, styles: Dict[str, str]):
        self.parent = parent
        self.styles = styles
        self.on_card_clicked: Optional[Callable[[Card], Coroutine]] = None
        self.cards: List[CardButton] = []
        self.interactive = False
        self._create_widgets()

    def _create_widgets(self):
        self.frame = tk.Frame(self.parent, bg=self.styles["frame_bg"])

        self.scroll_frame = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        self.scroll_frame.pack(fill="x")

        self.canvas = tk.Canvas(
            self.scroll_frame,
            bg=self.styles["frame_bg"],
            height=150,
            highlightthickness=0,
        )
        self.scrollbar = tk.Scrollbar(
            self.scroll_frame,
            orient="horizontal",
            command=self.canvas.xview,
        )

        self.cards_frame = tk.Frame(self.canvas, bg=self.styles["frame_bg"])
        self.cards_frame_id = self.canvas.create_window(
            (0, 0),
            window=self.cards_frame,
            anchor="nw",
        )

        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(fill="x", expand=True)
        self.scrollbar.pack(fill="x")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.cards_frame.bind("<Configure>", self._on_frame_configure)

    def _on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfigure(
            self.cards_frame_id,
            width=event.width,
        )

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _handle_card_click(self, card: Card):
        print(f"Card clicked: {card}")  # Debug print
        if self.on_card_clicked and self.interactive:
            asyncio.create_task(self.on_card_clicked(card))

    def update_hand(self, cards_data: List[Dict[str, Any]]):
        for card_button in self.cards:
            card_button.destroy()
        self.cards.clear()

        for card_data in cards_data:
            card = Card.from_dict(card_data)
            card_button = CardButton(
                self.cards_frame, card, self.styles, self._handle_card_click
            )
            card_button.pack(side="left", padx=2)

            self.cards.append(card_button)

        self.set_interactive(self.interactive)

    def set_interactive(self, interactive: bool):
        self.interactive = interactive
        for card_button in self.cards:
            card_button.config(
                state="normal" if interactive else "disabled",
                relief="raised" if interactive else "flat",
            )

    def highlight_playable_cards(self, playable_cards: List[Card]):
        for card_button in self.cards:
            if any(
                card_button.card == playable_card for playable_card in playable_cards
            ):
                card_button.config(relief="raised", state="normal")
            else:
                card_button.config(relief="sunken", state="disabled")
