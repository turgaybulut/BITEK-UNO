import pygame
import sys

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
CARD_WIDTH, CARD_HEIGHT = 100, 150
BACKGROUND_COLOR = (34, 139, 34)  # Green background

def animate_card(start, end, duration, elapsed_time):
    """Interpolates the position of the card."""
    progress = min(elapsed_time / duration, 1)  # Clamp progress to [0, 1]
    current_x = start[0] + (end[0] - start[0]) * progress
    current_y = start[1] + (end[1] - start[1]) * progress
    return current_x, current_y, progress

def load_cards_at_hand():
    """Loads example cards."""
    card_images = [
        {"image": pygame.image.load("src/cards/1.png"), "pos_x": 50, "pos_y": SCREEN_HEIGHT // 2 + CARD_HEIGHT // 2},
        {"image": pygame.image.load("src/cards/2.png"), "pos_x": 20, "pos_y": SCREEN_HEIGHT // 2 + CARD_HEIGHT // 2},
    ]
    for card in card_images:
        card["image"] = pygame.transform.scale(card["image"], (CARD_WIDTH, CARD_HEIGHT))
    return card_images

def clicked_on_card(card):
    print(f"Clicked on card with position {card['pos_x'], card['pos_y']}")

def print_cards_at_hand(card_images):
    y = SCREEN_HEIGHT - CARD_HEIGHT * 4 // 3  # Fixed for cards at hand
    for i, card in enumerate(card_images):
        x = SCREEN_WIDTH // 3 + i * (CARD_WIDTH + 20)  # Spacing between cards
        card["pos_x"] = x
        card["pos_y"] = y
        screen.blit(card["image"], (card["pos_x"], card["pos_y"]))

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Card Game")

# Load card images
card_images = load_cards_at_hand()

# Animation settings
animation_active = False
animation_card_image = None
start_pos, end_pos = None, None
start_time = None
duration = 1  # Animation duration in seconds

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:  # Detect mouse click
            mouse_pos = pygame.mouse.get_pos()
            for card in card_images:
                card_rect = pygame.Rect(card["pos_x"], card["pos_y"], CARD_WIDTH, CARD_HEIGHT)
                if card_rect.collidepoint(mouse_pos):  # Check if mouse clicked on card
                    clicked_on_card(card)
                    animation_active = True
                    animation_card_image = card["image"]
                    start_pos = [card["pos_x"], card["pos_y"]]
                    end_pos = [SCREEN_WIDTH // 2 - CARD_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2]
                    start_time = pygame.time.get_ticks()

    # Clear the screen
    screen.fill(BACKGROUND_COLOR)

    # Update and draw animation
    if animation_active:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds
        current_x, current_y, progress = animate_card(start_pos, end_pos, duration, elapsed_time)
        screen.blit(animation_card_image, (current_x, current_y))
        if progress >= 1:  # Stop animation once it's complete
            animation_active = False
    else:
        # Draw all cards normally
        print_cards_at_hand(card_images)

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Cap frame rate at 60 FPS

# Quit pygame
pygame.quit()
sys.exit()
