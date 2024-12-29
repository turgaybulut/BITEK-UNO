from common.game import Game, GameState
from common.player import Player
from common.card_enums import CardType, CardColor


def print_player_hands(game: Game):
    for player in game._players:
        print(f"\n{player.name}'s hand:")
        for card in player.hand:
            print(f"  {card.color} {card.type} {card.value}")


def print_game_state(game: Game):
    print("\nGame State:")
    print(f"Current Player: {game.current_player.name}")
    print(
        f"Direction: {'Clockwise' if game._direction_clockwise else 'Counter-Clockwise'}"
    )
    if game._discard_pile:
        top_card = game._discard_pile[-1]
        print(f"Top Card: {top_card.color} {top_card.type} {top_card.value}")
    if game._current_color:
        print(f"Current Color: {game._current_color}")
    print(f"Deck Cards Remaining: {game._deck.remaining}")


def main():
    game = Game()

    players = [
        Player("1", "Alice"),
        Player("2", "Bob"),
        Player("3", "Charlie"),
        Player("4", "David"),
    ]

    for player in players:
        game.add_player(player)

    print("Starting game...")
    game.start_game()

    print_game_state(game)
    print_player_hands(game)

    while True:
        current_player = game.current_player
        print(f"\n{current_player.name}'s turn")

        valid_plays = current_player.get_valid_plays(
            game._discard_pile[-1], game._current_color
        )

        if valid_plays:
            print("Valid plays:")
            for i, card in enumerate(valid_plays):
                print(f"{i}: {card.color} {card.type} {card.value}")

            choice = input("Choose a card to play (number) or 'd' to draw: ")

            if choice.lower() == "d":
                drawn_card = game.draw_card(current_player.player_id)
                if drawn_card:
                    print(
                        f"Drew: {drawn_card.color} {drawn_card.type} {drawn_card.value}"
                    )
            else:
                try:
                    card_to_play = valid_plays[int(choice)]
                    if card_to_play.type in [CardType.WILD, CardType.WILD_DRAW_FOUR]:
                        color_choice = input("Choose color (RED/BLUE/GREEN/YELLOW): ")
                        chosen_color = CardColor[color_choice.upper()]
                        game.play_card(
                            current_player.player_id, card_to_play, chosen_color
                        )
                    else:
                        game.play_card(current_player.player_id, card_to_play)
                except (ValueError, IndexError):
                    print("Invalid choice. Drawing a card instead.")
                    game.draw_card(current_player.player_id)
        else:
            print("No valid plays. Drawing a card.")
            game.draw_card(current_player.player_id)

        print_game_state(game)
        print_player_hands(game)

        if game.state == GameState.FINISHED:
            winner = game.get_winner()
            print(f"\nGame Over! {winner.name} wins!")
            break

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
