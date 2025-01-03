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

        self.start_button = self.create_button(
            parent=login_frame,
            text="Start",
            command=self.submit_username,
            name="start_button"
        )
        self.start_button.pack(pady=20)

    def create_button(self, parent, text="Button", command=None, font=("Arial", 12), bg="#27AE60", fg="white", width=15, name=None):
        """
        Creates a button with the given parameters. If parameters are not provided, defaults are used.

        Parameters:
        - parent: Parent widget for the button
        - text: Button text (default: "Button")
        - command: Function to call when the button is clicked (default: None)
        - font: Font for the button text (default: ("Arial", 12))
        - bg: Background color (default: "#27AE60")
        - fg: Foreground (text) color (default: "white")
        - width: Button width (default: 15)
        - name: Name for the button to identify externally (default: None)

        Returns:
        - tk.Button object
        """
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=font,
            bg=bg,
            fg=fg,
            width=width
        )
        if name:
            setattr(self, name, button)
        return button

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
        self.join_buttons = {}
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

            self.join_buttons[room["id"]] = self.create_button(
                parent=rooms_frame,
                text="Join",
                command=lambda r=room["id"]: self.join_specific_room(r),
                name=f"join_button_{room['id']}"
            )
            self.join_buttons[room["id"]].grid(row=i, column=3, padx=10, pady=5)

        # Bottom Buttons
        button_frame = tk.Frame(main_frame, bg="#2C3E50")
        button_frame.pack(pady=20)

        self.create_room_button = self.create_button(
            parent=button_frame,
            text="Create New Room",
            command=self.create_game_room,
            name="create_room_button"
        )
        self.create_room_button.pack(side=tk.LEFT, padx=10)

        self.join_private_room_button = self.create_button(
            parent=button_frame,
            text="Join Private Room",
            command=self.prompt_join_room,
            bg="#2980B9",
            name="join_private_room_button"
        )
        self.join_private_room_button.pack(side=tk.LEFT, padx=10)

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

        # Main Game Area (Pygame Surface) - Left side
        game_area_frame = tk.Frame(game_room_frame, bg="#2C3E50", highlightthickness=2)
        game_area_frame.place(relx=0.02, rely=0.02, relwidth=0.66, relheight=0.96)

        # Placeholder label until Pygame implementation
        self.game_area_label = tk.Label(
            game_area_frame,
            text="Pygame Surface\n(Game Board + Player Hand)",
            font=("Arial", 20),
            bg="#2C3E50",
            fg="white"
        )
        self.game_area_label.pack(expand=True)

        # Chat Box Section with Room Controls - Right side
        chat_box_frame = tk.Frame(game_room_frame, bg="#34495E", highlightthickness=2)
        chat_box_frame.place(relx=0.7, rely=0.02, relwidth=0.28, relheight=0.96)

        # Room info section at top of chat box
        room_info = tk.Frame(chat_box_frame, bg="#2C3E50")
        room_info.pack(fill="x", pady=(5, 0))

        # Room ID display
        self.room_code_label = tk.Label(
            room_info,
            text=f"Room Code: {self.room_code}",
            font=("Arial", 14, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        self.room_code_label.pack(pady=(10, 5))

        # Player count section
        player_frame = tk.Frame(room_info, bg="#2C3E50")
        player_frame.pack(fill="x", pady=(0, 10))

        # Player count display
        self.player_count_label = tk.Label(
            player_frame,
            text="Players: 1/4",  # Default value
            font=("Arial", 12),
            bg="#2C3E50",
            fg="#27AE60"
        )
        self.player_count_label.pack()

        # Add player icons/indicators
        player_icons_frame = tk.Frame(player_frame, bg="#2C3E50")
        player_icons_frame.pack(pady=5)

        self.player_indicators = []
        for i in range(4):
            indicator = tk.Label(
                player_icons_frame,
                text="○",
                font=("Arial", 16),
                bg="#2C3E50",
                fg="#95A5A6",
                padx=5
            )
            indicator.pack(side=tk.LEFT)
            self.player_indicators.append(indicator)

        # Update first indicator to show current player
        self.player_indicators[0].configure(text="●", fg="#27AE60")

        # Chat area
        chat_area_frame = tk.Frame(chat_box_frame, bg="#2C3E50")
        chat_area_frame.pack(fill="both", expand=True, pady=10, padx=5)
        ChatBox.create_chat_area(chat_area_frame)

        # Control buttons at bottom of chat box
        controls_frame = tk.Frame(chat_box_frame, bg="#2C3E50")
        controls_frame.pack(fill="x", pady=10, padx=5)

        self.leave_room_button = self.create_button(
            parent=controls_frame,
            text="Leave Room",
            command=self.init_main_menu,
            bg="#E74C3C",
            name="leave_room_button"
        )
        self.leave_room_button.pack(side=tk.LEFT, padx=5)

        if is_host:
            self.start_button = self.create_button(
                parent=controls_frame,
                text="Start Game",
                command=lambda: self.start_game(self.start_button),
                name="start_game_button"
            )
            self.start_button.pack(side=tk.RIGHT, padx=5)

    def update_player_count(self, count):
        """
        Updates the player count display and indicators

        Parameters:
        count (int): Current number of players in the room
        """
        if hasattr(self, 'player_count_label'):
            self.player_count_label.config(text=f"Players: {count}/4")

            for i in range(4):
                if i < count:
                    self.player_indicators[i].configure(text="●", fg="#27AE60")
                else:
                    self.player_indicators[i].configure(text="○", fg="#95A5A6")

    def start_game(self, start_button):
        """
        Starts the game and hides the Start Game button.
        """
        messagebox.showinfo("Game Started", "The game has begun!")
        print("Game logic to be implemented.")
        start_button.destroy()

    def show_game_end_screen(self, won=False):
        """Show the game end screen"""
        self.clear_screen()
        self.setup_background()

        end_frame = tk.Frame(self.root, bg="#2C3E50", highlightthickness=2)
        end_frame.place(relx=0.3, rely=0.3, relwidth=0.4, relheight=0.4)

        result_text = "You Win!" if won else "You Lost!"
        result_color = "#27AE60" if won else "#E74C3C"

        self.result_label = self.create_label(
            parent=end_frame,
            text=result_text,
            font=("Arial", 36, "bold"),
            bg="#2C3E50",
            fg=result_color,
            name="result_label"
        )
        self.result_label.pack(pady=40)

        self.return_button = self.create_button(
            parent=end_frame,
            text="Return to Lobby",
            command=self.init_main_menu,
            bg="#3498DB",
            name="return_button"
        )
        self.return_button.pack(pady=20)

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
        room_id = simpledialog.askstring("Join Room", "Enter the Room ID:")
        if room_id:
            self.join_private_room(room_id)
