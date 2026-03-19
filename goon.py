import random
import sys
import time
import pygame
import os
import time
# maze game cause sigma

script_dir = os.path.dirname(__file__)
save_path = os.path.join(script_dir, "data.txt")


#skinmenu

screen = pygame.display.set_mode((495, 500))
def skinmenu():
    # --- INITIAL SETTINGS ---
    pygame.init()
    font = pygame.font.Font(None, 30)
    big_font = pygame.font.Font(None, 50)

# Mock Data (In your real game, load these from your save file)
    owned_skins = ["0_Default.png"] 
    equipped_skin = "0_Default.png"

# --- 1. GRAB ALL PNGS FROM FOLDER ---
    skin_list = []
    skin_folder = "skins" # Make sure this folder exists with your PNGs!

    if os.path.exists(skin_folder):
        for filename in sorted(os.listdir(skin_folder)):
            if filename.endswith(".png"):
            # Extract requirement from filename (e.g., "5_Blue.png" -> 5)
                try:
                    requirement = int(filename.split('_')[0])
                except:
                    requirement = 0
            
                img = pygame.image.load(os.path.join(skin_folder, filename)).convert_alpha()
                img = pygame.transform.scale(img, (80, 80)) # Uniform size
                skin_list.append({"name": filename, "img": img, "req": requirement})

# --- GRID SETTINGS ---
    COLS = 4
    SPACING = 150
    START_X, START_Y = 100, 150
    back_btn = pygame.Rect(350, 20, 120, 40)

    def draw_skins_tab():
        global equipped_skin, state
    
        screen.fill((30, 30, 30))
        mouse_pos = pygame.mouse.get_pos()

    # 2. TOP UI: WINS & BACK BUTTON
        wins_text = big_font.render(f"WINS: {wins}", True, (255, 215, 0))
        screen.blit(wins_text, (20, 20))

        pygame.draw.rect(screen, (150, 50, 50), back_btn)
        screen.blit(font.render("BACK", True, (255, 255, 255)), (back_btn.x + 30, back_btn.y + 10))

    # 3. RENDER SKIN GRID
        for i, skin in enumerate(skin_list):
            row = i // COLS
            col = i % COLS
            x = START_X + (col * SPACING)
            y = START_Y + (row * (SPACING + 20))
        
        # Draw Skin Image
            screen.blit(skin["img"], (x, y))
        
        # Logic for Label (Locked / Buy / Equip)
            btn_rect = pygame.Rect(x, y + 90, 80, 30)
            label = ""
            btn_col = (100, 100, 100)

            if wins < skin["req"]:
                label = f"Lock: {skin['req']}"
                btn_col = (50, 50, 50)
            elif skin["name"] == equipped_skin:
                label = "EQUIPPED"
                btn_col = (50, 200, 50)
            elif skin["name"] in owned_skins:
                label = "EQUIP"
                btn_col = (100, 100, 255)
            else:
                label = "BUY"
                btn_col = (200, 150, 50)

        # Draw Button
            pygame.draw.rect(screen, btn_col, btn_rect)
            btn_text = font.render(label, True, (255, 255, 255))
            screen.blit(btn_text, (btn_rect.x + 5, btn_rect.y + 5))

        # 4. HANDLE CLICKING
            if pygame.mouse.get_pressed()[0] and btn_rect.collidepoint(mouse_pos):
                if label == "BUY":
                    owned_skins.append(skin["name"])
                elif label == "EQUIP":
                    equipped_skin = skin["name"]

# --- SIMPLE LOOP ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    mainmenu()

        draw_skins_tab()
        pygame.display.flip()



# Configuration
CELL_SIZE = 19      # pixels per cell
MAZE_COLS = 26      # number of columns
MAZE_ROWS = 25      # number of rows
WALL_COLOR = (40, 40, 40)
BG_COLOR = (220, 220, 220)
PLAYER_COLOR = (0, 150, 30)
GOAL_COLOR = (30, 160, 30)
FPS = 60
#wins

try:
    with open(save_path, "r") as f:
        wins = int(f.read()) # Convert back to integer
except FileNotFoundError:
    wins = 0

#main menu

  
# Directions: (dx, dy), wall indices ordering: top, right, bottom, left
DIRS = {
    'N': (0, -1, 0),
    'S': (0, 1, 2),
    'W': (-1, 0, 3),
    'E': (1, 0, 1),
}
OPPOSITE = {0:2, 1:3, 2:0, 3:1}  # opposite wall index mapping


class Cell:
    def __init__(self, col, row):
        self.col = col
        self.row = row
        # walls: top, right, bottom, left (True = wall exists)
        self.walls = [True, True, True, True]
        self.visited = False

    def coords(self):
        return (self.col, self.row)


def index(col, row, cols, rows):
    if 0 <= col < cols and 0 <= row < rows:
        return row * cols + col
    return None


def generate_maze(cols, rows):
    # Create grid of cells
    grid = [Cell(c, r) for r in range(rows) for c in range(cols)]

    # Recursive backtracker iterative
    start = grid[0]
    start.visited = True
    stack = [start]

    while stack:
        current = stack[-1]
        c, r = current.col, current.row
        neighbors = []

        # check neighbors that are unvisited
        for dir_key, (dx, dy, wall_idx) in DIRS.items():
            nc, nr = c + dx, r + dy
            idx = index(nc, nr, cols, rows)
            if idx is not None:
                neighbor = grid[idx]
                if not neighbor.visited:
                    neighbors.append((neighbor, wall_idx))

        if neighbors:
            neighbor, wall_idx = random.choice(neighbors)
            # knock down wall between current and neighbor
            current.walls[wall_idx] = False
            neighbor.walls[OPPOSITE[wall_idx]] = False
            neighbor.visited = True
            stack.append(neighbor)
        else:
            stack.pop()

    # After generation clear visited flags for potential use later
    for cell in grid:
        cell.visited = False
    return grid


def draw_maze(surface, grid, cols, rows, cell_size):
    for cell in grid:
        x = cell.col * cell_size
        y = cell.row * cell_size

        # draw background for cell (optional)
        pygame.draw.rect(surface, BG_COLOR, (x, y, cell_size, cell_size))

        # walls: top, right, bottom, left
        if cell.walls[0]:
            pygame.draw.line(surface, WALL_COLOR, (x, y), (x + cell_size, y), 2)
        if cell.walls[1]:
            pygame.draw.line(surface, WALL_COLOR, (x + cell_size, y), (x + cell_size, y + cell_size), 2)
        if cell.walls[2]:
            pygame.draw.line(surface, WALL_COLOR, (x + cell_size, y + cell_size), (x, y + cell_size), 2)
        if cell.walls[3]:
            pygame.draw.line(surface, WALL_COLOR, (x, y + cell_size), (x, y), 2)


def main():
    pygame.init()
    canwin = True
    cols, rows = MAZE_COLS, MAZE_ROWS
    width = cols * CELL_SIZE
    height = rows * CELL_SIZE

    pygame.display.set_caption("Maze Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    small_font = pygame.font.Font(None, 23) 


    def new_game():
        grid = generate_maze(cols, rows)
        player = [0, 0]  # col, row
        goal = [cols - 1, rows - 1]
        start_time = time.time()
        won = False
        steps = 0
        return grid, player, goal, start_time, won, steps

    grid, player, goal, start_time, won, steps = new_game()

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid, player, goal, start_time, won, steps = new_game()

                if not won:
                    moved = False
                    col, row = player
                    cur = grid[index(col, row, cols, rows)]

                    if event.key in (pygame.K_UP, pygame.K_w):
                        # move north if no top wall
                        if not cur.walls[0] and row > 0:
                            player[1] -= 1
                            moved = True
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if not cur.walls[2] and row < rows - 1:
                            player[1] += 1
                            moved = True
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if not cur.walls[3] and col > 0:
                            player[0] -= 1
                            moved = True
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if not cur.walls[1] and col < cols - 1:
                            player[0] += 1
                            moved = True

                    if moved:
                        steps += 1
                        if player == goal:
                            won = True
                            win_time = time.time() - start_time

        # draw
        screen.fill((125, 115, 105))
        draw_maze(screen, grid, cols, rows, CELL_SIZE)

        # draw goal
        gx = goal[0] * CELL_SIZE
        gy = goal[1] * CELL_SIZE
        pygame.draw.rect(screen, GOAL_COLOR, (gx + 4, gy + 4, CELL_SIZE - 8, CELL_SIZE - 8))

        # draw player
        px = player[0] * CELL_SIZE + CELL_SIZE // 2
        py = player[1] * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, PLAYER_COLOR, (px, py), CELL_SIZE // 3)

        # HUD
        pygame.font.SysFont("fixed", size=8)
        elapsed = time.time() - start_time
        hud_surf = font.render(f"Steps: {steps}  Time: {int(elapsed)}s  (R = regenerate)", True, (10, 10, 10))
        screen.blit(hud_surf, (8, 480))

        if won:
            msg = f"You won in {steps} steps, {int(win_time)}s! Press R to play again or C to go back"
            if canwin == True:
                global wins
                wins = wins + 1
                canwin = False
            win_surf = small_font.render(msg, True, (0, 0, 0))
            # center overlay
            rect = win_surf.get_rect(center=(width // 2, height // 2))
            overlay = pygame.Surface((rect.width + 20, rect.height + 20))
            overlay.fill((240, 240, 180))
            screen.blit(overlay, (rect.x - 10, rect.y - 10))
            screen.blit(win_surf, rect)
            with open(save_path, "w") as f:
                f.write(str(wins))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        time.sleep(1)
                        running = False
                        mainmenu()






        pygame.display.flip()

    pygame.quit()
    sys.exit()
pygame.init()
def mainmenu():
    font = pygame.font.Font(None, 36)
    color = (100, 100, 100)
    colorhov = (167, 167, 167)
    pygame.init()
    screen.fill((30, 30, 30))

# Button definitions
    button1 = pygame.Rect(125, 100, 250, 100) # Centred it a bit better
    button2 = pygame.Rect(125, 225, 250, 100)
    button3 = pygame.Rect(125, 350, 250, 100)

    font = pygame.font.Font(None, 36)

# Colours
    color = (100, 100, 100)
    colorhov = (167, 167, 167)
    bg_color = (30, 30, 30)

    runnin = True
    while runnin:
    # 1. Logic & Mouse Pos
        mouse = pygame.mouse.get_pos()
        hover1 = button1.collidepoint(mouse)
        hover2 = button2.collidepoint(mouse)
        hover3 = button3.collidepoint(mouse)

    # 2. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runnin = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if hover1:
                        main()
                    if hover2:
                        skinmenu()
                    if hover3:
                        pygame.quit()

    # 3. Drawing (ORDER MATTERS)
    # FIRST: Clear the screen
        screen.fill(bg_color)

    # SECOND: Draw Button 1
        curcol1 = colorhov if hover1 else color
        pygame.draw.rect(screen, curcol1, button1)
        text1 = font.render("Play", True, (255, 255, 255))
        screen.blit(text1, text1.get_rect(center=button1.center))

    # THIRD: Draw Button 2
        curcol2 = colorhov if hover2 else color
        pygame.draw.rect(screen, curcol2, button2)
        text2 = font.render("Skins", True, (255, 255, 255))
        screen.blit(text2, text2.get_rect(center=button2.center))

        curcol3 = colorhov if hover3 else color
        pygame.draw.rect(screen, curcol3, button3)
        text3 = font.render("Quit", True, (255, 255, 255))
        screen.blit(text3, text3.get_rect(center=button3.center))


    # FOURTH: Refresh the screen
        pygame.display.flip()

mainmenu()
