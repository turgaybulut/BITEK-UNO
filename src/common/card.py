from dataclasses import dataclass
from typing import Dict, Any, Optional
from common.card_enums import CardType, CardColor


@dataclass(frozen=True, eq=True)
class Card:
    type: CardType
    color: CardColor
    value: int

    def __post_init__(self):
        if self.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            if self.color != CardColor.WILD:
                raise ValueError("Wild cards must have WILD color")
            if self.value != -1:
                raise ValueError("Wild cards must have value -1")
        elif self.type == CardType.NUMBER:
            if not 0 <= self.value <= 9:
                raise ValueError(f"Number cards must have value 0-9, got {self.value}")
        else:
            if self.value != -1:
                raise ValueError(f"Action cards must have value -1, got {self.value}")
            if self.color == CardColor.WILD:
                raise ValueError("Only wild cards can have WILD color")

    def can_be_played_on(
        self, other: "Card", current_color: Optional[CardColor] = None
    ) -> bool:
        if self.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            return True

        if current_color:
            return self.color == current_color

        return (
            self.color == other.color
            or (
                self.type == other.type
                and self.type == CardType.NUMBER
                and self.value == other.value
            )
            or (self.type == other.type and self.type != CardType.NUMBER)
        )

    def get_score_value(self) -> int:
        if self.type == CardType.NUMBER:
            return self.value
        if self.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            return 50
        return 20

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.name, "color": self.color.name, "value": self.value}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Card":
        try:
            return cls(
                type=CardType[data["type"]],
                color=CardColor[data["color"]],
                value=data["value"],
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid card data: {e}")
