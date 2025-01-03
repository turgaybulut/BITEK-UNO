import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
import random
from src.client.ui.chat_box import ChatBox
from src.client.ui.game_board import GameBoard
from src.client.ui.player_hand import PlayerHand



class UnoGame:
    def __init__(self, root):
        self.root = root
        self.root.title("UNO Game")
        self.root.geometry("1024x700")
        self.username = ""

        self.game_rooms = [
            {"id": "1234", "players": 2, "max_players": 4, "status": "Waiting"},
            {"id": "5678", "players": 1, "max_players": 4, "status": "Waiting"},
            {"id": "9012", "players": 3, "max_players": 4, "status": "Waiting"}
        ]

        self.init_login_screen()

    def setup_background(self):
        try:
            bg_image = Image.open("../../resources/background.png")
            bg_image = bg_image.resize((1024, 768), Image.Resampling.LANCZOS)
            self.bg_image_tk = ImageTk.PhotoImage(bg_image)
            self.bg_label = tk.Label(self.root, image=self.bg_image_tk)
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"Could not load background image: {e}")
            self.root.configure(bg="#2C3E50")

    def init_login_screen(self):
        """Initialize the username input screen"""
        self.clear_screen()
        self.setup_background()

        login_frame = tk.Frame(self.root, bg="#2C3E50", highlightthickness=2)
        login_frame.place(relx=0.3, rely=0.3, relwidth=0.4, relheight=0.4)

        title = tk.Label(
            login_frame,
            text="Welcome to UNO!",
            font=("Arial", 24, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        title.pack(pady=20)

        username_label = tk.Label(
            login_frame,
            text="Enter your username:",
            font=("Arial", 14),
            bg="#2C3E50",
            fg="white"
        )
        username_label.pack(pady=10)

        self.username_entry = tk.Entry(
            login_frame,
            font=("Arial", 14),
            justify='center'
        )
        self.username_entry.pack(pady=10)

        submit_button = tk.Button(
            login_frame,
            text="Start",
            command=self.submit_username,
            font=("Arial", 14),
            bg="#27AE60",
            fg="white",
            width=15
        )
        submit_button.pack(pady=20)

    def submit_username(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return

        self.username = username
        self.init_main_menu()

    def init_main_menu(self):
        """
        Initializes the main menu of the UNO game.
        """
        self.clear_screen()
        self.setup_background()

        # Main Frame
        main_frame = tk.Frame(self.root, bg="#2C3E50", highlightthickness=2)
        main_frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

        # Title
        title = tk.Label(
            main_frame,
            text="Welcome to UNO!",
            font=("Arial", 36, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        title.pack(pady=30)

        # Game Rooms Section
        rooms_frame = tk.Frame(main_frame, bg="#34495E", padx=20, pady=20)
        rooms_frame.pack(expand=True, fill="both", padx=50)

        # Headers for Game Room List
        headers = ["Room ID", "Players", "Status", "Action"]
        for i, header in enumerate(headers):
            tk.Label(
                rooms_frame,
                text=header,
                font=("Arial", 12, "bold"),
                bg="#34495E",
                fg="white"
            ).grid(row=0, column=i, padx=10, pady=5, sticky="w")

        # Display Game Rooms
        for i, room in enumerate(self.game_rooms, 1):
            tk.Label(
                rooms_frame,
                text=room["id"],
                font=("Arial", 12),
                bg="#34495E",
                fg="white"
            ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

            tk.Label(
                rooms_frame,
                text=f"{room['players']}/{room['max_players']}",
                font=("Arial", 12),
                bg="#34495E",
                fg="white"
            ).grid(row=i, column=1, padx=10, pady=5, sticky="w")

            tk.Label(
                rooms_frame,
                text=room["status"],
                font=("Arial", 12),
                bg="#34495E",
                fg="white"
            ).grid(row=i, column=2, padx=10, pady=5, sticky="w")

            tk.Button(
                rooms_frame,
                text="Join",
                command=lambda r=room["id"]: self.join_specific_room(r),  # Join logic
                bg="#27AE60",
                fg="white"
            ).grid(row=i, column=3, padx=10, pady=5)

        # Bottom Buttons
        button_frame = tk.Frame(main_frame, bg="#2C3E50")
        button_frame.pack(pady=20)

        # Create Room Button
        tk.Button(
            button_frame,
            text="Create New Room",
            font=("Arial", 12),
            command=self.create_game_room,  # Create Room Logic
            bg="#27AE60",
            fg="white",
            width=20
        ).pack(side=tk.LEFT, padx=10)

        # Join Private Room Button
        tk.Button(
            button_frame,
            text="Join Private Room",
            font=("Arial", 12),
            command=self.prompt_join_room,  # Join Private Room Logic
            bg="#2980B9",
            fg="white",
            width=20
        ).pack(side=tk.LEFT, padx=10)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def init_game_room(self, is_host=False):
        """
        Initializes the game room interface.
        """
        self.clear_screen()

        # Create the main container for the game room
        game_room_frame = tk.Frame(self.root, bg="#34495E")
        game_room_frame.place(relwidth=1, relheight=1)

        # Top Section for Room Info
        top_frame = tk.Frame(game_room_frame, bg="#34495E")
        top_frame.place(relx=0.05, rely=0.02, relwidth=0.9, relheight=0.1)

        # Display Room ID
        tk.Label(
            top_frame,
            text=f"Room ID: {self.room_code}",
            font=("Arial", 16),
            bg="#34495E",
            fg="white"
        ).pack()

        # Game Board Section
        game_board = tk.Frame(game_room_frame, bg="#2C3E50", highlightthickness=2)
        game_board.place(relx=0.05, rely=0.05, relwidth=0.6, relheight=0.8)
        GameBoard.create_game_board(game_board)

        # Chat Box Section
        chat_box_frame = tk.Frame(game_room_frame, bg="#34495E", highlightthickness=2)
        chat_box_frame.place(relx=0.7, rely=0.05, relwidth=0.25, relheight=0.8)
        ChatBox.create_chat_area(chat_box_frame)

        # Player Hand Section
        hand_frame = tk.Frame(game_room_frame, bg="#34495E", highlightthickness=2)
        hand_frame.place(relx=0.05, rely=0.85, relwidth=0.9, relheight=0.1)
        PlayerHand.create_hand_area(hand_frame)

        # Buttons for game room actions
        tk.Button(
            game_room_frame,
            text="Leave Room",
            command=self.init_main_menu,  # Go back to the main menu
            font=("Arial", 12),
            bg="#E74C3C",
            fg="white"
        ).place(relx=0.85, rely=0.9)

        if is_host:
            start_button = tk.Button(
                game_room_frame,
                text="Start Game",
                command=lambda: self.start_game(start_button),
                font=("Arial", 12),
                bg="#27AE60",
                fg="white"
            )
            start_button.place(relx=0.7, rely=0.9)

    # bunların yeri burası değil!!!
    def start_game(self, start_button):
        """
        Starts the game and hides the Start Game button.
        """
        messagebox.showinfo("Game Started", "The game has begun!")
        print("Game logic to be implemented.")
        start_button.destroy()

    def create_game_room(self):
        self.room_code = str(random.randint(1000, 9999))
        self.init_game_room(is_host=True)

    def join_specific_room(self, room_id):
        self.room_code = room_id
        self.init_game_room()

    def join_private_room(self, room_id):
        """
        Joins a specific room if it exists.
        """
        room = next((r for r in self.game_rooms if r["id"] == room_id), None)
        if room:
            self.room_code = room_id
            self.init_game_room()
        else:
            messagebox.showerror("Error", "Room not found!")

    def prompt_join_room(self):
        """
        Prompts the user for a room ID and attempts to join it.
        """
        room_id = tk.simpledialog.askstring("Join Room", "Enter the Room ID:")
        if room_id:
            self.join_private_room(room_id)