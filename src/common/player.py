from typing import List, Dict, Any, Optional, Iterator
from common.card import Card
from common.card_enums import CardColor


class Player:
    def __init__(self, player_id: str, name: str):
        self._player_id: str = player_id
        self._name: str = name
        self._hand: List[Card] = []
        self._is_connected: bool = True
        self._score: int = 0

    @property
    def player_id(self) -> str:
        return self._player_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def hand(self) -> List[Card]:
        return self._hand.copy()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value: bool):
        self._is_connected = value

    @property
    def score(self) -> int:
        return self._score

    def add_card(self, card: Card) -> None:
        if not isinstance(card, Card):
            raise ValueError("Invalid card object")
        self._hand.append(card)

    def add_cards(self, cards: List[Card]) -> None:
        for card in cards:
            self.add_card(card)

    def remove_card(self, card: Card) -> None:
        try:
            self._hand.remove(card)
        except ValueError:
            raise ValueError("Card not found in player's hand")

    def get_valid_plays(
        self, top_card: Card, current_color: Optional[CardColor] = None
    ) -> List[Card]:
        return [
            card
            for card in self._hand
            if card.can_be_played_on(top_card, current_color)
        ]

    def has_playable_card(
        self, top_card: Card, current_color: Optional[CardColor] = None
    ) -> bool:
        return any(
            card.can_be_played_on(top_card, current_color) for card in self._hand
        )

    def calculate_score(self) -> int:
        return sum(card.get_score_value() for card in self._hand)

    def update_score(self) -> None:
        self._score += self.calculate_score()

    def card_count(self) -> int:
        return len(self._hand)

    def clear_hand(self) -> None:
        self._hand.clear()

    def __iter__(self) -> Iterator[Card]:
        return iter(self._hand)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self._player_id,
            "name": self._name,
            "hand": [card.to_dict() for card in self._hand],
            "is_connected": self._is_connected,
            "score": self._score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        try:
            player = cls(player_id=data["player_id"], name=data["name"])
            player._is_connected = data["is_connected"]
            player._score = data["score"]
            player._hand = [Card.from_dict(card_data) for card_data in data["hand"]]
            return player
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid player data: {e}")
