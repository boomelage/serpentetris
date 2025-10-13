from kivy.vector import Vector

class TouchControls:
    """
    Handles touch input for the Tetris game.
    Translates gestures into game actions like move, rotate, and drop.
    """
    
    # Gesture detection parameters
    SWIPE_THRESHOLD = 50 # Minimum distance for a swipe
    TAP_MAX_DIST = 20 # Maximum movement for a tap
    TAP_MAX_TIME = 0.2 # Maximum time for a tap
    DOUBLE_TAP_TIME = 0.3 # Maximum time between two taps for a double tap

    def __init__(self, game_state):
        self.game_state = game_state
        self._touches = {} # Store touch events for multi-touch and gesture detection

    def on_touch_down(self, touch):
        """Called when a touch is initiated."""
        if self.game_state.game_over:
            # If game over, any tap restarts or goes to menu
            if len(self._touches) == 0: # First touch
                self._touches[touch.uid] = touch
                touch.ud['down_time'] = touch.time_start
                touch.ud['start_pos'] = touch.pos
            elif len(self._touches) == 1: # Second touch for two-finger tap
                self._touches[touch.uid] = touch
                self.game_state.reset_game() # Two-finger tap for menu (for now, restart)
                self.game_state.game_over = False
                self.game_state.paused = False
                self._touches.clear() # Clear touches after action
            return True # Consume the touch

        if self.game_state.paused:
            # If paused, only the pause button should unpause.
            # Touch gestures on the game area should not affect the game.
            return False # Do not consume touch, let other widgets handle it (e.g., buttons)

        self._touches[touch.uid] = touch
        touch.ud['down_time'] = touch.time_start
        touch.ud['start_pos'] = touch.pos
        touch.ud['moved'] = False
        return True # Consume the touch

    def on_touch_move(self, touch):
        """Called when a touch is moved."""
        if self.game_state.game_over or self.game_state.paused:
            return False

        if touch.uid in self._touches:
            if Vector(*touch.pos).distance(touch.ud['start_pos']) > self.SWIPE_THRESHOLD:
                touch.ud['moved'] = True
                # Detect horizontal swipe
                if abs(touch.dx) > abs(touch.dy):
                    if touch.dx > 0:
                        self.game_state.move_tetromino(1, 0) # Move right
                    else:
                        self.game_state.move_tetromino(-1, 0) # Move left
                # Detect vertical swipe (soft drop)
                elif touch.dy < 0: # Only downward swipe for soft drop
                    self.game_state.move_tetromino(0, 1)
                
                # Reset start_pos to prevent continuous movement from a single long swipe
                touch.ud['start_pos'] = touch.pos
        return True # Consume the touch

    def on_touch_up(self, touch):
        """Called when a touch is released."""
        if self.game_state.game_over:
            # Single tap on game over screen restarts
            if len(self._touches) == 1 and not touch.ud['moved'] and (touch.time_end - touch.ud['down_time']) < self.TAP_MAX_TIME:
                self.game_state.reset_game()
                self.game_state.game_over = False
                self.game_state.paused = False
            self._touches.pop(touch.uid, None)
            return True

        if self.game_state.paused:
            self._touches.pop(touch.uid, None)
            return False

        if touch.uid in self._touches:
            # Check for tap (rotate)
            # Safely get 'moved' status, defaulting to True if not set (meaning it moved significantly or was not a tap)
            moved = touch.ud.get('moved', True)
            if not moved and (touch.time_end - touch.ud['down_time']) < self.TAP_MAX_TIME:
                # Check for double tap (hard drop)
                if hasattr(self, '_last_tap_time') and \
                   (touch.time_start - self._last_tap_time) < self.DOUBLE_TAP_TIME and \
                   Vector(*touch.pos).distance(self._last_tap_pos) < self.TAP_MAX_DIST:
                    self.game_state.drop_tetromino() # Double tap for hard drop
                    del self._last_tap_time # Reset for next double tap
                    del self._last_tap_pos
                else:
                    self.game_state.try_rotate() # Single tap for rotate
                    self._last_tap_time = touch.time_end
                    self._last_tap_pos = touch.pos
            
            self._touches.pop(touch.uid, None)
        return True # Consume the touch
