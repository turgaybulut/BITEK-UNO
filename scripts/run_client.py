import asyncio
from typing import Optional
from client.game_client import GameClient
from client.ui.game_ui import GameUI
from client.ui_coordinator import UICoordinator


class ClientApp:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.game_client: Optional[GameClient] = None
        self.game_ui: Optional[GameUI] = None
        self.ui_coordinator: Optional[UICoordinator] = None
        self.running = False

    async def start(self, player_name: str) -> None:
        self.game_client = GameClient(self.server_url, player_name)
        self.game_ui = GameUI()
        self.ui_coordinator = UICoordinator(self.game_client, self.game_ui)

        if await self.game_client.connect():
            self.running = True
            await self._run()
        else:
            self.game_ui.show_error("Failed to connect to server")
            self.game_ui.show_reconnect_prompt()

    async def stop(self) -> None:
        self.running = False
        if self.game_client:
            await self.game_client.disconnect()

    async def _run(self) -> None:
        try:
            self.game_ui.show()
            while self.running:
                await asyncio.sleep(0.1)
        except Exception as e:
            self.game_ui.show_error(f"Application error: {str(e)}")
        finally:
            await self.stop()


def main():
    server_url = "wss://uno-c57c1b314f2b.herokuapp.com"
    app = ClientApp(server_url)

    try:
        # Get player name from UI or command line
        player_name = input("Enter your name: ")
        asyncio.run(app.start(player_name))
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if app.running:
            asyncio.run(app.stop())


if __name__ == "__main__":
    main()
