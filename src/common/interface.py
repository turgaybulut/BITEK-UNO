import pygame
import sys
# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
# bunları env variable yapmak daha güzel olabilir.
CARD_WIDTH, CARD_HEIGHT = 100, 150
BACKGROUND_COLOR = (34, 139, 34)  # Green background

def animate_card(start, end, duration, elapsed_time):
    """Interpolates the position of the card."""
    progress = min(elapsed_time / duration, 1)  # Clamp progress to [0, 1]
    current_x = start[0] + (end[0] - start[0]) * progress
    current_y = start[1] + (end[1] - start[1]) * progress
    return current_x, current_y, progress



def load_cards_at_hand():
    '''
    This should get the cards as a dictionary from the server.
    I am uploading some example cards for now.
    The real implementation should follow this dictionary structure.
    However, pos_x & pos_y don't matter, they are reassigned later anyways.
    '''
    card_images = [
        {"image": pygame.image.load(
            "src/cards/1.png"), "pos_x": 50, "pos_y": SCREEN_HEIGHT // 2 + CARD_HEIGHT // 2},
        {"image": pygame.image.load(
            "src/cards/2.png"), "pos_x": 20, "pos_y": SCREEN_HEIGHT // 2 + CARD_HEIGHT // 2},
    ]
    for card in card_images:
        card["image"] = pygame.transform.scale(
            card["image"], (CARD_WIDTH, CARD_HEIGHT))
    return card_images

card_images = load_cards_at_hand()

def clicked_on_card(card):
    print(f"clicked on card with position{card["pos_x"], card["pos_y"]}")
    card_images.remove(card) #elden çıkıyor sonuçta!
    return card


def load_closed_card():  # I dunno this approach with two load methods makes sense :p
    closed_card = {"image": pygame.image.load(
        "src/cards/closed.png"), "pos_x": 50, "pos_y": SCREEN_HEIGHT // 2 + CARD_HEIGHT // 2}
    closed_card["image"] = pygame.transform.scale(
        closed_card["image"], (CARD_WIDTH, CARD_HEIGHT))
    return closed_card


def print_cards_at_hand(card_images):
    y = SCREEN_HEIGHT - CARD_HEIGHT *4 // 3  # fixed for cards at hand
    for i, card in enumerate(card_images):
        # Spacing between cards, this will become important!
        x = SCREEN_WIDTH//3 + i * (CARD_WIDTH + 20)
        card["pos_x"] = x
        card["pos_y"] = y
        # this prints to the screen with a tuple
        screen.blit(card["image"], (card["pos_x"], card["pos_y"]))


def print_closed_cards(number_of_cards):  # give closed card to this.
    card = load_closed_card()
    y = CARD_HEIGHT // 4
    for i in range(number_of_cards):
        
        #rotated_width, rotated_height = rotated_card.get_size()

        # Spacing between cards, this will become important!
        x = SCREEN_WIDTH//3 + i * (CARD_WIDTH - 80)
        card["pos_x"] = x
        card["pos_y"] = y
        # this prints to the screen with a tuple
        screen.blit(card["image"], (card["pos_x"], card["pos_y"]))

def print_closed_left(number_of_cards):
    card = load_closed_card()
    card["image"] = pygame.transform.rotate(card["image"], 270)  # 90 degrees clockwise
    x = CARD_HEIGHT // 3
    for i in range(number_of_cards):
        #rotated_width, rotated_height = rotated_card.get_size()

        # Spacing between cards, this will become important!
        y = SCREEN_HEIGHT//3 + i * (CARD_WIDTH - 80)
        card["pos_x"] = x
        card["pos_y"] = y
        # this prints to the screen with a tuple
        screen.blit(card["image"], (card["pos_x"], card["pos_y"]))

def print_closed_right(number_of_cards):
    card = load_closed_card()
    card["image"] = pygame.transform.rotate(card["image"], 90)  # 90 degrees clockwise
    x = SCREEN_WIDTH - CARD_HEIGHT - CARD_HEIGHT//3  
    for i in range(number_of_cards):
        #rotated_width, rotated_height = rotated_card.get_size()

        # Spacing between cards, this will become important!
        y = SCREEN_HEIGHT//3 + i * (CARD_WIDTH - 80)
        card["pos_x"] = x
        card["pos_y"] = y
        # this prints to the screen with a tuple
        screen.blit(card["image"], (card["pos_x"], card["pos_y"]))



# Initialize pygame
pygame.init()


# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Card Game")

# Load card images and assign positions



# Scale images to a consistent size


# Main game loop
animation_active = False
animation_card_image = None #load_closed_card["image"]
running = True
clock = pygame.time.Clock()

while running:  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # Detect mouse click
            mouse_pos = pygame.mouse.get_pos()  # Get mouse position
            for card in card_images:
                # Get card rect
                card_rect = pygame.Rect(
                    card["pos_x"], card["pos_y"], CARD_WIDTH, CARD_HEIGHT)
                # Check if mouse clicked on card
                if card_rect.collidepoint(mouse_pos):
                    clicked_on_card(card)
                    animation_active = True
                    start_pos = [card["pos_x"], card["pos_y"]]
                    end_pos = [SCREEN_WIDTH // 2 - CARD_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2]
                    animate_card_image = card["image"]
                    start_time = pygame.time.get_ticks()
                    
    screen.fill(BACKGROUND_COLOR)
    print_closed_cards(5)
    print_closed_left(4)
    print_closed_right(3)

    if animation_active:
        duration = 1
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) / 1000  # Convert to seconds
        current_x, current_y, progress = animate_card(start_pos, end_pos, duration, elapsed_time)
        current_pos = (current_x, current_y)
        screen.blit(animate_card_image, current_pos) 

        if progress >= 1:  # Stop animation once it's complete
            animation_active = False
            
    else:
        print_cards_at_hand(card_images)
            

    

    # Update the display
    pygame.display.flip()
    clock.tick(60)
# Quit pygame
pygame.quit()
sys.exit()
