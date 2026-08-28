# levels/stage5_netherworld.py

"""
Stage 5 — Netherworld (Hell)
Doctor Doom Battle
"""

import pygame
import random

from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG
from core.asset_manager import assets


class Stage5Netherworld(BaseLevel):

    def __init__(self, difficulty: str):

        # =========================================================
        # BASE LEVEL
        # =========================================================

        super().__init__(5, difficulty)

        # =========================================================
        # SCREEN
        # =========================================================

        self.screen_width = 1280
        self.screen_height = 720

        # =========================================================
        # BACKGROUND
        # =========================================================

        self.bg_image = assets.get_image(
            "backgrounds/stage5_netherworld_hell.jpg",
            size=(1280, 720)
        )

        # =========================================================
        # EMBER PARTICLES
        # =========================================================

        self.ember_particles = []

        for _ in range(120):

            self.ember_particles.append(
                {
                    "x": random.randint(0, 1279),
                    "y": random.randint(0, 719),
                    "size": random.randint(1, 3),
                    "speed": random.uniform(20, 60),
                }
            )

        # =========================================================
        # SETUP
        # =========================================================

        self.setup()

    # =============================================================
    # SETUP
    # =============================================================

    def setup(self):

        cfg = STAGE_CONFIG[5]

        # ---------------------------------------------------------
        # PLAYER START
        # ---------------------------------------------------------

        player_start = cfg["player_start"]

        # ---------------------------------------------------------
        # WORLD
        # ---------------------------------------------------------

        world_w = self.world_w
        world_h = self.world_h

        # ---------------------------------------------------------
        # OUTER WALLS
        # ---------------------------------------------------------

        self.walls = [

            pygame.Rect(
                0,
                0,
                world_w,
                40
            ),

            pygame.Rect(
                0,
                world_h - 40,
                world_w,
                40
            ),

            pygame.Rect(
                0,
                0,
                40,
                world_h
            ),

            pygame.Rect(
                world_w - 40,
                0,
                40,
                world_h
            ),
        ]

        # =========================================================
        # NETHERWORLD PLATFORMS
        # =========================================================

        blocks = [

            # Left platform
            (80, 390, 250, 170),

            # Upper-left platform
            (390, 180, 240, 170),

            # Centre arena
            (680, 390, 300, 190),

            # Upper-centre platform
            (900, 150, 250, 180),

            # Right platform
            (1180, 300, 280, 190),

            # Lower-right platform
            (1450, 470, 300, 190),

            # Ground
            (60, 760, 1700, 60),
        ]

        for x, y, width, height in blocks:

            self.walls.append(
                pygame.Rect(
                    x,
                    y,
                    width,
                    height
                )
            )

        # =========================================================
        # PORTALS
        # =========================================================

        self.generate_portals(
            player_start
        )

        # =========================================================
        # FRAGMENTS
        # =========================================================

        self.generate_fragments(
            cfg["fragment_count"]
        )

    # =============================================================
    # BACKGROUND
    # =============================================================

    def draw_background(
        self,
        surface: pygame.Surface
    ):

        # ---------------------------------------------------------
        # DRAW JPG
        # ---------------------------------------------------------

        surface.blit(
            self.bg_image,
            (0, 0)
        )

        # ---------------------------------------------------------
        # DRAW EMBERS
        # ---------------------------------------------------------

        for ember in self.ember_particles:

            # Move upward
            ember["y"] -= (
                ember["speed"] * 0.016
            )

            # Slight horizontal movement
            ember["x"] += random.uniform(
                -0.35,
                0.35
            )

            # -----------------------------------------------------
            # RESET
            # -----------------------------------------------------

            if ember["y"] < -5:

                ember["y"] = 725

                ember["x"] = random.randint(
                    0,
                    1279
                )

                ember["size"] = random.randint(
                    1,
                    3
                )

                ember["speed"] = random.uniform(
                    20,
                    60
                )

            # -----------------------------------------------------
            # SCREEN WRAP
            # -----------------------------------------------------

            if ember["x"] < 0:
                ember["x"] = 1279

            if ember["x"] > 1279:
                ember["x"] = 0

            # -----------------------------------------------------
            # EMBER
            # -----------------------------------------------------

            pygame.draw.circle(
                surface,
                (
                    255,
                    90,
                    20
                ),
                (
                    int(ember["x"]),
                    int(ember["y"])
                ),
                ember["size"]
            )

    # =============================================================
    # UPDATE INSTABILITY
    # =============================================================

    def update_instability(
        self,
        time_left,
        cfg_t,
        camera,
        shake
    ):
        """
        Compatibility with core/game.py.

        The main game passes:
            time_left
            cfg_t
            camera
            shake

        Stage 5 does not need additional instability logic here.
        """

        return

    # =============================================================
    # DRAW
    # =============================================================

    def draw(
        self,
        surface,
        label_font=None
    ):

        # ---------------------------------------------------------
        # BACKGROUND
        # ---------------------------------------------------------

        self.draw_background(
            surface
        )

        # ---------------------------------------------------------
        # ROCK PLATFORMS
        # ---------------------------------------------------------

        for wall in self.walls:

            # Skip outer boundary walls
            if (
                wall.x == 0
                or wall.y == 0
                or wall.right == self.world_w
                or wall.bottom == self.world_h
            ):
                continue

            screen_rect = self.camera.apply(
                wall
            )

            # -----------------------------------------------------
            # VOLCANIC ROCK
            # -----------------------------------------------------

            pygame.draw.rect(
                surface,
                (
                    38,
                    25,
                    30
                ),
                screen_rect
            )

            # -----------------------------------------------------
            # LAVA TOP
            # -----------------------------------------------------

            lava_rect = pygame.Rect(
                screen_rect.x,
                screen_rect.y,
                screen_rect.width,
                8
            )

            pygame.draw.rect(
                surface,
                (
                    220,
                    55,
                    15
                ),
                lava_rect
            )

            # -----------------------------------------------------
            # LAVA HIGHLIGHT
            # -----------------------------------------------------

            pygame.draw.line(
                surface,
                (
                    255,
                    120,
                    20
                ),
                (
                    screen_rect.x + 10,
                    screen_rect.y + 4
                ),
                (
                    screen_rect.right - 10,
                    screen_rect.y + 4
                ),
                2
            )

            # -----------------------------------------------------
            # ROCK BORDER
            # -----------------------------------------------------

            pygame.draw.rect(
                surface,
                (
                    100,
                    45,
                    35
                ),
                screen_rect,
                2
            )

        # =========================================================
        # PORTALS
        # =========================================================

        if self.portal_mgr:

            self.portal_mgr.draw(
                surface,
                self.camera,
                label_font
            )

        # =========================================================
        # FRAGMENTS
        # =========================================================

        for fragment in self.fragments:

            fragment.draw(
                surface,
                self.camera
            )

        # =========================================================
        # ENVIRONMENT EFFECTS
        # =========================================================

        self.env_fx.draw(
            surface,
            self.camera
        )

    # =============================================================
    # INTERACTION PROMPTS
    # =============================================================

    def draw_interact_prompts(
        self,
        surface,
        player_rect,
        label_font
    ):

        if self.portal_mgr and label_font:

            self.portal_mgr.draw_prompts(
                surface,
                self.camera,
                player_rect,
                label_font
            )