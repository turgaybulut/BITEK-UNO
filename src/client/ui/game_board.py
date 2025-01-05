import tkinter as tk


class GameBoard:
    def __init__(self):
        self.current_card_button = None
        self.turn_label = None

    def create_game_board(self, container, current_card, players):
        """
        Creates the game board area.

        Parameters:
        - container: Parent container for the game board.
        - current_card: The current card on the pile (e.g., "Red 5").
        - players: List of dictionaries with player info (name and card count).
        """
        # Current Card on the Pile
        current_card_frame = tk.Frame(container, bg="#34495E")
        current_card_frame.pack(side=tk.TOP, fill="x", pady=10)

        tk.Label(
            current_card_frame,
            text="Current Card:",
            font=("Arial", 14),
            bg="#34495E",
            fg="white"
        ).pack(pady=5)

        self.current_card_button = tk.Button(
            current_card_frame,
            text=current_card,
            font=("Arial", 12),
            bg="#E74C3C",
            fg="white",
            width=10,
            height=2
        )
        self.current_card_button.pack()

        # Player Info
        players_frame = tk.Frame(container, bg="#34495E")
        players_frame.pack(fill="x", pady=10)

        for player in players:
            player_frame = tk.Frame(players_frame, bg="#34495E")
            player_frame.pack(fill="x", pady=5)

            tk.Label(
                player_frame,
                text=f"{player['name']}: {player['card_count']} cards",
                font=("Arial", 12),
                bg="#34495E",
                fg="white"
            ).pack(side=tk.LEFT, padx=10)

        # Turn Indicator
        self.turn_label = tk.Label(
            container,
            text="Current Turn: Player 1",
            font=("Arial", 14),
            bg="#34495E",
            fg="#27AE60"
        )
        self.turn_label.pack(pady=10)

    def update_current_card(self, new_card):
        """Updates the current card displayed on the pile."""
        self.current_card_button.config(text=new_card)

    def update_turn(self, player_name):
        """Updates the turn indicator."""
        self.turn_label.config(text=f"Current Turn: {player_name}")
