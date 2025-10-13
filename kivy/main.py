from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
from kivy.vector import Vector
from kivy.core.window import Window

from game_core import GameState, WIDTH, HEIGHT, BLOCK_SIZE, tetrominoes, FPS # Import necessary game logic

# Import controls for touch gestures
from controls import TouchControls

class GameGrid(Widget):
    """
    Kivy Widget responsible for drawing the Tetris game grid and falling tetrominoes.
    """
    game_state = ObjectProperty(None)
    block_render_size = NumericProperty(0) # Actual size of a block on screen
    touch_controls = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_block_render_size, pos=self.update_block_render_size)
        # Bind touch events to the GameGrid itself
        self.bind(on_touch_down=self.on_touch_down_grid,
                  on_touch_move=self.on_touch_move_grid,
                  on_touch_up=self.on_touch_up_grid)

    def on_touch_down_grid(self, instance, touch):
        if self.collide_point(*touch.pos):
            return self.touch_controls.on_touch_down(touch)
        return False

    def on_touch_move_grid(self, instance, touch):
        if self.collide_point(*touch.pos):
            return self.touch_controls.on_touch_move(touch)
        return False

    def on_touch_up_grid(self, instance, touch):
        if self.collide_point(*touch.pos):
            return self.touch_controls.on_touch_up(touch)
        return False

    def update_block_render_size(self, *args):
        """Calculates the appropriate block size based on widget size."""
        if self.width > 0 and self.height > 0:
            self.block_render_size = min(self.width / WIDTH, self.height / HEIGHT)
        self.draw_game()

    def draw_game(self):
        """Draws the game board, falling tetromino, and ghost piece."""
        self.canvas.clear()
        if not self.game_state:
            return

        with self.canvas:
            # Draw background grid lines
            Color(0.1, 0.1, 0.1, 1) # Dark grey for grid lines
            for x in range(WIDTH + 1):
                Rectangle(pos=(self.x + x * self.block_render_size, self.y),
                          size=(1, self.height))
            for y in range(HEIGHT + 1):
                Rectangle(pos=(self.x, self.y + y * self.block_render_size),
                          size=(self.width, 1))

            # Draw locked blocks on the board
            for y_idx in range(HEIGHT):
                for x_idx in range(WIDTH):
                    if self.game_state.board[y_idx][x_idx] == 1:
                        Color(0, 1, 0, 1) # Green
                        Rectangle(pos=(self.x + x_idx * self.block_render_size,
                                       self.y + (HEIGHT - 1 - y_idx) * self.block_render_size),
                                  size=(self.block_render_size, self.block_render_size))

            # Draw ghost tetromino
            if self.game_state.falling_tetromino and not self.game_state.game_over and not self.game_state.paused:
                ghost_pos = self.game_state.get_ghost_pos()
                for y_offset, row in enumerate(self.game_state.falling_tetromino):
                    for x_offset, value in enumerate(row):
                        if value == 1:
                            Color(0.5, 0.5, 0.5, 0.5) # Grey, semi-transparent
                            Rectangle(pos=(self.x + (ghost_pos[0] + x_offset) * self.block_render_size,
                                           self.y + (HEIGHT - 1 - (ghost_pos[1] + y_offset)) * self.block_render_size),
                                      size=(self.block_render_size, self.block_render_size))

            # Draw falling tetromino
            if self.game_state.falling_tetromino and not self.game_state.game_over and not self.game_state.paused:
                for y_offset, row in enumerate(self.game_state.falling_tetromino):
                    for x_offset, value in enumerate(row):
                        if value == 1:
                            Color(0, 1, 0, 1) # Green
                            Rectangle(pos=(self.x + (self.game_state.tetromino_pos[0] + x_offset) * self.block_render_size,
                                           self.y + (HEIGHT - 1 - (self.game_state.tetromino_pos[1] + y_offset)) * self.block_render_size),
                                      size=(self.block_render_size, self.block_render_size))

class UpcomingPiecePreview(Widget):
    """
    Kivy Widget for displaying the next tetromino in the queue.
    """
    game_state = ObjectProperty(None)
    block_render_size = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_block_render_size, pos=self.update_block_render_size)

    def update_block_render_size(self, *args):
        """Calculates the appropriate block size for the preview."""
        if self.width > 0 and self.height > 0:
            # A smaller block size for the preview
            self.block_render_size = min(self.width / 4, self.height / 4) # Assuming max 4x4 tetromino
        self.draw_preview()

    def draw_preview(self):
        """Draws the next tetromino."""
        self.canvas.clear()
        if not self.game_state or self.game_state.game_over or self.game_state.paused:
            return

        next_tetromino = self.game_state.get_next_tetromino_data()

        if next_tetromino:
            with self.canvas:
                Color(0, 1, 0, 1) # Green
                # Center the preview piece within its widget area
                max_dim = max(len(next_tetromino), max(len(row) for row in next_tetromino))
                start_x = self.x + (self.width - max_dim * self.block_render_size) / 2
                start_y = self.y + (self.height - max_dim * self.block_render_size) / 2

                for y_offset, row in enumerate(next_tetromino):
                    for x_offset, value in enumerate(row):
                        if value == 1:
                            Rectangle(pos=(start_x + x_offset * self.block_render_size,
                                           start_y + (max_dim - 1 - y_offset) * self.block_render_size),
                                      size=(self.block_render_size, self.block_render_size))

class StashedPiecePreview(Widget):
    """
    Kivy Widget for displaying the stashed tetromino.
    """
    game_state = ObjectProperty(None)
    block_render_size = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_block_render_size, pos=self.update_block_render_size)

    def update_block_render_size(self, *args):
        """Calculates the appropriate block size for the preview."""
        if self.width > 0 and self.height > 0:
            self.block_render_size = min(self.width / 4, self.height / 4)
        self.draw_preview()

    def draw_preview(self):
        """
        Draws the stashed tetromino.
        """
        self.canvas.clear()
        if not self.game_state or self.game_state.game_over or self.game_state.paused:
            return

        stashed_tetromino = self.game_state.get_stashed_tetromino_data()

        if stashed_tetromino:
            with self.canvas:
                Color(0, 1, 0, 1) # Green
                max_dim = max(len(stashed_tetromino), max(len(row) for row in stashed_tetromino))
                start_x = self.x + (self.width - max_dim * self.block_render_size) / 2
                start_y = self.y + (self.height - max_dim * self.block_render_size) / 2

                for y_offset, row in enumerate(stashed_tetromino):
                    for x_offset, value in enumerate(row):
                        if value == 1:
                            Rectangle(pos=(start_x + x_offset * self.block_render_size,
                                           start_y + (max_dim - 1 - y_offset) * self.block_render_size),
                                      size=(self.block_render_size, self.block_render_size))


class GameScreen(BoxLayout):
    """
    The main game screen widget, combining the game grid, score/level, and controls.
    """
    game_state = ObjectProperty(GameState())
    score_label = ObjectProperty(None)
    level_label = ObjectProperty(None)
    game_grid = ObjectProperty(None)
    upcoming_piece_preview = ObjectProperty(None)
    stashed_piece_preview = ObjectProperty(None)
    pause_label = ObjectProperty(None)
    game_over_label = ObjectProperty(None)
    game_over_restart_label = ObjectProperty(None)
    game_over_menu_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # Initialize touch controls
        self.touch_controls = TouchControls(self.game_state)
        self.game_grid.touch_controls = self.touch_controls # Pass controls to GameGrid

        # Schedule the game update loop
        Clock.schedule_interval(self.update, 1.0 / FPS)

    def update(self, dt):
        """
        Main game update loop. Calls the game_state's update method
        and refreshes the UI.
        """
        if self.game_state.game_over:
            self.game_over_label.opacity = 1
            self.game_over_restart_label.opacity = 1
            self.game_over_menu_label.opacity = 1
            self.pause_label.opacity = 0 # Hide pause label if game over
            return
        else:
            self.game_over_label.opacity = 0
            self.game_over_restart_label.opacity = 0
            self.game_over_menu_label.opacity = 0

        if self.game_state.paused:
            self.pause_label.opacity = 1
            return
        else:
            self.pause_label.opacity = 0

        self.game_state.update(dt)
        self.score_label.text = f"Score: {self.game_state.score}"
        self.level_label.text = f"Level: {self.game_state.level}"
        self.game_grid.draw_game()
        self.upcoming_piece_preview.draw_preview()
        self.stashed_piece_preview.draw_preview()

    def on_pause_button(self):
        """Toggles the game pause state."""
        self.game_state.paused = not self.game_state.paused

    def on_restart_button(self):
        """Restarts the game."""
        self.game_state.reset_game()
        self.game_state.game_over = False # Ensure game_over is reset
        self.game_state.paused = False # Ensure game is unpaused

    def on_menu_button(self):
        """Returns to the main menu (for now, just restarts)."""
        # In a full app, this would switch to a different screen (e.g., a main menu screen)
        # For this port, we'll just reset the game for simplicity.
        self.game_state.reset_game()
        self.game_state.game_over = False
        self.game_state.paused = False


class TetrisApp(App):
    """
    The main Kivy application class.
    """
    def build(self):
        self.title = "PyTetris Kivy"
        return GameScreen()

if __name__ == '__main__':
    TetrisApp().run()
