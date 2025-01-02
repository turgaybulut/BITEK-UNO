import tkinter as tk
from src.client.ui.game_ui import UnoGame



if __name__ == "__main__":
    root = tk.Tk()
    game = UnoGame(root)
    root.mainloop()
