import tkinter as tk
import asyncio
from tkinter import messagebox
from typing import Callable, Optional, Coroutine, Any, List, Dict
from client.ui.room_selection_section import RoomSelectionSection
from client.ui.game_room_section import GameRoomSection
from common.card import Card
from common.card_enums import CardColor


class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UNO Game")
        self.root.state("zoomed")

        self.on_login: Optional[Callable[[str], Coroutine]] = None
        self.on_create_room: Optional[Callable[[], Coroutine]] = None
        self.on_join_room: Optional[Callable[[str], Coroutine]] = None
        self.on_leave_room: Optional[Callable[[], Coroutine]] = None
        self.on_refresh_rooms: Optional[Callable[[], Coroutine]] = None
        self.on_start_game: Optional[Callable[[], None]] = None
        self.on_chat_message: Optional[Callable[[str], Coroutine]] = None
        self.on_card_played: Optional[
            Callable[[Card, Optional[CardColor]], Coroutine]
        ] = None
        self.on_card_drawn: Optional[Callable[[], Coroutine]] = None
        self.on_color_selected: Optional[Callable[[CardColor], Coroutine]] = None

        self.room_selection: Optional[RoomSelectionSection] = None
        self.game_room: Optional[GameRoomSection] = None

        self._setup_styles()
        self.show_login_screen()

    def _setup_styles(self):
        self.styles = {
            "bg_color": "#2C3E50",
            "fg_color": "white",
            "button_bg": "#27AE60",
            "button_fg": "white",
            "error_bg": "#E74C3C",
            "frame_bg": "#34495E",
        }

        self.root.configure(bg=self.styles["bg_color"])

    def show_login_screen(self):
        self._clear_window()

        login_frame = tk.Frame(
            self.root, bg=self.styles["bg_color"], highlightthickness=2
        )
        login_frame.place(relx=0.3, rely=0.3, relwidth=0.4, relheight=0.4)

        tk.Label(
            login_frame,
            text="Welcome to UNO!",
            font=("Arial", 24, "bold"),
            bg=self.styles["bg_color"],
            fg=self.styles["fg_color"],
        ).pack(pady=20)

        tk.Label(
            login_frame,
            text="Enter your username:",
            font=("Arial", 14),
            bg=self.styles["bg_color"],
            fg=self.styles["fg_color"],
        ).pack(pady=10)

        self.username_entry = tk.Entry(
            login_frame, font=("Arial", 14), justify="center"
        )
        self.username_entry.pack(pady=10)

        login_button = tk.Button(
            login_frame,
            text="Login",
            command=lambda: asyncio.create_task(self._handle_login()),
            font=("Arial", 12),
            bg=self.styles["button_bg"],
            fg=self.styles["button_fg"],
            width=15,
        )
        login_button.pack(pady=20)

        self.username_entry.bind(
            "<Return>", lambda e: asyncio.create_task(self._handle_login())
        )
        self.username_entry.focus_set()

    async def _handle_login(self):
        username = self.username_entry.get().strip()
        if not username:
            self.show_error("Please enter a username")
            return

        if self.on_login:
            await self.on_login(username)

    def show_error(self, message: str):
        messagebox.showerror("Error", message)

    def show_info(self, message: str):
        messagebox.showinfo("Info", message)

    def show_connection_lost(self):
        self.show_error("Connection to server lost!")
        self.show_login_screen()

    def show_room_selection(self):
        self._clear_window()
        self.room_selection = RoomSelectionSection(self.root, self.styles)
        self.room_selection.on_create_room = self.on_create_room
        self.room_selection.on_join_room = self.on_join_room
        self.room_selection.on_refresh_rooms = self.on_refresh_rooms

    def update_room_list(self, rooms: List[Dict[str, Any]]):
        if self.room_selection:
            self.room_selection.update_room_list(rooms)

    def show_game_room(self, is_host: bool = False):
        self._clear_window()
        self.game_room = GameRoomSection(self.root, self.styles, is_host)
        self.game_room.on_leave_room = self.on_leave_room
        self.game_room.on_start_game = self.on_start_game
        self.game_room.on_chat_message = self.on_chat_message
        self.game_room.chat_box.on_message_sent = self.on_chat_message
        self.game_room.on_card_played = self.on_card_played
        self.game_room.on_card_drawn = self.on_card_drawn
        self.game_room.on_color_selected = self.on_color_selected

    def add_chat_message(self, player_name: str, message: str, timestamp: float = None):
        if self.game_room and self.game_room.chat_box:
            self.game_room.chat_box.add_message(player_name, message, timestamp)

    def add_system_message(self, message: str):
        if self.game_room and self.game_room.chat_box:
            self.game_room.chat_box.add_system_message(message)

    def update_game_state(self, game_state: Dict[str, Any]):
        if self.game_room:
            self.game_room.update_game_state(game_state)

    def show_winner(self, winner_name: str):
        if self.game_room:
            self.game_room.show_winner(winner_name)
            self.show_info(f"{winner_name} has won the game!")

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        if self.room_selection:
            self.room_selection = None
        if self.game_room:
            self.game_room = None

    def set_on_login(self, callback: Callable[[str], Coroutine]):
        self.on_login = callback

    def set_on_create_room(self, callback: Callable[[], Coroutine]):
        self.on_create_room = callback

    def set_on_join_room(self, callback: Callable[[str], Coroutine]):
        self.on_join_room = callback

    def set_on_leave_room(self, callback: Callable[[], Coroutine]):
        self.on_leave_room = callback

    def set_on_start_game(self, callback: Callable[[], Coroutine]):
        self.on_start_game = callback

    def set_on_refresh_rooms(self, callback: Callable[[], Coroutine]):
        self.on_refresh_rooms = callback

    def set_on_chat_message(self, callback: Callable[[str], Coroutine]):
        self.on_chat_message = callback

    def set_on_card_played(
        self, callback: Callable[[Card, Optional[CardColor]], Coroutine]
    ):
        self.on_card_played = callback

    def set_on_card_drawn(self, callback: Callable[[], Coroutine]):
        self.on_card_drawn = callback

    def set_on_color_selected(self, callback: Callable[[CardColor], Coroutine]):
        self.on_color_selected = callback
