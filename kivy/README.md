
# PyTetris Kivy Port

This is a Kivy port of a classic Tetris game, originally implemented in Pygame.
It's designed for touch-based devices, with responsive scaling and gesture controls.

## Files

- `main.py`: The main Kivy application entry point.
- `game_core.py`: Contains all the core Tetris gameplay logic, independent of the UI.
- `game_ui.kv`: The Kivy Language file defining the user interface layout.
- `controls.py`: Handles touch gestures for game control.
- `requirements.txt`: Lists Python dependencies.

## Functional Requirements

- Gameplay is identical to the original Pygame version (spawning, rotation, scoring, levels, game over).
- Uses Kivy's `Clock.schedule_interval` for the main game loop.
- All keyboard events are replaced with touch input and on-screen buttons.
- Implements the SRS (Super Rotation System) for tetromino rotations.
- The UI is responsive and scales well for various mobile screen sizes.

## Touch Controls

The game features on-screen control buttons at the bottom of the screen:
- `←`: Move tetromino left
- `→`: Move tetromino right
- `↓`: Soft drop (move tetromino down one step)
- `⟳`: Rotate tetromino
- `⭳`: Hard drop (instantly drop tetromino to the bottom)

Additionally, the following touch gestures are supported on the game grid area:
- **Swipe Left/Right:** Move tetromino horizontally.
- **Swipe Down:** Soft drop.
- **Single Tap:** Rotate tetromino.
- **Double Tap:** Hard drop.
- **Two-finger Tap (on Game Over screen):** Returns to the main menu (currently restarts the game for simplicity).

## Design

- **Aesthetics:** Preserves the classic green-on-black Tetris look.
- **Layout:** The game grid is centered horizontally. Score, level, and next piece preview are displayed nearby.
- **Responsiveness:** The layout is designed to adapt to different screen orientations and sizes.

## How to Run Locally

1.  **Install Kivy:**
    ```bash
    pip install kivy
    ```
    (For detailed Kivy installation instructions, refer to the official Kivy documentation: [https://kivy.org/doc/stable/installation/installation.html](https://kivy.org/doc/stable/installation/installation.html))

2.  **Run the application:**
    ```bash
    python main.py
    ```

## How to Build and Install on Mobile Devices

### For Android (using Buildozer)

1.  **Install Buildozer:**
    ```bash
    pip install buildozer
    ```
    (Ensure you have all Buildozer dependencies installed as per its documentation: [https://buildozer.readthedocs.io/en/latest/installation.html](https://buildozer.readthedocs.io/en/latest/installation.html))

2.  **Initialize Buildozer in your project directory:**
    ```bash
    buildozer init
    ```
    This will create a `buildozer.spec` file.

3.  **Edit `buildozer.spec`:**
    -   Set `title = PyTetris Kivy`
    -   Set `package.name = pytetris`
    -   Set `package.domain = org.yourorganization` (replace with your domain)
    -   Ensure `requirements = python3,kivy`
    -   Adjust other settings as needed (e.g., `orientation`, `fullscreen`).

4.  **Build the Android APK:**
    ```bash
    buildozer android debug deploy run
    ```
    This command will build the APK, install it on a connected device (if `adb` is configured), and run it. For just building, use `buildozer android debug`.

### For iOS (using Kivy-iOS)

1.  **Set up Kivy-iOS:**
    Follow the official Kivy-iOS toolchain documentation to set up your environment on macOS: [https://kivy.org/doc/stable/guide/packaging-ios.html](https://kivy.org/doc/stable/guide/packaging-ios.html)

2.  **Create an iOS project:**
    ```bash
    toolchain create <app_name> <path_to_main.py_directory>
    ```
    For example:
    ```bash
    toolchain create pytetris .
    ```

3.  **Build the iOS app:**
    ```bash
    toolchain build pytetris
    ```

4.  **Deploy to device/simulator:**
    Use Xcode to deploy the generated `.xcodeproj` to your iPhone or simulator.

---

## Summary of Testing and Building

1.  **Local Testing:**
    -   Ensure `kivy` is installed (`pip install kivy`).
    -   Run `python main.py` from the project root.

2.  **Building for iPhone (using kivy-ios):**
    -   Requires macOS and Xcode.
    -   Install `kivy-ios` toolchain.
    -   Navigate to your project directory.
    -   Run `toolchain create pytetris .`
    -   Run `toolchain build pytetris`.
    -   Open the generated Xcode project and deploy.