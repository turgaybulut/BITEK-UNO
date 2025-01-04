import tkinter as tk
from client.ui.game_ui import GameUI



if __name__ == "__main__":
    root = tk.Tk()
    game = GameUI(root)
    root.mainloop()
