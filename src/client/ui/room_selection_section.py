import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional, Any, Callable, Coroutine
import asyncio


class RoomSelectionSection:
    def __init__(self, parent: tk.Widget, styles: Dict[str, str]):
        self.parent = parent
        self.styles = styles
        self.rooms: List[Dict[str, Any]] = []

        self.on_create_room: Optional[Callable[[], Coroutine]] = None
        self.on_join_room: Optional[Callable[[str], Coroutine]] = None
        self.on_refresh_rooms: Optional[Callable[[], Coroutine]] = None

        self._create_widgets()

    def _create_widgets(self):
        self.frame = tk.Frame(self.parent, bg=self.styles["bg_color"])
        self.frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

        title = tk.Label(
            self.frame,
            text="Game Rooms",
            font=("Arial", 24, "bold"),
            bg=self.styles["bg_color"],
            fg=self.styles["fg_color"],
        )
        title.pack(pady=20)

        self._create_room_list()
        self._create_controls()

    def _create_room_list(self):
        list_frame = tk.Frame(self.frame, bg=self.styles["frame_bg"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create outer frame for both header and content
        outer_frame = tk.Frame(list_frame, bg=self.styles["frame_bg"])
        outer_frame.pack(fill="both", expand=True)

        # Header Frame with fixed width
        self.header_frame = tk.Frame(outer_frame, bg=self.styles["frame_bg"])
        self.header_frame.pack(fill="x")

        headers = ["Room ID", "Players", "Status", "Action"]
        column_widths = [200, 100, 150, 100]  # Fixed widths for columns

        for col, (header, width) in enumerate(zip(headers, column_widths)):
            header_label = tk.Label(
                self.header_frame,
                text=header,
                font=("Arial", 11, "bold"),
                bg=self.styles["frame_bg"],
                fg=self.styles["fg_color"],
                width=width // 10,  # Convert pixels to character width
            )
            header_label.grid(row=0, column=col, padx=5, sticky="w")

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            outer_frame, bg=self.styles["frame_bg"], highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            outer_frame, orient="vertical", command=self.canvas.yview
        )

        # Create frame for room list with same width settings
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.styles["frame_bg"])
        self.scrollable_frame.columnconfigure(0, minsize=column_widths[0])
        self.scrollable_frame.columnconfigure(1, minsize=column_widths[1])
        self.scrollable_frame.columnconfigure(2, minsize=column_widths[2])
        self.scrollable_frame.columnconfigure(3, minsize=column_widths[3])

        # Configure canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        # Update the scrollable region when the canvas size changes
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _create_controls(self):
        control_frame = tk.Frame(self.frame, bg=self.styles["bg_color"])
        control_frame.pack(pady=20)

        create_btn = tk.Button(
            control_frame,
            text="Create Room",
            command=lambda: asyncio.create_task(self._handle_create_room()),
            font=("Arial", 12),
            bg=self.styles["button_bg"],
            fg=self.styles["button_fg"],
        )
        create_btn.pack(side="left", padx=10)

        refresh_btn = tk.Button(
            control_frame,
            text="Refresh",
            command=lambda: asyncio.create_task(self._handle_refresh()),
            font=("Arial", 12),
            bg=self.styles["button_bg"],
            fg=self.styles["button_fg"],
        )
        refresh_btn.pack(side="left", padx=10)

    def update_room_list(self, rooms: List[Dict[str, Any]]):
        self.rooms = rooms

        # Clear existing rooms
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for room in rooms:
            self._create_room_row(room)

    def _create_room_row(self, room: Dict[str, Any]):
        row = len(self.scrollable_frame.winfo_children()) // 4

        # Room ID
        tk.Label(
            self.scrollable_frame,
            text=room["room_id"],
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
            anchor="w",
        ).grid(row=row, column=0, padx=5, pady=2, sticky="w")

        # Player Count
        tk.Label(
            self.scrollable_frame,
            text=f"{room['player_count']}/{room['max_players']}",
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
            anchor="w",
        ).grid(row=row, column=1, padx=5, pady=2, sticky="w")

        # Status
        tk.Label(
            self.scrollable_frame,
            text=room["state"],
            bg=self.styles["frame_bg"],
            fg=self.styles["fg_color"],
            anchor="w",
        ).grid(row=row, column=2, padx=5, pady=2, sticky="w")

        # Join Button or Full Label
        if room["player_count"] < room["max_players"]:
            join_button = tk.Button(
                self.scrollable_frame,
                text="Join",
                command=lambda r=room["room_id"]: asyncio.create_task(
                    self._handle_join_room(r)
                ),
                bg=self.styles["button_bg"],
                fg=self.styles["button_fg"],
                width=8,
            )
            join_button.grid(row=row, column=3, padx=5, pady=2, sticky="w")
        else:
            tk.Label(
                self.scrollable_frame,
                text="Full",
                bg=self.styles["frame_bg"],
                fg="red",
                anchor="w",
            ).grid(row=row, column=3, padx=5, pady=2, sticky="w")

    async def _handle_create_room(self):
        if self.on_create_room:
            await self.on_create_room()

    async def _handle_refresh(self):
        if self.on_refresh_rooms:
            await self.on_refresh_rooms()

    async def _handle_join_room(self, room_id: str):
        if self.on_join_room:
            await self.on_join_room(room_id)
