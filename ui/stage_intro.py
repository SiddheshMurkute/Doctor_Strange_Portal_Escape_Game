import pygame
import math

from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.asset_manager import assets


STAGE_SUBTITLES = {
    1: "NEW YORK CITY",
    2: "SPACESHIP",
    3: "TITAN",
    4: "SNOW MTN",
    5: "NETHERWORLD",
}

STAGE_COLORS = {
    1: (255, 160, 0),
    2: (0, 200, 255),
    3: (190, 80, 255),
    4: (120, 210, 255),
    5: (255, 90, 20),
}


class StageIntro:

    def __init__(
        self,
        font_large,
        font_med,
        font_small,
        stage,
        timer
    ):
        self.fl = font_large
        self.fm = font_med
        self.fs = font_small

        self.stage = stage
        self.timer = timer
        self.time = 0.0

        self.color = STAGE_COLORS.get(
            stage,
            (255, 160, 0)
        )

        # ========================================================
        # INTRO BACKGROUND
        # ========================================================

        intro_images = {
            1: "backgrounds/stage1_intro.jpg",
            2: "backgrounds/stage2_intro.jpg",
            3: "backgrounds/stage3_intro.jpg",
            4: "backgrounds/stage4_intro.jpg",
            5: "backgrounds/stage5_intro.jpg",
        }

        self.background = None

        image_path = intro_images.get(stage)

        if image_path:

            try:
                self.background = assets.get_image(
                    image_path,
                    size=(
                        SCREEN_WIDTH,
                        SCREEN_HEIGHT
                    )
                )

                print(
                    "Loaded intro:",
                    image_path
                )

            except Exception as error:

                print(
                    "ERROR loading intro:",
                    image_path
                )

                print(error)

                self.background = None

    # ============================================================
    # EVENT
    # ============================================================

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER
            ):

                return "start"

        return None

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, dt):

        self.time += dt

    # ============================================================
    # FALLBACK SCREEN
    # ============================================================

    def draw_fallback(self, surface):

        surface.fill(
            (20, 5, 5)
        )

        # --------------------------------------------------------
        # NETHERWORLD FALLBACK
        # --------------------------------------------------------

        if self.stage == 5:

            for y in range(SCREEN_HEIGHT):

                p = y / SCREEN_HEIGHT

                r = int(20 + 50 * p)
                g = int(5 + 10 * p)
                b = int(5 + 5 * p)

                pygame.draw.line(
                    surface,
                    (r, g, b),
                    (0, y),
                    (SCREEN_WIDTH, y)
                )

            # Lava
            pygame.draw.polygon(
                surface,
                (100, 20, 5),
                [
                    (0, 620),
                    (150, 570),
                    (300, 640),
                    (470, 590),
                    (650, 650),
                    (850, 570),
                    (1050, 630),
                    (1280, 560),
                    (1280, SCREEN_HEIGHT),
                    (0, SCREEN_HEIGHT)
                ]
            )

            # Floating rocks
            for i in range(10):

                x = (i * 157) % SCREEN_WIDTH
                y = 250 + ((i * 91) % 300)

                pygame.draw.polygon(
                    surface,
                    (45, 20, 18),
                    [
                        (x, y),
                        (x + 100, y - 15),
                        (x + 130, y + 45),
                        (x + 40, y + 70)
                    ]
                )

            # Fire particles
            for i in range(100):

                x = (i * 137) % SCREEN_WIDTH

                y = (
                    i * 73
                    - int(self.time * 80)
                ) % SCREEN_HEIGHT

                pygame.draw.circle(
                    surface,
                    (255, 120, 20),
                    (x, y),
                    2 + (i % 3)
                )

        else:

            surface.fill(
                (10, 10, 20)
            )

        # --------------------------------------------------------
        # TITLE
        # --------------------------------------------------------

        title = self.fl.render(
            f"STAGE {self.stage}",
            True,
            self.color
        )

        title_rect = title.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                90
            )
        )

        surface.blit(
            title,
            title_rect
        )

        # --------------------------------------------------------
        # SUBTITLE
        # --------------------------------------------------------

        subtitle = self.fl.render(
            STAGE_SUBTITLES.get(
                self.stage,
                ""
            ),
            True,
            (255, 255, 255)
        )

        subtitle_rect = subtitle.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                155
            )
        )

        surface.blit(
            subtitle,
            subtitle_rect
        )

        # --------------------------------------------------------
        # MISSION
        # --------------------------------------------------------

        mission = self.fm.render(
            "MISSION: FIND AND ENTER THE CORRECT PORTAL",
            True,
            (235, 235, 235)
        )

        mission_rect = mission.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                510
            )
        )

        surface.blit(
            mission,
            mission_rect
        )

        # --------------------------------------------------------
        # TIMER
        # --------------------------------------------------------

        timer_text = self.fm.render(
            f"TIME LIMIT: {self.timer} SECONDS",
            True,
            (255, 190, 50)
        )

        timer_rect = timer_text.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                560
            )
        )

        surface.blit(
            timer_text,
            timer_rect
        )

        # --------------------------------------------------------
        # ENTER
        # --------------------------------------------------------

        if int(self.time * 2) % 2 == 0:

            enter = self.fs.render(
                "PRESS ENTER TO BEGIN",
                True,
                (255, 255, 255)
            )

            enter_rect = enter.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT - 50
                )
            )

            surface.blit(
                enter,
                enter_rect
            )

    # ============================================================
    # DRAW
    # ============================================================

    def draw(self, surface):

        # ========================================================
        # IMPORTANT:
        # If JPG loaded successfully, SHOW IT DIRECTLY.
        # ========================================================

        if self.background is not None:

            surface.blit(
                self.background,
                (
                    0,
                    0
                )
            )

            # Slight dark overlay so the image remains readable.
            overlay = pygame.Surface(
                (
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 25)
            )

            surface.blit(
                overlay,
                (
                    0,
                    0
                )
            )

            # ----------------------------------------------------
            # ENTER ANIMATION
            # ----------------------------------------------------

            pulse = (
                0.5
                + 0.5 * math.sin(
                    self.time * 3
                )
            )

            alpha = int(
                150 + pulse * 105
            )

            enter = self.fs.render(
                "PRESS ENTER TO BEGIN",
                True,
                (255, 255, 255)
            )

            enter.set_alpha(
                alpha
            )

            enter_rect = enter.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT - 45
                )
            )

            surface.blit(
                enter,
                enter_rect
            )

            return

        # ========================================================
        # JPG FAILED TO LOAD
        # ========================================================

        self.draw_fallback(
            surface
        )