import random

# Constants
WIDTH, HEIGHT = 10, 20
BLOCK_SIZE = 30  # This will be a logical block size, actual rendering size will be dynamic
# Colors are placeholders; actual rendering will use Kivy's color system
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
FPS = 30
MOVE_DELAY = 500  # Milliseconds between automatic downward movement

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

class GameState:
    """
    Manages the entire state and logic of the Tetris game.
    This class is UI-agnostic and can be integrated with any rendering engine.
    """
    def __init__(self):
        self.board = [[0] * WIDTH for _ in range(HEIGHT)]
        self.level = 1
        self.score = 0
        self.lines_cleared_count = 0
        self.current_move_delay = MOVE_DELAY
        self.falling_tetromino_queue = []
        self.falling_tetromino_shape = None
        self.falling_tetromino_rotation = 0
        self.falling_tetromino = None
        self.tetromino_pos = [0, 0]
        self.has_changed = False # For 'Z' key functionality (switch piece)
        self.game_over = False
        self.paused = False
        self.last_move_time = 0 # To track automatic downward movement
        self.stashed_tetromino_shape = None # New attribute for stashed piece

        self.all_tetromino_types = list(tetrominoes.keys())
        self.generate_tetromino_queue()
        self.spawn_new_tetromino()

    def generate_tetromino_queue(self):
        """Generates a queue of random tetromino types with repetition."""
        # Generate a queue of 14 random tetrominoes, allowing repetition
        self.falling_tetromino_queue = [random.choice(self.all_tetromino_types) for _ in range(14)]

    def reset_game(self):
        """Resets the game state to its initial values."""
        self.board = [[0] * WIDTH for _ in range(HEIGHT)]
        self.level = 1
        self.score = 0
        self.lines_cleared_count = 0
        self.current_move_delay = MOVE_DELAY
        self.generate_tetromino_queue()
        self.spawn_new_tetromino()
        self.game_over = False
        self.paused = False
        self.last_move_time = 0
        self.stashed_tetromino_shape = None # Reset stashed piece

    def spawn_new_tetromino(self):
        """Spawns a new tetromino and replenishes the queue if needed."""
        self.falling_tetromino_queue.pop(0) # Always pop the current piece from the queue
        
        # Replenish the queue if it's getting low
        if len(self.falling_tetromino_queue) <= 7: # If 7 or fewer items left, generate more
            new_tetrominoes = [random.choice(self.all_tetromino_types) for _ in range(7)] # Add 7 new random tetrominoes
            self.falling_tetromino_queue.extend(new_tetrominoes)

        self.falling_tetromino_shape = self.falling_tetromino_queue[0]
        self.falling_tetromino_rotation = 0
        self.falling_tetromino = tetrominoes[self.falling_tetromino_shape][self.falling_tetromino_rotation]

        # Initial position for the new tetromino
        if self.falling_tetromino_shape == 'I':
            self.tetromino_pos = [WIDTH // 2 - len(self.falling_tetromino[0]) // 2 - 1, 0]
        else:
            self.tetromino_pos = [WIDTH // 2 - len(self.falling_tetromino[0]) // 2, 0]
        
        self.has_changed = False # Reset change tracker for the new block

        # Check for game over immediately after spawning
        if self.check_collision(self.falling_tetromino, self.tetromino_pos):
            self.game_over = True

    def check_collision(self, tetromino, pos):
        """Checks if the given tetromino at the given position collides with anything."""
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
                    # Only check if board_y is within bounds to prevent index out of range
                    if board_y >= 0 and self.board[board_y][board_x] == 1:
                        return True
        return False

    def move_tetromino(self, dx, dy):
        """Attempts to move the falling tetromino by (dx, dy). Returns True if moved, False otherwise."""
        new_pos = [self.tetromino_pos[0] + dx, self.tetromino_pos[1] + dy]
        if not self.check_collision(self.falling_tetromino, new_pos):
            self.tetromino_pos = new_pos
            return True
        return False

    def get_rotated_tetromino_data(self, shape, rotation_index):
        """Returns the tetromino data for the next rotation state."""
        rotations = tetrominoes[shape]
        next_rotation_index = (rotation_index + 1) % len(rotations)
        return rotations[next_rotation_index], next_rotation_index

    def try_rotate(self):
        """Attempts to rotate the falling tetromino using SRS kick data."""
        if self.game_over or self.paused:
            return

        next_tetromino_data, next_rotation_index = self.get_rotated_tetromino_data(
            self.falling_tetromino_shape, self.falling_tetromino_rotation
        )

        # Determine the kick data to use
        if self.falling_tetromino_shape == 'I':
            kick_data = SRS_KICK_DATA_I
        else:
            kick_data = SRS_KICK_DATA_OTHER

        # Get the specific kick offsets for this rotation transition
        kick_offsets = kick_data.get((self.falling_tetromino_rotation, next_rotation_index), [(0,0)])

        for dx, dy in kick_offsets:
            new_pos = [self.tetromino_pos[0] + dx, self.tetromino_pos[1] + dy]
            if not self.check_collision(next_tetromino_data, new_pos):
                self.falling_tetromino = next_tetromino_data
                self.falling_tetromino_rotation = next_rotation_index
                self.tetromino_pos = new_pos
                return True
        return False

    def drop_tetromino(self):
        """Hard drops the falling tetromino to the lowest possible position."""
        if self.game_over or self.paused:
            return

        initial_y = self.tetromino_pos[1]
        while self.move_tetromino(0, 1):
            pass # Keep moving down until collision
        rows_dropped = self.tetromino_pos[1] - initial_y
        self.score += rows_dropped * 2 # Add score for hard drop (2 points per row)
        self._lock_tetromino()

    def get_ghost_pos(self):
        """Calculates the position of the ghost tetromino."""
        ghost_pos = list(self.tetromino_pos)
        while not self.check_collision(self.falling_tetromino, [ghost_pos[0], ghost_pos[1] + 1]):
            ghost_pos[1] += 1
        return ghost_pos

    def _lock_tetromino(self):
        """Locks the falling tetromino onto the board and checks for line clears."""
        for y, row in enumerate(self.falling_tetromino):
            for x, value in enumerate(row):
                if value == 1:
                    # Ensure we don't write outside the board if a piece spawns on top
                    if self.tetromino_pos[1] + y >= 0:
                        self.board[self.tetromino_pos[1] + y][self.tetromino_pos[0] + x] = 1
        self.clear_lines()
        self.spawn_new_tetromino()

    def clear_lines(self):
        """Checks for and clears full lines, updating score and level."""
        cleared_lines = 0
        new_board = []
        for y in range(HEIGHT):
            if not all(self.board[y]): # If line is not full, keep it
                new_board.append(self.board[y])
            else: # If line is full, clear it
                cleared_lines += 1
        
        # Add empty lines to the top
        for _ in range(cleared_lines):
            new_board.insert(0, [0] * WIDTH)
        self.board = new_board

        if cleared_lines > 0:
            if cleared_lines == 1:
                self.score += 40 * self.level
            elif cleared_lines == 2:
                self.score += 100 * self.level
            elif cleared_lines == 3:
                self.score += 300 * self.level
            elif cleared_lines == 4:
                self.score += 1200 * self.level
            self.lines_cleared_count += cleared_lines
            self.level = 1 + self.lines_cleared_count // 10
            self.current_move_delay = max(100, MOVE_DELAY - (self.level - 1) * 50)

    def update(self, dt):
        """
        Main game logic update function, called periodically by the UI.
        Handles automatic downward movement.
        """
        if self.game_over or self.paused:
            return

        # Simulate time passing for automatic downward movement
        self.last_move_time += dt * 1000 # Convert dt (seconds) to milliseconds

        if self.last_move_time > self.current_move_delay:
            self.last_move_time = 0
            if not self.move_tetromino(0, 1): # Attempt to move down
                # If cannot move down, lock the tetromino
                self._lock_tetromino()

    def get_next_tetromino_data(self):
        """Returns the data for the next tetromino in the queue."""
        if len(self.falling_tetromino_queue) > 1: # Check if there's a next tetromino
            next_tetromino_shape = self.falling_tetromino_queue[1]
            return tetrominoes[next_tetromino_shape][0]
        return None # Or handle this case as appropriate, e.g., return a default empty shape

    def get_stashed_tetromino_data(self):
        """Returns the data for the stashed tetromino."""
        if self.stashed_tetromino_shape:
            return tetrominoes[self.stashed_tetromino_shape][0]
        return None

    def switch_tetromino(self):
        """Switches the current falling tetromino with the stashed one."""
        if self.game_over or self.paused or self.has_changed:
            return

        current_falling_shape = self.falling_tetromino_shape
        
        if self.stashed_tetromino_shape is None:
            # Stash current piece, spawn new from queue
            self.stashed_tetromino_shape = current_falling_shape
            self.falling_tetromino_queue.pop(0) # Remove the piece that was just stashed from the queue
            self.falling_tetromino_shape = self.falling_tetromino_queue[0]
        else:
            # Swap current with stashed
            self.falling_tetromino_shape = self.stashed_tetromino_shape
            self.stashed_tetromino_shape = current_falling_shape
        
        self.falling_tetromino_rotation = 0
        self.falling_tetromino = tetrominoes[self.falling_tetromino_shape][self.falling_tetromino_rotation]

        # Recalculate tetromino_pos after swap
        if self.falling_tetromino_shape == 'I':
            self.tetromino_pos = [WIDTH // 2 - len(self.falling_tetromino[0]) // 2 - 1, 0]
        else:
            self.tetromino_pos = [WIDTH // 2 - len(self.falling_tetromino[0]) // 2, 0]

        # Check for immediate collision after swap, if so, revert
        if self.check_collision(self.falling_tetromino, self.tetromino_pos):
            # Revert the swap if it causes a collision
            # This part needs careful consideration for reverting the stash state
            # For simplicity, if collision, we just don't allow the swap
            # A more robust solution might involve trying to move the piece up
            # or finding a valid position, but for now, we'll disallow.
            self.falling_tetromino_shape = current_falling_shape # Revert to original
            self.falling_tetromino = tetrominoes[current_falling_shape][0] # Revert to original rotation
            # Revert stashed piece
            if self.stashed_tetromino_shape == current_falling_shape: # If it was just stashed
                self.stashed_tetromino_shape = None
                self.falling_tetromino_queue.insert(0, current_falling_shape) # Put it back in queue
            else: # If it was swapped from stash
                temp_stashed = self.stashed_tetromino_shape
                self.stashed_tetromino_shape = current_falling_shape
                self.falling_tetromino_shape = temp_stashed
            
            # Revert position
            if current_falling_shape == 'I':
                self.tetromino_pos = [WIDTH // 2 - len(tetrominoes[current_falling_shape][0][0]) // 2 - 1, 0]
            else:
                self.tetromino_pos = [WIDTH // 2 - len(tetrominoes[current_falling_shape][0][0]) // 2, 0]
            return False # Swap failed due to collision
        
        self.has_changed = True
        return True
