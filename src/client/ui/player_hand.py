import tkinter as tk


class PlayerHand:
    @staticmethod
    def create_hand_area(container):
        """
        Creates the player's hand area.
        """
        tk.Label(
            container,
            text="Your Hand",
            font=("Arial", 14),
            bg="#34495E",
            fg="white"
        ).pack(pady=10)

        # Placeholder for cards
        tk.Label(
            container,
            text="Cards will appear here",
            font=("Arial", 12),
            bg="#34495E",
            fg="white"
        ).pack(expand=True)

