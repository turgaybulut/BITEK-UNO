import tkinter as tk
import asyncio
from typing import Dict, Optional, Callable, Any, Coroutine


class GameRoomSection:
    def __init__(
        self, parent: tk.Widget, styles: Dict[str, str], is_host: bool = False
    ):
        self.parent = parent
        self.styles = styles
        self.is_host = is_host

        self.on_leave_room: Optional[Callable[[], Coroutine]] = None
        self.on_start_game: Optional[Callable[[], Coroutine]] = None

        self._create_widgets()

    def _create_widgets(self):
        self.frame = tk.Frame(self.parent, bg=self.styles["bg_color"])
        self.frame.place(relwidth=1, relheight=1)

        # Game Area (Left side)
        game_area = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        game_area.place(relx=0.02, rely=0.02, relwidth=0.66, relheight=0.96)

        # Placeholder for game board
        tk.Label(
            game_area,
            text="Game Board\n(To be implemented)",
            font=("Arial", 20),
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
        ).pack(expand=True)

        # Chat & Controls (Right side)
        side_panel = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        side_panel.place(relx=0.7, rely=0.02, relwidth=0.28, relheight=0.96)

        # Room Info
        tk.Label(
            side_panel,
            text="Game Room",
            font=("Arial", 16, "bold"),
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
        ).pack(pady=10)

        # Placeholder for chat
        tk.Label(
            side_panel,
            text="Chat Area\n(To be implemented)",
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
        ).pack(expand=True)

        # Control buttons
        controls = tk.Frame(side_panel, bg=self.styles["frame_bg"])
        controls.pack(side="bottom", fill="x", pady=10)

        # Leave button
        tk.Button(
            controls,
            text="Leave Room",
            command=lambda: self.on_leave_room
            and asyncio.create_task(self.on_leave_room()),
            bg=self.styles["button_bg"],
            fg=self.styles["button_fg"],
        ).pack(side="left", padx=5)

        # Start button (host only)
        if self.is_host:
            tk.Button(
                controls,
                text="Start Game",
                command=lambda: self.on_start_game
                and asyncio.create_task(self.on_start_game()),
                bg=self.styles["button_bg"],
                fg=self.styles["button_fg"],
            ).pack(side="right", padx=5)

    def destroy(self):
        if hasattr(self, "frame"):
            self.frame.destroy()
