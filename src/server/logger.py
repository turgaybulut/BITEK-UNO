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
    INCOMING = auto()
    OUTGOING = auto()


class ServerLogger:
    def __init__(self):
        self.logger = logging.getLogger("UNOServer")
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        self.logger.addHandler(handler)

    def log_message(
        self, direction: Direction, message_type: str, client_id: str = None
    ):
        direction_str = "←" if direction == Direction.INCOMING else "→"
        color = LogColor.CYAN if direction == Direction.INCOMING else LogColor.GREEN

        client_info = f" [{client_id}]" if client_id else ""
        log_message = (
            f"{color}{direction_str} {message_type}{LogColor.END}{client_info}"
        )

        self.logger.info(log_message)

    def log_error(self, message: str):
        self.logger.error(f"{LogColor.RED}✗ {message}{LogColor.END}")

    def log_connection(self, client_id: str, connected: bool = True):
        status = (
            f"{LogColor.GREEN}Connected" if connected else f"{LogColor.RED}Disconnected"
        )
        self.logger.info(f"{status}{LogColor.END} [{client_id}]")


server_logger = ServerLogger()
