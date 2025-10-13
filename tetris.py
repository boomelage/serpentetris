import pygame
import sys
import random

# Constants
WIDTH, HEIGHT = 10, 20
BLOCK_SIZE = 30
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 30
MOVE_DELAY = 500  # Milliseconds between automatic downward movement

# Initialize Pygame
pygame.init()
pygame.font.init()  # Initialize the font module
# Add extra space for the preview area to the right of the game board
extra_preview_width = 8 * BLOCK_SIZE  # Adjust as needed for the size of the preview area
screen = pygame.display.set_mode((WIDTH * BLOCK_SIZE + extra_preview_width, HEIGHT * BLOCK_SIZE))

clock = pygame.time.Clock()

# Game board
board = [[0] * WIDTH for _ in range(HEIGHT)]

# Tetrominoes with all rotation states
tetrominoes = {
    'I': [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]]
    ],
    'L': [
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]],
        [[0, 1], [0, 1], [1, 1]]
    ],
    'J': [
        [[0, 0, 1], [1, 1, 1]],
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]]
    ],
    'S': [
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]]
    ],
    'Z': [
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1], [1, 1], [1, 0]]
    ],
    'O': [
        [[1, 1], [1, 1]]
    ]
}

# SRS Kick Data for 'I' tetromino
# [current_rotation][next_rotation] -> list of (dx, dy) offsets
SRS_KICK_DATA_I = {
    (0, 1): [(0,0), (-2,0), (1,0), (-2,1), (1,-2)], # 0 -> R
    (1, 0): [(0,0), (2,0), (-1,0), (2,-1), (-1,2)], # R -> 0
    (1, 2): [(0,0), (-1,0), (2,0), (-1,-2), (2,1)], # R -> 2
    (2, 1): [(0,0), (1,0), (-2,0), (1,2), (-2,-1)], # 2 -> R
    (2, 3): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)], # 2 -> L
    (3, 2): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)], # L -> 2
    (3, 0): [(0,0), (1,0), (-2,0), (1,2), (-2,-1)], # L -> 0
    (0, 3): [(0,0), (-1,0), (2,0), (-1,-2), (2,1)], # 0 -> L
}

# SRS Kick Data for other tetrominoes (J, L, S, T, Z)
# [current_rotation][next_rotation] -> list of (dx, dy) offsets
SRS_KICK_DATA_OTHER = {
    (0, 1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], # 0 -> R
    (1, 0): [(0,0), (1,0), (1,-1), (0,2), (1,2)], # R -> 0
    (1, 2): [(0,0), (1,0), (1,-1), (0,2), (1,2)], # R -> 2
    (2, 1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)], # 2 -> R
    (2, 3): [(0,0), (1,0), (1,1), (0,-2), (1,-2)], # 2 -> L
    (3, 2): [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], # L -> 2
    (3, 0): [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)], # L -> 0
    (0, 3): [(0,0), (1,0), (1,1), (0,-2), (1,-2)], # 0 -> L
}

def generate_tetromino_queue():
    all_tetromino_types = list(tetrominoes.keys())
    queue = [random.choice(all_tetromino_types) for _ in range(14)]
    return queue

# Functions
def draw_board():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            pygame.draw.rect(screen, (50, 50, 50), (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
            if board[y][x] == 1:
                pygame.draw.rect(screen, GREEN, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def draw_tetromino(tetromino, pos):
    for y, row in enumerate(tetromino):
        for x, value in enumerate(row):
            if value == 1:
                pygame.draw.rect(screen, GREEN, ((pos[0] + x) * BLOCK_SIZE, (pos[1] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def move_tetromino(tetromino, pos, dx, dy):
    new_pos = [pos[0] + dx, pos[1] + dy]
    if not check_collision(tetromino, new_pos):
        return new_pos
    return pos

def check_collision(tetromino, pos):
    for y_offset, row in enumerate(tetromino):
        for x_offset, value in enumerate(row):
            if value == 1:
                board_x = pos[0] + x_offset
                board_y = pos[1] + y_offset

                # Check if outside horizontal boundaries
                if board_x < 0 or board_x >= WIDTH:
                    return True
                # Check if outside vertical boundaries (bottom or top)
                if board_y < 0 or board_y >= HEIGHT:
                    return True
                # Check if collides with existing blocks on the board
                if board[board_y][board_x] == 1:
                    return True
    return False

def get_rotated_tetromino_data(shape, rotation_index):
    rotations = tetrominoes[shape]
    next_rotation_index = (rotation_index + 1) % len(rotations)
    return rotations[next_rotation_index], next_rotation_index

def try_rotate(current_tetromino, current_pos, shape_name, current_rotation_index):
    next_tetromino_data, next_rotation_index = get_rotated_tetromino_data(shape_name, current_rotation_index)

    # Determine the kick data to use
    if shape_name == 'I':
        kick_data = SRS_KICK_DATA_I
    else:
        kick_data = SRS_KICK_DATA_OTHER

    # Get the specific kick offsets for this rotation transition
    # The key for kick_data is (current_rotation_index, next_rotation_index)
    kick_offsets = kick_data.get((current_rotation_index, next_rotation_index), [(0,0)])

    for dx, dy in kick_offsets:
        new_pos = [current_pos[0] + dx, current_pos[1] + dy]
        if not check_collision(next_tetromino_data, new_pos):
            return next_tetromino_data, next_rotation_index, new_pos

    # If no kick works, rotation is not possible, return original state
    return current_tetromino, current_rotation_index, current_pos

def drop_tetromino(tetromino, pos):
    # Start from the current position and move down until a collision is detected
    while not check_collision(tetromino, [pos[0], pos[1] + 1]):
        pos[1] += 1  # Move down by one row
    return pos

def get_ghost_pos(tetromino, pos):
    ghost_pos = list(pos)
    while not check_collision(tetromino, [ghost_pos[0], ghost_pos[1] + 1]):
        ghost_pos[1] += 1
    return ghost_pos

def draw_ghost_tetromino(tetromino, pos):
    for y, row in enumerate(tetromino):
        for x, value in enumerate(row):
            if value == 1:
                pygame.draw.rect(screen, (128, 128, 128), ((pos[0] + x) * BLOCK_SIZE, (pos[1] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 2)

def draw_score(surface, score):
    font = pygame.font.SysFont("Courier New", 24)
    text_surface = font.render(f"Score: {score}", True, GREEN)
    surface.blit(text_surface, (WIDTH * BLOCK_SIZE + 10, 10))

def draw_level(surface, level):
    font = pygame.font.SysFont("Courier New", 24)
    text_surface = font.render(f"Level: {level}", True, GREEN)
    surface.blit(text_surface, (WIDTH * BLOCK_SIZE + 10, 40))

def draw_tetromino_preview(current_tetromino, next_tetromino, screen, block_size, offset):
    # Draw the current tetromino preview
    preview_offset_x = offset[0]
    preview_offset_y = offset[1]
    
    for y, row in enumerate(current_tetromino):
        for x, value in enumerate(row):
            if value == 1:
                pygame.draw.rect(screen, GREEN, (preview_offset_x + x * block_size, preview_offset_y + y * block_size, block_size, block_size))
    
    # Adjust the Y offset for the next tetromino to draw it below the current one with some spacing
    preview_offset_y += 5 * block_size  # Adjust this value based on your preference for spacing

    for y, row in enumerate(next_tetromino):
        for x, value in enumerate(row):
            if value == 1:
                pygame.draw.rect(screen, GREEN, (preview_offset_x + x * block_size, preview_offset_y + y * block_size, block_size, block_size))

def main_menu(screen):
    font = pygame.font.SysFont("Courier New", 48)
    small_font = pygame.font.SysFont("Courier New", 24)
    tiny_font = pygame.font.SysFont("Courier New", 18)
    selected_level = 1

    while True:
        screen.fill(BLACK)
        title_surface = font.render("Serpentetris", True, GREEN)
        title_rect = title_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 100))
        screen.blit(title_surface, title_rect)

        tiny_font = pygame.font.SysFont("Courier New", 20)
        byline_surface = tiny_font.render("by boomelage", True, GREEN)
        byline_rect = byline_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 70))
        screen.blit(byline_surface, byline_rect)

        level_surface = small_font.render(f"Starting Level: {selected_level}", True, GREEN)
        level_rect = level_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
        screen.blit(level_surface, level_rect)

        level_change_surface = tiny_font.render("\u2191/\u2193", True, GREEN)
        level_change_rect = level_change_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 25))
        screen.blit(level_change_surface, level_change_rect)

        start_surface = small_font.render("Press Enter to Start", True, GREEN)
        start_rect = start_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 80))
        screen.blit(start_surface, start_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = min(10, selected_level + 1)
                elif event.key == pygame.K_DOWN:
                    selected_level = max(1, selected_level - 1)
                elif event.key == pygame.K_RETURN:
                    return selected_level

def draw_controls(surface):
    font = pygame.font.SysFont("Courier New", 18)
    controls = [
        "←/→/↓: Move",
        "↑: Rotate",
        "Space: Drop",
        "Z: Switch",
        "P: Pause",
    ]
    for i, control in enumerate(controls):
        text_surface = font.render(control, True, GREEN)
        surface.blit(text_surface, (WIDTH * BLOCK_SIZE + 10, HEIGHT * BLOCK_SIZE - (len(controls) - i) * 20))

def show_game_over_screen(screen):
    screen.fill(BLACK)  # Clear the screen
    font = pygame.font.SysFont("Courier New", 48)
    small_font = pygame.font.SysFont("Courier New", 24)
    text_surface = font.render("Game Over", True, GREEN)
    text_rect = text_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 50))
    screen.blit(text_surface, text_rect)

    restart_surface = small_font.render("Press R to restart", True, GREEN)
    restart_rect = restart_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 50))
    screen.blit(restart_surface, restart_rect)

    menu_surface = small_font.render("Press M to return to menu", True, GREEN)
    menu_rect = menu_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 80))
    screen.blit(menu_surface, menu_rect)

    pygame.display.flip()
    # Wait for the user to acknowledge the game over
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    global restart_game
                    restart_game = True
                    return
                elif event.key == pygame.K_m:
                    global return_to_menu
                    return_to_menu = True
                    return


# Define the preview offset from the top right corner of the game window
preview_offset = (WIDTH * BLOCK_SIZE + 10, 10)

def reset_game():
    global board, level, score, lines_cleared_count, current_move_delay, falling_tetromino_queue, falling_tetromino_shape, falling_tetromino_rotation, falling_tetromino, tetromino_pos, has_changed, game_over
    board = [[0] * WIDTH for _ in range(HEIGHT)]
    level = 1
    score = 0
    lines_cleared_count = 0
    current_move_delay = MOVE_DELAY
    falling_tetromino_queue = generate_tetromino_queue()
    spawn_new_tetromino()
    game_over = False

def spawn_new_tetromino():
    global falling_tetromino_queue, falling_tetromino_shape, falling_tetromino_rotation, falling_tetromino, tetromino_pos, has_changed

    falling_tetromino_queue.pop(0)
    # Replenish the queue if it's getting low
    if len(falling_tetromino_queue) <= 7: # If 7 or fewer items left, generate more
        all_tetromino_types = list(tetrominoes.keys())
        new_tetrominoes = [random.choice(all_tetromino_types) for _ in range(7)] # Add 7 new random tetrominoes
        falling_tetromino_queue.extend(new_tetrominoes)

    falling_tetromino_shape = falling_tetromino_queue[0]
    falling_tetromino_rotation = 0
    falling_tetromino = tetrominoes[falling_tetromino_shape][falling_tetromino_rotation]

    if falling_tetromino_shape == 'I':
        tetromino_pos = [WIDTH // 2 - len(falling_tetromino[0]) // 2 - 1, 0]
    else:
        tetromino_pos = [WIDTH // 2 - len(falling_tetromino[0]) // 2, 0]
    
    has_changed = False # Reset change tracker for the new block

def main():
    global board, level, score, lines_cleared_count, current_move_delay, falling_tetromino_queue, falling_tetromino_shape, falling_tetromino_rotation, falling_tetromino, tetromino_pos, has_changed, game_over, return_to_menu, p_key_pressed, restart_game
    pygame.key.set_repeat(100, 50)
    return_to_menu = False
    p_key_pressed = False
    return_to_menu_from_pause = False
    restart_game = False
    reset_game()
    starting_level = main_menu(screen)
    level = starting_level
    lines_cleared_count = (level - 1) * 10
    current_move_delay = max(100, MOVE_DELAY - (level - 1) * 50)

    # Define the preview offset from the top right corner of the game window
    preview_offset = (WIDTH * BLOCK_SIZE + 10, 10)
    last_move_time = pygame.time.get_ticks()
    small_font = pygame.font.SysFont("Courier New", 24)
    paused = False
    up_key_pressed = False

    while True:
        # Handle pause toggle using key state
        keys = pygame.key.get_pressed()
        current_p_state = keys[pygame.K_p]

        if current_p_state and not last_p_state:
            paused = not paused
        
        last_p_state = current_p_state

        if return_to_menu:
            return_to_menu = False # Reset the flag
            starting_level = main_menu(screen) # Go back to main menu
            # After main_menu, the game should restart with the chosen level
            reset_game() # Reset game state
            level = starting_level
            lines_cleared_count = (level - 1) * 10
            current_move_delay = max(100, MOVE_DELAY - (level - 1) * 50)
            continue # Continue the main loop with a fresh game

        if game_over:
            show_game_over_screen(screen)
            if restart_game:
                reset_game()
                level = starting_level # Reset level to starting level
                lines_cleared_count = (level - 1) * 10
                current_move_delay = max(100, MOVE_DELAY - (level - 1) * 50)
                restart_game = False
                game_over = False # Reset game_over flag
                continue
            if return_to_menu:
                return_to_menu = False # Reset the flag
                starting_level = main_menu(screen) # Go back to main menu
                reset_game() # Reset game state
                level = starting_level
                lines_cleared_count = (level - 1) * 10
                current_move_delay = max(100, MOVE_DELAY - (level - 1) * 50)
                continue # Continue the main loop with a fresh game
            else: # If not restarting and not returning to menu, then user quit
                break # Exit the game loop

        if paused:
            screen.fill(BLACK)
            font = pygame.font.SysFont("Courier New", 48)
            text_surface = font.render("Paused", True, GREEN)
            text_rect = text_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
            screen.blit(text_surface, text_rect)
            restart_game_surface = small_font.render("Press R to Restart", True, GREEN)
            restart_game_rect = restart_game_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 50))
            screen.blit(restart_game_surface, restart_game_rect)

            restart_surface = small_font.render("Press M to return to menu", True, GREEN)
            restart_rect = restart_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 80))
            screen.blit(restart_surface, restart_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        return_to_menu = True
                        paused = False # Unpause the game to allow main loop to process return_to_menu
                    elif event.key == pygame.K_r:
                        reset_game()
                        paused = False
                        game_over = False # Ensure game_over is reset for a fresh start
                elif event.type == pygame.KEYUP:
                    pass # No longer need to handle p_key_pressed here
            continue # Skip game logic and drawing when paused

        # Game logic and drawing only if not paused
        if not paused:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > current_move_delay:
                last_move_time = current_time
                new_pos = move_tetromino(falling_tetromino, tetromino_pos, 0, 1)
                if new_pos == tetromino_pos:  # Tetromino reached bottom or collided
                    if check_collision(falling_tetromino, tetromino_pos):
                        game_over = True
                        continue
                    for y, row in enumerate(falling_tetromino):
                        for x, value in enumerate(row):
                            if value == 1:
                                board[tetromino_pos[1] + y][tetromino_pos[0] + x] = 1
                    cleared_lines = 0
                    for y in range(HEIGHT):
                        if all(board[y]):
                            del board[y]
                            board.insert(0, [0] * WIDTH)
                            cleared_lines += 1
                    
                    if cleared_lines > 0:
                        if cleared_lines == 1:
                            score += 40 * level
                        elif cleared_lines == 2:
                            score += 100 * level
                        elif cleared_lines == 3:
                            score += 300 * level
                        elif cleared_lines == 4:
                            score += 1200 * level
                        lines_cleared_count += cleared_lines
                        level = 1 + lines_cleared_count // 10
                        current_move_delay = max(100, MOVE_DELAY - (level - 1) * 50)
                    spawn_new_tetromino()

                    # Check for game over condition before placing the tetromino
                    if check_collision(falling_tetromino, tetromino_pos):
                        game_over = True  # Set the game over flag
                        continue # Skip placing the tetromino if game is over

                else:
                    tetromino_pos = new_pos

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        tetromino_pos = move_tetromino(falling_tetromino, tetromino_pos, -1, 0)
                    elif event.key == pygame.K_RIGHT:
                        tetromino_pos = move_tetromino(falling_tetromino, tetromino_pos, 1, 0)
                    elif event.key == pygame.K_DOWN:
                        tetromino_pos = move_tetromino(falling_tetromino, tetromino_pos, 0, 1)
                    elif event.key == pygame.K_UP:
                        if not up_key_pressed:
                            falling_tetromino, falling_tetromino_rotation, tetromino_pos = try_rotate(falling_tetromino, tetromino_pos, falling_tetromino_shape, falling_tetromino_rotation)
                            up_key_pressed = True

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        up_key_pressed = False
                    elif event.key == pygame.K_p:
                        p_key_pressed = False
                    elif event.key == pygame.K_z:
                        if not has_changed:  # Change block if not already changed
                            if len(falling_tetromino_queue) > 1:
                                current_shape = falling_tetromino_shape
                                next_shape = falling_tetromino_queue[1]
                                falling_tetromino_queue[0] = next_shape
                                falling_tetromino_queue[1] = current_shape
                                falling_tetromino_shape = next_shape
                                falling_tetromino_rotation = 0
                                falling_tetromino = tetrominoes[falling_tetromino_shape][falling_tetromino_rotation]

                                # Recalculate tetromino_pos after swap
                                if falling_tetromino_shape == 'I':
                                    tetromino_pos = [WIDTH // 2 - len(falling_tetromino[0]) // 2 - 1, 0]
                                else:
                                    tetromino_pos = [WIDTH // 2 - len(falling_tetromino[0]) // 2, 0]

                                has_changed = True
                    elif event.key == pygame.K_SPACE:
                        initial_y = tetromino_pos[1] # Store initial y position
                        tetromino_pos = drop_tetromino(falling_tetromino, tetromino_pos)
                        rows_dropped = tetromino_pos[1] - initial_y # Calculate rows dropped
                        score += rows_dropped * 2 # Add score for hard drop (2 points per row)
                        for y, row in enumerate(falling_tetromino):
                            for x, value in enumerate(row):
                                if value == 1:
                                    board[tetromino_pos[1] + y][tetromino_pos[0] + x] = 1
                        cleared_lines = 0
                        for y in range(HEIGHT):
                            if all(board[y]):
                                del board[y]
                                board.insert(0, [0] * WIDTH)
                                cleared_lines += 1
                        
                        if cleared_lines > 0:
                            if cleared_lines == 1:
                                score += 40 * level
                            elif cleared_lines == 2:
                                score += 100 * level
                            elif cleared_lines == 3:
                                score += 300 * level
                            elif cleared_lines == 4:
                                score += 1200 * level
                            lines_cleared_count += cleared_lines
                            level = 1 + lines_cleared_count // 10
                            current_move_delay = max(100, MOVE_DELAY - (level - 1) * 50)

                        spawn_new_tetromino()
            if len(falling_tetromino_queue) > 1:
                next_tetromino_shape = falling_tetromino_queue[1]
                next_tetromino = tetrominoes[next_tetromino_shape][0]
            else:
                # If there is no next tetromino in the queue, generate a new queue
                new_queue = generate_tetromino_queue()
                next_tetromino_shape = new_queue[0]
                next_tetromino = tetrominoes[next_tetromino_shape][0]


            screen.fill(BLACK)
            draw_board()
            ghost_pos = get_ghost_pos(falling_tetromino, tetromino_pos)
            draw_ghost_tetromino(falling_tetromino, ghost_pos)
            draw_tetromino(falling_tetromino, tetromino_pos)
            draw_score(screen, score)
            draw_level(screen, level)
            draw_tetromino_preview(falling_tetromino, next_tetromino, screen, BLOCK_SIZE, (preview_offset[0], preview_offset[1] + 60))
            draw_controls(screen)
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()