# slider.py
# Module for difficulty selection slider
import sys
import pygame

import config as cfg
import state

# Function for the difficulty slider menu
def slider():
    # Define fonts
    font = cfg.menu_styles['btn_font']
    sub_font = cfg.menu_styles['sub_font']
    key_font = cfg.menu_styles['key_font']
    # Pygame clock
    clock    = pygame.time.Clock()
    # Stop music
    pygame.mixer.stop()

    # Slider constants
    MIN_SIZE = 5
    MAX_SIZE = 100
    # Current maze size, clamped to max
    current = max(MIN_SIZE, min(cfg.MAZE_COLS, MAX_SIZE))
    # Slider position and dimensions
    slider_x = 100
    slider_y = 280
    slider_w = 300
    slider_h = 8
    handle_r = 12
    # Confirm button
    confirm_btn = pygame.Rect(175, 360, 150, 50)

    # Function to convert size to slider x position
    def size_to_x(val):
        t = (val - MIN_SIZE) / (MAX_SIZE - MIN_SIZE)
        return int(slider_x + t * slider_w)

    # Function to convert slider x to size
    def x_to_size(x):
        t = (x - slider_x) / slider_w
        return round(MIN_SIZE + t * (MAX_SIZE - MIN_SIZE))

    # Dragging flag
    dragging = False
    running  = True
    # Main loop
    while running:
        # Limit frame rate
        clock.tick(cfg.FPS)
        # Get mouse position
        mouse    = pygame.mouse.get_pos()
        # Calculate handle x
        handle_x = size_to_x(current)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from menu import mainmenu
                    mainmenu(); return
                if event.key == pygame.K_LEFT:
                    current = max(MIN_SIZE, current - 1)
                if event.key == pygame.K_RIGHT:
                    current = min(MAX_SIZE, current + 1)
                if event.key == pygame.K_RETURN:
                    # Set maze size and start game
                    cfg.MAZE_COLS = current
                    cfg.MAZE_ROWS = current
                    from play import main
                    main(); return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if handle clicked
                if abs(mouse[0] - handle_x) <= handle_r + 4 and abs(mouse[1] - slider_y) <= handle_r + 4:
                    dragging = True
                # Check confirm button
                if confirm_btn.collidepoint(mouse):
                    cfg.MAZE_COLS = current
                    cfg.MAZE_ROWS = current
                    from play import main
                    main(); return
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                # Update current size based on mouse
                current = x_to_size(max(slider_x, min(slider_x + slider_w, mouse[0])))

        # Fill screen
        cfg.draw_vertical_gradient(cfg.screen, cfg.THEME['bg_top'], cfg.THEME['bg_bottom'])

        # Render title
        title = font.render("DIFFICULTY", True, cfg.THEME['title'])
        cfg.screen.blit(title, title.get_rect(center=(cfg.WINDOW_W // 2, 80)))

        # Determine difficulty label, color, and reward based on size tier.
        if current == 1:
            diff_label = "Impossible"; diff_col = (220, 75, 75); state.winz = 7
        elif current <= 10:
            diff_label = "Easy";      diff_col = (95, 205, 120); state.winz = 1
        elif current <= 20:
            diff_label = "Medium";    diff_col = (245, 200, 95); state.winz = 2
        elif current <= 40:
            diff_label = "Hard";      diff_col = (245, 155, 95); state.winz = 3
        elif current <= 60:
            diff_label = "Insane";    diff_col = (230, 100, 100); state.winz = 4
        elif current < 75:
            diff_label = "Crazy";     diff_col = (110, 170, 255); state.winz = 5
        else:
            diff_label = "Mentally Unstable"; diff_col = (190, 130, 255); state.winz = 6

        # Override winz if noclip
        if state.noclip == 1:
            state.winz = 0

        # Render difficulty label
        label = font.render(f"{diff_label} ({current}x{current})", True, diff_col)
        cfg.screen.blit(label, label.get_rect(center=(cfg.WINDOW_W // 2, 200)))
        reward_text = sub_font.render(f"Reward: +{state.winz} wins", True, cfg.THEME['muted_text'])
        cfg.screen.blit(reward_text, reward_text.get_rect(center=(cfg.WINDOW_W // 2, 232)))

        # Draw slider background
        pygame.draw.rect(cfg.screen, cfg.THEME['panel_alt'],
                         (slider_x, slider_y - slider_h // 2, slider_w, slider_h), border_radius=4)
        # Draw filled part
        pygame.draw.rect(cfg.screen, diff_col,
                         (slider_x, slider_y - slider_h // 2, handle_x - slider_x, slider_h), border_radius=4)
        # Draw handle
        pygame.draw.circle(cfg.screen, cfg.THEME['title'], (handle_x, slider_y), handle_r)
        pygame.draw.circle(cfg.screen, diff_col, (handle_x, slider_y), handle_r - 3)

        # Draw confirm button
        hover = confirm_btn.collidepoint(mouse)
        cfg.draw_button(cfg.screen, confirm_btn, "Play", "Enter", hover, sub_font, key_font)

        # Render hint text
        hint = sub_font.render("<- -> to adjust | Enter to confirm", True, cfg.THEME['muted_text'])
        cfg.screen.blit(hint, hint.get_rect(center=(cfg.WINDOW_W // 2, 440)))

        # Update display
        pygame.display.flip()
