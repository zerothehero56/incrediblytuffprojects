import sys
import random
import time
import pygame
import os

# Import configuration module for game settings
import config as cfg
# Import saves module for handling game save data
import saves
# Import skins module for player skin management
import skins
# Import sounds module for audio loading and effects
import sounds
# Import state module for global game state variables
import state
# Import maze generation and drawing functions
from maze import generate_maze, draw_maze, grid_index
# Import specific constants from config for screen and game parameters
from config import (screen, WINDOW_W, HUD_H, VIEW_H,
                    FPS, LERP_CAM, LERP_PLAYER, GOAL_COLOR, GOAL_BORDER_COLOR)
# Import slider function for difficulty selection
from slider import slider
# Import mainmenu function for the main menu
from menu import mainmenu


# Function to get the player surface based on equipped skin
def get_player_surf(all_imgs, radius):
    # Call skins.make_player_surf to create the player image surface
    return skins.make_player_surf(saves.equipped_skin, all_imgs, radius)


def maybe_play_step_sound(steps):
    if state.noclip == 0:
        if saves.equipped_skin == "Hillo.png" and steps not in (200, 300) and sounds.sound_fah:
            sounds.sound_fah.play()
        if saves.equipped_skin == "imattheclub.png" and steps not in (200, 300) and sounds.sound_idk:
            sounds.sound_idk.play()
        if saves.equipped_skin == "bart.png" and steps not in (200, 300) and sounds.sound_aycaramba:
            sounds.sound_aycaramba.play()
        if saves.equipped_skin == "lebron.png" and sounds.sound_flight:
            sounds.sound_flight.play()
        if saves.equipped_skin == "dingle.png" and sounds.sound_rizz:
            sounds.sound_rizz.play()
        return

    rando = random.randint(1, 85)
    if 55 <= rando <= 84 and sounds.sound_ankle:
        sounds.sound_ankle.play()
    elif 1 <= rando <= 2 and sounds.sound_talary:
        sounds.sound_talary.play()
    elif 6 <= rando <= 8 and sounds.sound_sike:
        sounds.sound_sike.play()
    elif rando == 11 and sounds.sound_siren:
        sounds.sound_siren.play()
    elif 16 <= rando <= 22 and sounds.sound_weave:
        sounds.sound_weave.play()


def get_win_reward(size):
    if state.noclip == 1:
        return 0
    if size == 1:
        return 7
    if size <= 10:
        return 1
    if size <= 20:
        return 2
    if size <= 40:
        return 3
    if size <= 60:
        return 4
    if size < 75:
        return 5
    return 6


# Function to initialize a new game with given columns and rows
def new_game(cols, rows):
    # Generate the maze grid using the maze module
    grid   = generate_maze(cols, rows)
    # Set initial player position at top-left
    player = [0, 0]
    # Set goal position at bottom-right
    goal   = [cols - 1, rows - 1]
    # Record start time for timing the game
    start_t = time.time()
    # Calculate initial smooth player x position
    spx = float(0 * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
    # Calculate initial smooth player y position
    spy = float(0 * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
    # Calculate initial camera x offset
    csx = float(max(0, spx - cfg.WINDOW_W // 2))
    # Calculate initial camera y offset
    csy = float(max(0, spy - cfg.VIEW_H  // 2))
    # Return all initial game state variables
    return grid, player, goal, start_t, False, 0, False, False, spx, spy, csx, csy


# Main game loop function
def main():
    # Get maze dimensions from config
    cols, rows = cfg.MAZE_COLS, cfg.MAZE_ROWS
    # Create Pygame clock for frame rate control
    clock      = pygame.time.Clock()
    # Create font for HUD text
    font       = pygame.font.SysFont(None, 23)
    # Calculate player radius based on cell size
    radius     = cfg.CELL_SIZE // 3
    # Load all skin images for player customization
    all_imgs   = skins.load_all_skin_images()
    pygame.mixer.stop()

    # Ensure sounds are loaded
    sounds.load_all_sounds()

    # Start background music based on equipped skin
    def get_soundtrack(skin):
        # Return soundtrack file based on skin name
        if skin == "lebron.png":
            return "LebronShine.wav"
        elif skin == "dingle.png":
            return "rizzy.mp3"
        else:
            return "default.mp3"

    # Get the soundtrack file for the current equipped skin
    soundtrack_file = get_soundtrack(saves.equipped_skin)
    # Construct full path to the soundtrack file
    music_path = os.path.join(cfg.SOUNDS_DIR, soundtrack_file)
    # Check if the music file exists and load/play it in a loop
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(saves.bg_volume)

    # Initialize new game state
    (grid, player, goal, start_t, won, steps,
     played_200, played_300, smooth_px, smooth_py, cam_sx, cam_sy) = new_game(cols, rows)

    # Flag to allow winning once per game
    canwin   = True
    # Flag for win sound playback
    winplay  = True
    # Time taken to win
    win_time = 0.0
    earned_wins = 0
    # Get player surface for rendering
    player_surf = get_player_surf(all_imgs, radius)

    def get_win_button_rects():
        card_w, card_h = 420, 220
        card_y = (VIEW_H - card_h) // 2
        btn_w, btn_h = 118, 44
        gap = 10
        total_w = 3 * btn_w + 2 * gap
        bx = (WINDOW_W - total_w) // 2
        by = card_y + 152
        return [
            pygame.Rect(bx + i * (btn_w + gap), by, btn_w, btn_h)
            for i in range(3)
        ]

    # Main game loop flag
    running = True
    # Start the main game loop
    while running:
        # Calculate delta time for smooth animations
        dt = clock.tick(FPS) / 1000.0

        # Event handling loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.stop()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and won:
                win_btn_rects = get_win_button_rects()
                if win_btn_rects[0].collidepoint(event.pos):
                    (grid, player, goal, start_t, won, steps,
                     played_200, played_300, smooth_px, smooth_py,
                     cam_sx, cam_sy) = new_game(cols, rows)
                    canwin = True
                    win_time = 0.0
                    winplay = True
                    earned_wins = 0
                    player_surf = get_player_surf(all_imgs, radius)
                elif win_btn_rects[1].collidepoint(event.pos):
                    pygame.mixer.stop()
                    mainmenu()
                    return
                elif win_btn_rects[2].collidepoint(event.pos):
                    pygame.mixer.stop()
                    slider()
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    (grid, player, goal, start_t, won, steps,
                     played_200, played_300, smooth_px, smooth_py,
                     cam_sx, cam_sy) = new_game(cols, rows)
                    canwin = True
                    winplay = True
                    win_time = 0.0
                    earned_wins = 0
                    player_surf = get_player_surf(all_imgs, radius)
                    continue
                if event.key == pygame.K_ESCAPE:
                    running = False
                    mainmenu()
                    return
                if event.key == pygame.K_q:
                    running = False
                    slider()
                    return
                if not won:
                    col_p, row_p = player
                    moved = False
                    idx = grid_index(col_p, row_p, cols, rows)
                    cur = grid[idx] if idx is not None else None
                    if state.noclip == 0:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            if row_p > 0 and (cur is None or not cur.walls[0]):
                                player[1] -= 1
                                moved = True
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            if row_p < rows - 1 and (cur is None or not cur.walls[2]):
                                player[1] += 1
                                moved = True
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            if col_p > 0 and (cur is None or not cur.walls[3]):
                                player[0] -= 1
                                moved = True
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            if col_p < cols - 1 and (cur is None or not cur.walls[1]):
                                player[0] += 1
                                moved = True
                    else:
                        if event.key in (pygame.K_UP, pygame.K_w) and row_p > 0:
                            player[1] -= 1
                            moved = True
                        elif event.key in (pygame.K_DOWN, pygame.K_s) and row_p < rows - 1:
                            player[1] += 1
                            moved = True
                        elif event.key in (pygame.K_LEFT, pygame.K_a) and col_p > 0:
                            player[0] -= 1
                            moved = True
                        elif event.key in (pygame.K_RIGHT, pygame.K_d) and col_p < cols - 1:
                            player[0] += 1
                            moved = True

                    if moved:
                        steps += 1
                        if saves.step_sounds_enabled and steps == 200 and not played_200:
                            played_200 = True
                            if sounds.sound_200:
                                sounds.sound_200.set_volume(saves.sfx_volume)
                                sounds.sound_200.play()
                        if saves.step_sounds_enabled and steps == 300 and not played_300:
                            played_300 = True
                            if sounds.sound_300:
                                sounds.sound_300.set_volume(saves.sfx_volume)
                                sounds.sound_300.play()
                        maybe_play_step_sound(steps)

                    if player == goal:
                        won = True
                        win_time = time.time() - start_t
                        if canwin:
                            earned_wins = get_win_reward(cols)
                            saves.wins += earned_wins
                            canwin = False
                            saves.save_wins()

        # Smooth player position interpolation
        target_px = float(player[0] * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
        target_py = float(player[1] * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
        tp         = min(1.0, LERP_PLAYER * 60 * dt)
        smooth_px += (target_px - smooth_px) * tp
        smooth_py += (target_py - smooth_py) * tp

        # Calculate maze dimensions in pixels
        maze_pw = cols * cfg.CELL_SIZE
        maze_ph = rows * cfg.CELL_SIZE
        # Calculate target camera position
        tcx     = max(0, min(smooth_px - WINDOW_W // 2, maze_pw - WINDOW_W))
        tcy     = max(0, min(smooth_py - VIEW_H  // 2,  maze_ph - VIEW_H))
        tc      = min(1.0, LERP_CAM * 60 * dt)
        # Interpolate camera position
        cam_sx += (tcx - cam_sx) * tc
        cam_sy += (tcy - cam_sy) * tc

        # Fill screen with background color
        cfg.draw_vertical_gradient(screen, cfg.THEME['bg_top'], cfg.THEME['bg_bottom'])
        # Draw the maze
        draw_maze(screen, grid, cfg.CELL_SIZE, cam_sx, cam_sy)

        # Draw goal rectangle
        gsx = goal[0] * cfg.CELL_SIZE - int(cam_sx)
        gsy = goal[1] * cfg.CELL_SIZE - int(cam_sy)
        pygame.draw.rect(screen, GOAL_COLOR,
                         (gsx + 4, gsy + 4, cfg.CELL_SIZE - 8, cfg.CELL_SIZE - 8))
        pygame.draw.rect(screen, GOAL_BORDER_COLOR,
                 (gsx + 4, gsy + 4, cfg.CELL_SIZE - 8, cfg.CELL_SIZE - 8), 2)

        # Draw player
        draw_px = int(smooth_px - cam_sx)
        draw_py = int(smooth_py - cam_sy)
        if saves.color_change_enabled:
            if steps >= 300:
                player_color = (255, 0, 0)  # red
            elif steps >= 200:
                player_color = (255, 165, 0)  # orange
            else:
                player_color = (255, 255, 0)  # yellow
        else:
            player_color = (255, 255, 0)
        pygame.draw.circle(screen, player_color, (draw_px, draw_py), radius)
        if player_surf:
            screen.blit(player_surf, (draw_px - radius, draw_py - radius))

        # Draw HUD
        elapsed = time.time() - start_t
        pygame.draw.rect(screen, cfg.THEME['panel'], (0, VIEW_H, WINDOW_W, HUD_H))
        pygame.draw.line(screen, cfg.THEME['panel_border'], (0, VIEW_H), (WINDOW_W, VIEW_H), 2)
        hud = font.render(f"Time: {int(elapsed)}s   Steps: {steps}", True, cfg.THEME['button_text'])
        screen.blit(hud, (8, VIEW_H + 9))

        # Handle win screen
        if won:
            # Play win sound once
            if winplay:
                if saves.equipped_skin == "lebron.png":
                    if sounds.sound_cmonman:
                        sounds.sound_cmonman.play()
                elif saves.equipped_skin == "bart.png":
                    if sounds.sound_eatmyshorts:
                        sounds.sound_eatmyshorts.play()
                else:
                    if sounds.sound_win:
                        sounds.sound_win.play()
                winplay = False

            # Draw win overlay
            overlay = pygame.Surface((WINDOW_W, VIEW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            # Define win card dimensions
            card_w, card_h = 420, 220
            card_y = (VIEW_H - card_h) // 2

            # Create fonts for win screen
            title_font = pygame.font.Font(None, 56)
            stat_font  = pygame.font.Font(None, 30)
            btn_font   = pygame.font.Font(None, 26)
            key_font   = pygame.font.Font(None, 20)

            # Render win title
            t = title_font.render("YOU WIN!", True, cfg.THEME['accent'])
            screen.blit(t, t.get_rect(center=(WINDOW_W // 2, card_y + 44)))

            # Render stats
            s1 = stat_font.render(f"Steps: {steps}", True, cfg.THEME['title'])
            s2 = stat_font.render(f"Time:  {int(win_time)}s", True, cfg.THEME['title'])
            s3 = stat_font.render(f"Reward: +{earned_wins} wins", True, cfg.THEME['title'])
            screen.blit(s1, s1.get_rect(center=(WINDOW_W // 2, card_y + 90)))
            screen.blit(s2, s2.get_rect(center=(WINDOW_W // 2, card_y + 118)))
            screen.blit(s3, s3.get_rect(center=(WINDOW_W // 2, card_y + 146)))

            # Get mouse position for button hover
            mouse = pygame.mouse.get_pos()

            # Define win buttons
            win_btn_labels = [("Regenerate", "R"), ("Menu", "Esc"), ("Resize", "Q")]
            win_btn_rects = get_win_button_rects()
            for i, (label, hotkey) in enumerate(win_btn_labels):
                r = win_btn_rects[i]
                hov = r.collidepoint(mouse)
                cfg.draw_button(screen, r, label, hotkey, hov, btn_font, key_font)

        # Update display
        pygame.display.flip()

    # Quit Pygame and exit
    pygame.quit()
    sys.exit()
