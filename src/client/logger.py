import logging
import sys
from enum import Enum, auto


class LogColor:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


class Direction(Enum):
    SEND = auto()
    RECEIVE = auto()
    EVENT = auto()


class ClientLogger:
    def __init__(self, player_name: str):
        self.logger = logging.getLogger(f"UNOClient-{player_name}")
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        self.logger.addHandler(handler)
        self.player_name = player_name

    def log_message(self, direction: Direction, message_type: str, room_id: str = None):
        match direction:
            case Direction.SEND:
                symbol = "↑"
                color = LogColor.GREEN
            case Direction.RECEIVE:
                symbol = "↓"
                color = LogColor.CYAN
            case Direction.EVENT:
                symbol = "⚡"
                color = LogColor.YELLOW

        room_info = f" [{room_id}]" if room_id else ""
        log_message = f"{color}{symbol} {message_type}{LogColor.END}{room_info}"

        self.logger.info(log_message)

    def log_error(self, message: str):
        self.logger.error(f"{LogColor.RED}✗ {message}{LogColor.END}")

    def log_connection(self, server_url: str, connected: bool = True):
        status = (
            f"{LogColor.GREEN}Connected to"
            if connected
            else f"{LogColor.RED}Disconnected from"
        )
        self.logger.info(f"{status} {server_url}{LogColor.END}")

    def log_game_event(self, event: str):
        self.logger.info(f"{LogColor.PURPLE}◆ {event}{LogColor.END}")
