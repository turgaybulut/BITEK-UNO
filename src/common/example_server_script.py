import asyncio
import logging
from server.game_server import GameServer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def run_server():
    server = GameServer(host="0.0.0.0", port=8765)
    await server.start()
    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        await server.stop()


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
