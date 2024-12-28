import random
from typing import List, Dict, Any, Optional, Iterator
from common.card import Card
from common.card_enums import CardType, CardColor


class Deck:
    def __init__(self):
        self._cards: List[Card] = []
        self._initialize_deck()

    def _initialize_deck(self) -> None:
        for color in [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]:
            # One zero card per color
            self._cards.append(Card(CardType.NUMBER, color, 0))

            # Two of each number 1-9 per color
            for value in range(1, 10):
                self._cards.extend([Card(CardType.NUMBER, color, value)] * 2)

            # Two of each action card per color
            for card_type in [CardType.SKIP, CardType.REVERSE, CardType.DRAW_TWO]:
                self._cards.extend([Card(card_type, color, -1)] * 2)

        # Four wild cards of each type
        for _ in range(4):
            self._cards.append(Card(CardType.WILD, CardColor.WILD, -1))
            self._cards.append(Card(CardType.WILD_DRAW_FOUR, CardColor.WILD, -1))

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def draw(self) -> Optional[Card]:
        return self._cards.pop() if self._cards else None

    def draw_multiple(self, count: int) -> List[Card]:
        cards = []
        for _ in range(count):
            card = self.draw()
            if card:
                cards.append(card)
            else:
                break
        return cards

    def add_card(self, card: Card) -> None:
        if not isinstance(card, Card):
            raise ValueError("Invalid card object")
        self._cards.append(card)

    def add_cards(self, cards: List[Card]) -> None:
        for card in cards:
            if not isinstance(card, Card):
                raise ValueError("Invalid card object")
        self._cards.extend(cards)

    def merge_pile(self, cards: List[Card], shuffle: bool = True) -> None:
        self.add_cards(cards)
        if shuffle:
            self.shuffle()

    @property
    def remaining(self) -> int:
        return len(self._cards)

    def __iter__(self) -> Iterator[Card]:
        return iter(self._cards)

    def to_dict(self) -> Dict[str, Any]:
        return {"cards": [card.to_dict() for card in self._cards]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Deck":
        try:
            deck = cls()
            deck._cards = [Card.from_dict(card_data) for card_data in data["cards"]]
            return deck
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid deck data: {e}")
