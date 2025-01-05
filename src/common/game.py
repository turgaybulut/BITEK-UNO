from typing import List, Dict, Any, Optional
from uuid import uuid4
from enum import Enum, auto
from common.card import Card, CardType, CardColor
from common.player import Player
from common.deck import Deck


class GameState(Enum):
    WAITING = auto()  # Waiting for players to join
    PLAYING = auto()  # Game is in progress
    FINISHED = auto()  # Game has ended


class GameError(Exception):
    pass


class Game:
    INITIAL_CARDS_PER_PLAYER = 7
    MIN_PLAYERS = 2
    MAX_PLAYERS = 4

    def __init__(self, game_id: str = None):
        self._game_id = game_id or str(uuid4())
        self._players: List[Player] = []
        self._deck = Deck()
        self._discard_pile: List[Card] = []
        self._current_player_index = 0
        self._direction_clockwise = True
        self._state = GameState.WAITING
        self._current_color = None  # Set when a wild card is played

    @property
    def game_id(self) -> str:
        return self._game_id

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def current_player(self) -> Optional[Player]:
        if not self._players:
            return None
        return self._players[self._current_player_index]

    @property
    def current_color(self) -> Optional[CardColor]:
        if not self._discard_pile:
            return None
        return self._current_color or self._discard_pile[-1].color

    def add_player(self, player: Player) -> None:
        if self._state != GameState.WAITING:
            raise GameError("Cannot add player: game has already started")
        if len(self._players) >= self.MAX_PLAYERS:
            raise GameError("Cannot add player: game is full")
        if any(p.player_id == player.player_id for p in self._players):
            raise GameError("Cannot add player: player ID already exists")

        self._players.append(player)

    def remove_player(self, player_id: str) -> None:
        if self._state == GameState.PLAYING:
            # Just mark the player as disconnected during gameplay
            for player in self._players:
                if player.player_id == player_id:
                    player.is_connected = False
                    break
            return

        self._players = [p for p in self._players if p.player_id != player_id]

    def start_game(self) -> None:
        if self._state != GameState.WAITING:
            raise GameError("Game has already started")
        if len(self._players) < self.MIN_PLAYERS:
            raise GameError(f"Need at least {self.MIN_PLAYERS} players to start")

        # Initialize the game
        self._deck.shuffle()

        # Deal initial cards to players
        for player in self._players:
            cards = self._deck.draw_multiple(self.INITIAL_CARDS_PER_PLAYER)
            player.add_cards(cards)

        # Place first card on discard pile (but not a wild card)
        initial_card = self._deck.draw()
        while initial_card and initial_card.type in [
            CardType.WILD,
            CardType.WILD_DRAW_FOUR,
        ]:
            self._deck.add_card(initial_card)
            self._deck.shuffle()
            initial_card = self._deck.draw()

        if initial_card:
            self._discard_pile.append(initial_card)
            self._current_color = initial_card.color

        self._state = GameState.PLAYING
        self._current_player_index = 0
        self._direction_clockwise = True

    def play_card(
        self, player_id: str, card: Card, chosen_color: Optional[CardColor] = None
    ) -> None:
        if self._state != GameState.PLAYING:
            raise GameError("Game is not in progress")

        if self.current_player.player_id != player_id:
            raise GameError("Not your turn")

        if not self.is_valid_play(card):
            raise GameError("Invalid card play")

        self.current_player.remove_card(card)
        self._discard_pile.append(card)

        if card.type not in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
            self._current_color = None

        match card.type:
            case CardType.SKIP:
                self.skip_turn()
            case CardType.REVERSE:
                self._direction_clockwise = not self._direction_clockwise
                if len(self._players) == 2:  # In 2-player game, reverse acts as skip
                    self.skip_turn()
            case CardType.DRAW_TWO:
                next_player = self._get_next_player()
                drawn_cards = self._deck.draw_multiple(2)
                next_player.add_cards(drawn_cards)
                self.skip_turn()
            case CardType.WILD_DRAW_FOUR:
                if not chosen_color:
                    raise GameError("Must specify color for wild card")
                self._current_color = chosen_color
                next_player = self._get_next_player()
                drawn_cards = self._deck.draw_multiple(4)
                next_player.add_cards(drawn_cards)
                self.skip_turn()
            case CardType.WILD:
                if not chosen_color:
                    raise GameError("Must specify color for wild card")
                self._current_color = chosen_color

        if self.current_player.card_count() == 0:
            self._state = GameState.FINISHED
        else:
            self._advance_turn()

    def draw_card(self, player_id: str) -> Optional[Card]:
        if self._state != GameState.PLAYING:
            raise GameError("Game is not in progress")

        if self.current_player.player_id != player_id:
            raise GameError("Not your turn")

        card = self._deck.draw()
        if not card and len(self._discard_pile) > 1:
            top_card = self._discard_pile.pop()
            self._deck.add_cards(self._discard_pile)
            self._discard_pile = [top_card]
            self._deck.shuffle()
            card = self._deck.draw()

        if card:
            self.current_player.add_card(card)

        self._advance_turn()
        return card

    def skip_turn(self) -> None:
        if self._state == GameState.PLAYING:
            self._advance_turn()

    def is_valid_play(self, card: Card) -> bool:
        if not self._discard_pile:
            return True

        top_card = self._discard_pile[-1]

        return card.can_be_played_on(top_card, self._current_color)

    def get_game_state(self) -> Dict[str, Any]:
        return {
            "game_id": self._game_id,
            "state": self._state.name,
            "current_player_index": self._current_player_index,
            "current_player_id": self.current_player.player_id,
            "direction_clockwise": self._direction_clockwise,
            "current_color": self._current_color.name if self._current_color else None,
            "top_card": (
                self._discard_pile[-1].to_dict() if self._discard_pile else None
            ),
            "deck_count": self._deck.remaining,
            "players": [
                {
                    "id": player.player_id,
                    "name": player.name,
                    "card_count": player.card_count(),
                    "is_connected": player.is_connected,
                }
                for player in self._players
            ],
        }

    def get_player_view(self, player_id: str) -> Dict[str, Any]:
        state = self.get_game_state()
        player = next((p for p in self._players if p.player_id == player_id), None)
        if player:
            state["hand"] = [card.to_dict() for card in player.hand]
        return state

    def get_winner(self) -> Optional[Player]:
        if self._state == GameState.FINISHED:
            for player in self._players:
                if player.card_count() == 0:
                    return player
        return None

    def _advance_turn(self) -> None:
        if self._direction_clockwise:
            self._current_player_index = (self._current_player_index + 1) % len(
                self._players
            )
        else:
            self._current_player_index = (self._current_player_index - 1) % len(
                self._players
            )

    def _get_next_player(self) -> Player:
        if self._direction_clockwise:
            next_index = (self._current_player_index + 1) % len(self._players)
        else:
            next_index = (self._current_player_index - 1) % len(self._players)
        return self._players[next_index]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_id": self._game_id,
            "players": [p.to_dict() for p in self._players],
            "deck": self._deck.to_dict(),
            "discard_pile": [card.to_dict() for card in self._discard_pile],
            "current_player_index": self._current_player_index,
            "current_player_id": self.current_player.player_id,
            "direction_clockwise": self._direction_clockwise,
            "state": self._state.name,
            "current_color": self._current_color.name if self._current_color else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Game":
        game = cls(game_id=data["game_id"])
        game._players = [Player.from_dict(p) for p in data["players"]]
        game._deck = Deck.from_dict(data["deck"])
        game._discard_pile = [Card.from_dict(c) for c in data["discard_pile"]]
        game._current_player_index = data["current_player_index"]
        game._direction_clockwise = data["direction_clockwise"]
        game._state = GameState[data["state"]]
        game._current_color = (
            CardColor[data["current_color"]] if data["current_color"] else None
        )
        return game
