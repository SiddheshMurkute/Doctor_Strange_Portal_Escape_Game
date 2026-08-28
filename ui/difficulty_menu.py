# ui/difficulty_menu.py

import os
import pygame


class DifficultyMenu:
    """
    Image-based difficulty selection screen.

    The complete visual design comes from:
        assets/backgrounds/difficulty_menu.jpg

    Internal values are lowercase so this also works with older
    EnemyManager code that expects "easy", "medium", "hard".
    """

    def __init__(self, font_large=None, font_med=None, font_small=None):
        pygame.init()

        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((1280, 720))

        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        self.font_large = font_large or pygame.font.SysFont(
            "arial", 42, bold=True
        )
        self.font_med = font_med or pygame.font.SysFont(
            "arial", 28, bold=True
        )
        self.font_small = font_small or pygame.font.SysFont(
            "arial", 20
        )

        # Keep these names compatible with the rest of the game.
        self.options = ["easy", "medium", "hard"]
        self.difficulties = self.options

        self.selected = 1          # medium
        self.result = None
        self.running = True

        self.background = self._load_background()
        self._create_buttons()

    # -------------------------------------------------------------
    # IMAGE LOADING
    # -------------------------------------------------------------

    def _load_background(self):
        """
        Find difficulty_menu.jpg reliably.

        First checks the normal project location, then searches the
        project folder for the filename. This prevents the menu from
        becoming a blank fallback screen because of a path mismatch.
        """

        ui_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(ui_dir)

        candidates = [
            os.path.join(
                project_root,
                "assets",
                "backgrounds",
                "difficulty_menu.jpg",
            ),
            os.path.join(
                project_root,
                "assets",
                "backgrounds",
                "difficulty_menu.jpeg",
            ),
            os.path.join(
                project_root,
                "assets",
                "backgrounds",
                "difficulty_menu.png",
            ),
            os.path.join(os.getcwd(), "assets", "backgrounds",
                         "difficulty_menu.jpg"),
        ]

        # Add any matching file found anywhere in the project.
        if os.path.isdir(project_root):
            for root, dirs, files in os.walk(project_root):
                dirs[:] = [
                    d for d in dirs
                    if d not in {".git", ".venv", "__pycache__"}
                ]
                for filename in files:
                    if filename.lower() in {
                        "difficulty_menu.jpg",
                        "difficulty_menu.jpeg",
                        "difficulty_menu.png",
                    }:
                        candidates.append(os.path.join(root, filename))

        # Remove duplicates while preserving order.
        unique_candidates = []
        seen = set()

        for path in candidates:
            normalized = os.path.normcase(os.path.abspath(path))
            if normalized not in seen:
                seen.add(normalized)
                unique_candidates.append(path)

        print()
        print("========================================")
        print("LOADING DIFFICULTY IMAGE")
        print("========================================")

        for image_path in unique_candidates:
            if not os.path.isfile(image_path):
                continue

            try:
                image = pygame.image.load(image_path).convert()
                print("DIFFICULTY IMAGE LOADED:")
                print(image_path)
                print("========================================")
                print()
                return image
            except pygame.error as error:
                print("Found image but pygame could not load it:")
                print(image_path)
                print(error)

        print("WARNING: difficulty_menu.jpg was NOT FOUND.")
        print("Expected:")
        print(
            os.path.join(
                project_root,
                "assets",
                "backgrounds",
                "difficulty_menu.jpg",
            )
        )
        print("========================================")
        print()

        return None

    # -------------------------------------------------------------
    # BUTTON AREAS
    # -------------------------------------------------------------

    def _create_buttons(self):
        self.width, self.height = self.screen.get_size()
        self.buttons = []

        # Positions match the three cards in the supplied JPG.
        # These are invisible click areas.
        card_width = int(self.width * 0.205)
        card_height = int(self.height * 0.48)
        center_y = int(self.height * 0.58)

        centers = [
            int(self.width * 0.255),  # EASY
            int(self.width * 0.500),  # MEDIUM
            int(self.width * 0.745),  # HARD
        ]

        for center_x in centers:
            self.buttons.append(
                pygame.Rect(
                    center_x - card_width // 2,
                    center_y - card_height // 2,
                    card_width,
                    card_height,
                )
            )

    def _refresh(self):
        if self.screen is None:
            return

        new_width, new_height = self.screen.get_size()

        if new_width != self.width or new_height != self.height:
            self._create_buttons()

    # -------------------------------------------------------------
    # SELECTION
    # -------------------------------------------------------------

    def select_difficulty(self, index):
        self.selected = index % len(self.options)

    # -------------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------------

    def update(self, *args, **kwargs):
        if self.screen is None:
            self.screen = pygame.display.get_surface()
            if self.screen is None:
                return

        self._refresh()

    # -------------------------------------------------------------
    # EVENTS
    # -------------------------------------------------------------

    def handle_event(self, event, mouse=None):
        if event is None:
            return None

        if event.type == pygame.QUIT:
            self.running = False
            self.result = None
            return None

        if event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_UP, pygame.K_LEFT):
                self.select_difficulty(self.selected - 1)
                return None

            if event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                self.select_difficulty(self.selected + 1)
                return None

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.result = self.options[self.selected]
                print("DIFFICULTY SELECTED:", self.result)
                return self.result

            if event.key == pygame.K_ESCAPE:
                # Returning None keeps the existing game state.
                self.result = None
                return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            position = event.pos

            for index, rect in enumerate(self.buttons):
                if rect.collidepoint(position):
                    self.selected = index
                    self.result = self.options[self.selected]
                    print("DIFFICULTY SELECTED:", self.result)
                    return self.result

        return None

    # -------------------------------------------------------------
    # DRAW
    # -------------------------------------------------------------

    def draw(self, screen=None, *args, **kwargs):
        if isinstance(screen, pygame.Surface):
            self.screen = screen
        else:
            current_screen = pygame.display.get_surface()
            if current_screen is not None:
                self.screen = current_screen

        if self.screen is None:
            return

        self._refresh()

        # IMPORTANT:
        # Draw the saved JPG as the entire background.
        if self.background is not None:
            background = pygame.transform.smoothscale(
                self.background,
                (self.width, self.height),
            )
            self.screen.blit(background, (0, 0))
        else:
            # Only used if the JPG genuinely cannot be found.
            self.screen.fill((8, 5, 20))

            title = self.font_large.render(
                "SELECT DIFFICULTY",
                True,
                (255, 200, 40),
            )
            self.screen.blit(
                title,
                title.get_rect(
                    center=(
                        self.width // 2,
                        int(self.height * 0.25),
                    )
                ),
            )

        # Draw only a selection outline.
        # The JPG itself supplies all text, cards and artwork.
        if 0 <= self.selected < len(self.buttons):
            pygame.draw.rect(
                self.screen,
                (255, 200, 40),
                self.buttons[self.selected],
                3,
                border_radius=8,
            )

    # -------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------

    def get_selected(self):
        return self.options[self.selected]

    # -------------------------------------------------------------
    # STANDALONE TEST
    # -------------------------------------------------------------

    def run(self):
        self.running = True
        self.result = None

        while self.running:
            for event in pygame.event.get():
                result = self.handle_event(event)
                if result is not None:
                    self.result = result
                    self.running = False

            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        return self.result


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Doctor Strange - Difficulty")

    menu = DifficultyMenu()
    result = menu.run()

    print("Final difficulty:", result)

    pygame.quit()
