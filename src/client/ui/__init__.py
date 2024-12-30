import tkinter as tk
from PIL import Image, ImageTk

# Create the main window
root = tk.Tk()
root.title("Test GUI")
root.geometry("800x600")

# Load the background image using PIL -> pillow
bg_image = Image.open("../../resources/background.png")

# Resize the image to fit the window size
bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)

# Convert the image to a format tkinter can use
bg_image_tk = ImageTk.PhotoImage(bg_image)

# Create a label to display the background image
bg_label = tk.Label(root, image=bg_image_tk)
bg_label.place(relwidth=1, relheight=1)  # This will make the background cover the entire window

# Create a label over the background
label = tk.Label(root, text="Welcome to UNO!", font=("Arial", 16), bg="white", fg="black")
label.pack(pady=20)

# Function to handle joining a game room
def join_game(game_id):
    print(f"Joining game {game_id}...")  # You can replace this with the server connection logic

# Create a frame to hold the game room buttons (no transparent bg, inherits from root)
game_rooms_frame = tk.Frame(root)
game_rooms_frame.pack(pady=20)

# Create a list of game rooms (replace this with real data later)
game_rooms = ["Game Room 1", "Game Room 2", "Game Room 3", "Game Room 4", "Game Room 5"]

# Create buttons for each game room dynamically
for idx, game in enumerate(game_rooms):
    game_button = tk.Button(game_rooms_frame, text=game, command=lambda idx=idx: join_game(idx), font=("Arial", 12), width=20, height=2)
    game_button.grid(row=idx // 3, column=idx % 3, padx=10, pady=10)  # Grid layout for buttons


friend_game_frame = tk.Frame(root, bg="white", padx=20, pady=20)
friend_game_frame.pack(pady=20)

# enter friend's game ID
friend_label = tk.Label(friend_game_frame, text="Enter Private Game Room ID:", font=("Arial", 12), bg="white", fg="black")
friend_label.pack(pady=5)

game_id_entry = tk.Entry(friend_game_frame, font=("Arial", 12))
game_id_entry.pack(pady=5)

# Function to join a friend's game by ID
def join_friend_game():
    friend_game_id = game_id_entry.get()
    if friend_game_id:  # Check if the input is not empty
        print(f"Joining friend's game with ID {friend_game_id}...")  # Replace this with server logic
    else:
        print("Please enter a valid game ID.")

# a button to join the friend's game room
join_friend_button = tk.Button(friend_game_frame, text="Join Private Game", command=join_friend_game, font=("Arial", 12))
join_friend_button.pack(pady=10)

# a button that closes the application
button = tk.Button(root, text="Return to Desktop", command=root.quit, font=("Arial", 12))
button.pack(side="bottom", pady=10)

# Start the GUI event loop
root.mainloop()
