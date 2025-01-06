if animation_active:
        duration = 1

        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) / 1000  # Convert to seconds
        progress = elapsed_time / duration  # Clamp progress to [0, 1]

        # Interpolate card position
        current_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
        current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
        current_pos = (current_x, current_y)

        screen.blit(animate_card_image, current_pos) 

        if progress >= 1:  # Stop animation once it's complete
            animation_active = False
            
    else:
        screen.fill(BACKGROUND_COLOR)
        print_closed_cards(5)
        print_closed_left(4)
        print_closed_right(3)
        print_cards_at_hand(card_images)