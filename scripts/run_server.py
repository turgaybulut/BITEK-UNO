import asyncio
import logging
import os
from server.game_server import GameServer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def run_server():
    port = int(os.environ.get("PORT", 5000))
    server = GameServer(host="0.0.0.0", port=port)
    await server.start()
    try:
        while True:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        await server.stop()


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
