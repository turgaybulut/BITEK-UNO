import tkinter as tk


class PlayerHand:
    def __init__(self):
        self.card_buttons = []
        self.canvas = None
        self.scrollbar = None
        self.inner_frame = None

    def create_hand_area(self, container, player_cards, on_card_play, on_draw_card, frame_height=100):
        """
        Creates the player's hand area with the scrollbar below the cards.

        Parameters:
        - container: Parent container for the player's hand.
        - player_cards: List of card names (e.g., ["Red 5", "Blue Skip"]).
        - on_card_play: Callback function when a card is played.
        - on_draw_card: Callback function when the "Draw Card" button is pressed.
        - frame_height: Height of the player hand area in pixels (default: 100).
        """
        tk.Label(
            container,
            text="Your Hand:",
            font=("Arial", 14),
            bg="#34495E",
            fg="white"
        ).pack(pady=5)

        # Main frame for player hand
        hand_frame = tk.Frame(container, bg="#34495E")
        hand_frame.pack(fill="x", expand=False)

        # Canvas for the scrollable area
        self.canvas = tk.Canvas(hand_frame, bg="#34495E", height=frame_height, highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill="x", expand=True)

        # Frame inside the canvas for card buttons
        self.inner_frame = tk.Frame(self.canvas, bg="#34495E")
        self.inner_frame_id = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw"
        )

        # Scrollbar for the canvas
        self.scrollbar = tk.Scrollbar(
            hand_frame,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )
        self.scrollbar.pack(side=tk.TOP, fill="x")

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        # Bind events for resizing and scrolling
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Display Player's Cards
        for card in player_cards:
            card_button = tk.Button(
                self.inner_frame,
                text=card,
                font=("Arial", 10),
                bg="#2C3E50",
                fg="white",
                width=10,
                height=2,
                command=lambda c=card: on_card_play(c)
            )
            card_button.pack(side=tk.LEFT, padx=5)
            self.card_buttons.append(card_button)

        # Draw Card Button (outside scrollable area)
        draw_card_button = tk.Button(
            container,
            text="Draw Card",
            font=("Arial", 12),
            bg="#27AE60",
            fg="white",
            command=on_draw_card
        )
        draw_card_button.pack(pady=10)

    def _on_frame_configure(self, event):
        """Adjust the canvas scrollable region to fit the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        """Ensure the inner frame width matches the canvas width."""
        self.canvas.itemconfig(self.inner_frame_id, width=max(event.width, self.inner_frame.winfo_reqwidth()))
