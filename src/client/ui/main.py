import tkinter as tk
import asyncio
from client.game_client import GameClient
from client.ui.game_ui import GameUI
from client.ui_coordinator import UICoordinator


async def main():
    root = tk.Tk()
    game_ui = GameUI(root)
    game_client = GameClient("wss://uno-c57c1b314f2b.herokuapp.com", "")
    ui_coordinator = UICoordinator(game_client, game_ui)

    try:
        while True:
            root.update()
            await asyncio.sleep(0.1)
    except tk.TclError:
        # Window was closed
        await game_client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
