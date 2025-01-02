import tkinter as tk


class GameBoard:
    @staticmethod
    def create_game_board(container):
        """
        Creates the game board area.
        """
        tk.Label(
            container,
            text="Game Board",
            font=("Arial", 14),
            bg="#2C3E50",
            fg="white"
        ).pack(pady=20)

        # Placeholder for the actual game board content
        tk.Label(
            container,
            text="Game in Progress...",
            font=("Arial", 12),
            bg="#34495E",
            fg="white"
        ).pack(expand=True)
