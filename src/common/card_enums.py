from enum import Enum, auto


class CardType(Enum):
    NUMBER = auto()
    SKIP = auto()
    REVERSE = auto()
    DRAW_TWO = auto()
    WILD = auto()
    WILD_DRAW_FOUR = auto()

    def __str__(self) -> str:
        return self.name


class CardColor(Enum):
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()
    WILD = auto()  # For wild cards

    def __str__(self) -> str:
        return self.name
