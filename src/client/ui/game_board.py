import tkinter as tk
from typing import Dict, Any, List
from common.card import Card
from common.card_enums import CardType, CardColor


class GameBoard:
    def __init__(self, parent: tk.Widget, styles: Dict[str, str]):
        self.parent = parent
        self.styles = styles
        self._create_widgets()

    def _create_widgets(self):
        self.frame = tk.Frame(self.parent, bg=self.styles["frame_bg"])

        self.top_frame = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        self.top_frame.pack(fill="x", padx=10, pady=5)

        self.deck_label = tk.Label(
            self.top_frame,
            text="Deck: 0",
            font=("Arial", 12),
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
        )
        self.deck_label.pack(side="left")

        self.direction_label = tk.Label(
            self.top_frame,
            text="→",
            font=("Arial", 16),
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
        )
        self.direction_label.pack(side="right")

        self.board_frame = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        self.board_frame.pack(fill="both", expand=True, padx=10)

        self.current_color_frame = tk.Frame(
            self.board_frame,
            width=50,
            height=50,
            bg=self.styles["frame_bg"],
        )
        self.current_color_frame.pack(side="left", padx=10)

        self.top_card_frame = tk.Frame(
            self.board_frame,
            width=100,
            height=150,
            bg="white",
            relief="solid",
            borderwidth=1,
        )
        self.top_card_frame.pack(side="left", padx=10)
        self.top_card_frame.pack_propagate(False)

        self.top_card_label = tk.Label(
            self.top_card_frame,
            text="No Card",
            font=("Arial", 14),
            bg="white",
            fg="black",
        )
        self.top_card_label.pack(expand=True)

        self.players_frame = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        self.players_frame.pack(fill="x", padx=10, pady=10)

        self.player_labels: Dict[str, tk.Label] = {}

    def update_state(self, game_state: Dict[str, Any]):
        self.deck_label.config(text=f"Deck: {game_state['deck_count']}")
        self.direction_label.config(
            text="→" if game_state["direction_clockwise"] else "←"
        )

        current_color = game_state.get("current_color")
        if current_color:
            color_name = CardColor[current_color].name.lower()
            self.current_color_frame.config(bg=color_name)
        else:
            top_card = Card.from_dict(game_state["top_card"])
            self.current_color_frame.config(bg=top_card.color.name.lower())

        top_card = game_state.get("top_card")
        if top_card:
            card_type = CardType[top_card["type"]]
            card_color = CardColor[top_card["color"]]
            card_value = top_card["value"]

            if card_type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
                text = card_type.name.replace("_", "\n")
                bg_color = "black"
                fg_color = "white"
            else:
                text = (
                    str(card_value) if card_type == CardType.NUMBER else card_type.name
                )
                bg_color = card_color.name.lower()
                fg_color = (
                    "white"
                    if card_color in [CardColor.BLUE, CardColor.GREEN]
                    else "black"
                )

            self.top_card_label.config(
                text=text,
                bg=bg_color,
                fg=fg_color,
            )
            self.top_card_frame.config(bg=bg_color)

        self._update_players(game_state["players"], game_state["current_player_id"])

    def _update_players(self, players: List[Dict[str, Any]], current_player_id: str):
        for widget in self.players_frame.winfo_children():
            widget.destroy()
        self.player_labels.clear()

        for i, player in enumerate(players):
            player_frame = tk.Frame(
                self.players_frame,
                bg=self.styles["frame_bg"],
                relief="solid" if player["id"] == current_player_id else "flat",
                borderwidth=2 if player["id"] == current_player_id else 0,
            )
            player_frame.pack(side="left", expand=True, padx=5)

            name_label = tk.Label(
                player_frame,
                text=player["name"],
                font=(
                    "Arial",
                    10,
                    "bold" if player["id"] == current_player_id else "normal",
                ),
                bg=self.styles["frame_bg"],
                fg="red" if not player["is_connected"] else self.styles["fg_color"],
            )
            name_label.pack()

            cards_label = tk.Label(
                player_frame,
                text=f"{player['card_count']} cards",
                font=("Arial", 10),
                bg=self.styles["frame_bg"],
                fg=self.styles["fg_color"],
            )
            cards_label.pack()

            self.player_labels[player["id"]] = name_label
