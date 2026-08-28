# levels/stage4_snow.py

"""
Stage 4 — Snow Mountain
"""

import pygame
import random

from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG
from core.asset_manager import assets


class Stage4Snow(BaseLevel):

    def __init__(self, difficulty: str):

        # ---------------------------------------------------------
        # BASE LEVEL
        # ---------------------------------------------------------

        super().__init__(4, difficulty)

        # ---------------------------------------------------------
        # SCREEN
        # ---------------------------------------------------------

        self.screen_width = 1280
        self.screen_height = 720

        # ---------------------------------------------------------
        # SNOW MOUNTAIN BACKGROUND
        # ---------------------------------------------------------

        self.bg_image = assets.get_image(
            "backgrounds/stage4_snow_mountain.jpg",
            size=(1280, 720)
        )

        # ---------------------------------------------------------
        # SNOW PARTICLES
        # ---------------------------------------------------------

        self.snow_particles = []

        for _ in range(80):

            self.snow_particles.append(
                {
                    "x": random.randint(0, 1279),
                    "y": random.randint(0, 719),
                    "size": random.randint(1, 3),
                    "speed": random.uniform(15, 35)
                }
            )

        # ---------------------------------------------------------
        # SETUP
        # ---------------------------------------------------------

        self.setup()

    # =============================================================
    # SETUP
    # =============================================================

    def setup(self):

        cfg = STAGE_CONFIG[4]

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
            )
        ]

        # ---------------------------------------------------------
        # SNOWY ROCK / MOUNTAIN BLOCKS
        # ---------------------------------------------------------

        blocks = [

            # Left mountain
            (80, 380, 260, 180),

            # Upper left
            (400, 180, 250, 180),

            # Centre
            (700, 400, 280, 180),

            # Upper centre
            (900, 150, 250, 170),

            # Upper right
            (1180, 280, 280, 190),

            # Lower right
            (1450, 470, 300, 190),

            # Ground
            (60, 760, 1700, 60)
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

        # ---------------------------------------------------------
        # PORTALS
        # ---------------------------------------------------------

        self.generate_portals(
            player_start
        )

        # ---------------------------------------------------------
        # FRAGMENTS
        # ---------------------------------------------------------

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
        # SNOW MOUNTAIN JPG
        # ---------------------------------------------------------

        surface.blit(
            self.bg_image,
            (0, 0)
        )

        # ---------------------------------------------------------
        # FALLING SNOW
        # ---------------------------------------------------------

        for snow in self.snow_particles:

            snow["y"] += (
                snow["speed"] * 0.016
            )

            if snow["y"] > 720:

                snow["y"] = -5

                snow["x"] = random.randint(
                    0,
                    1279
                )

            pygame.draw.circle(
                surface,
                (
                    245,
                    250,
                    255
                ),
                (
                    int(snow["x"]),
                    int(snow["y"])
                ),
                snow["size"]
            )

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
        # SNOWY BLOCKS
        # ---------------------------------------------------------

        for wall in self.walls:

            # Skip outside boundary walls

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

            # Rock body

            pygame.draw.rect(
                surface,
                (
                    45,
                    50,
                    65
                ),
                screen_rect
            )

            # Snow cap

            pygame.draw.rect(
                surface,
                (
                    225,
                    235,
                    245
                ),
                (
                    screen_rect.x,
                    screen_rect.y,
                    screen_rect.width,
                    10
                )
            )

            # Edge

            pygame.draw.rect(
                surface,
                (
                    150,
                    175,
                    200
                ),
                screen_rect,
                2
            )

        # ---------------------------------------------------------
        # PORTALS
        # ---------------------------------------------------------

        if self.portal_mgr:

            self.portal_mgr.draw(
                surface,
                self.camera,
                label_font
            )

        # ---------------------------------------------------------
        # FRAGMENTS
        # ---------------------------------------------------------

        for fragment in self.fragments:

            fragment.draw(
                surface,
                self.camera
            )

        # ---------------------------------------------------------
        # ENVIRONMENT EFFECTS
        # ---------------------------------------------------------

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