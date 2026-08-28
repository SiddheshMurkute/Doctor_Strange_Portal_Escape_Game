# levels/stage2_space.py

"""
Stage 2 — SPACE

Simple and stable space level.
Uses the existing BaseLevel systems for:
- camera
- portals
- fragments
- environment effects
- collision
"""

import pygame
import random

from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG
from core.asset_manager import assets
from objects.fragment import Fragment


class Stage2Space(BaseLevel):

    def __init__(self, difficulty: str):

        super().__init__(2, difficulty)

        # ---------------------------------------------------------
        # SCREEN SIZE
        # ---------------------------------------------------------

        self.screen_width = 1280
        self.screen_height = 720

        # ---------------------------------------------------------
        # SPACE BACKGROUND
        # ---------------------------------------------------------

        self.bg_image = assets.get_image(
            "backgrounds/stage2_space.jpg",
            size=(
                self.screen_width,
                self.screen_height
            )
        )

        # ---------------------------------------------------------
        # PLATFORMS
        # ---------------------------------------------------------

        self.platforms = []

        # ---------------------------------------------------------
        # PARTICLES
        # ---------------------------------------------------------

        self.space_particles = []

        # ---------------------------------------------------------
        # SETUP
        # ---------------------------------------------------------

        self.setup()

    # =============================================================
    # SETUP
    # =============================================================

    def setup(self):

        cfg = STAGE_CONFIG[2]

        # ---------------------------------------------------------
        # PLAYER START
        # ---------------------------------------------------------

        self.player_start = cfg.get(
            "player_start",
            (150, 650)
        )

        # ---------------------------------------------------------
        # WORLD
        # ---------------------------------------------------------

        self.world_w = 1920
        self.world_h = 1080

        self.world_rect = pygame.Rect(
            0,
            0,
            self.world_w,
            self.world_h
        )

        # ---------------------------------------------------------
        # COLLISION WALLS
        # ---------------------------------------------------------

        self.walls = []

        # Top wall

        self.walls.append(
            pygame.Rect(
                0,
                0,
                self.world_w,
                30
            )
        )

        # Bottom wall

        self.walls.append(
            pygame.Rect(
                0,
                self.world_h - 30,
                self.world_w,
                30
            )
        )

        # Left wall

        self.walls.append(
            pygame.Rect(
                0,
                0,
                30,
                self.world_h
            )
        )

        # Right wall

        self.walls.append(
            pygame.Rect(
                self.world_w - 30,
                0,
                30,
                self.world_h
            )
        )

        # ---------------------------------------------------------
        # SPACE PLATFORMS
        # ---------------------------------------------------------

        platform_data = [

            (80, 760, 420, 50),

            (180, 550, 280, 40),

            (500, 430, 280, 40),

            (760, 600, 300, 40),

            (1000, 400, 300, 40),

            (1180, 600, 300, 40),

            (1450, 480, 300, 40),

        ]

        self.platforms = []

        for x, y, width, height in platform_data:

            rect = pygame.Rect(
                x,
                y,
                width,
                height
            )

            self.platforms.append(rect)

        # Add platforms to collision

        self.walls.extend(
            self.platforms
        )

        # ---------------------------------------------------------
        # PORTALS
        # ---------------------------------------------------------

        self.generate_portals(
            self.player_start
        )

        # ---------------------------------------------------------
        # FRAGMENTS
        # ---------------------------------------------------------

        self.fragments = []

        fragment_positions = [
            (400, 500),
            (650, 380),
            (900, 550),
            (1200, 350),
            (1500, 430),
        ]

        for x, y in fragment_positions:

            self.fragments.append(
                Fragment(
                    x,
                    y
                )
            )

        # ---------------------------------------------------------
        # SPACE PARTICLES
        # ---------------------------------------------------------

        for _ in range(100):

            self.space_particles.append(
                {
                    "x": random.randint(
                        0,
                        self.screen_width
                    ),

                    "y": random.randint(
                        0,
                        self.screen_height
                    ),

                    "size": random.randint(
                        1,
                        3
                    ),

                    "speed": random.uniform(
                        5,
                        20
                    ),

                    "alpha": random.randint(
                        100,
                        220
                    )
                }
            )

    # =============================================================
    # BACKGROUND
    # =============================================================

    def draw_background(
        self,
        surface: pygame.Surface
    ):

        # ---------------------------------------------------------
        # DRAW IMAGE
        # ---------------------------------------------------------

        if self.bg_image is not None:

            surface.blit(
                self.bg_image,
                (0, 0)
            )

        else:

            # Fallback if image cannot be loaded

            surface.fill(
                (
                    8,
                    5,
                    25
                )
            )

        # ---------------------------------------------------------
        # SPACE STARS
        # ---------------------------------------------------------

        for particle in self.space_particles:

            particle["y"] -= (
                particle["speed"] * 0.016
            )

            if particle["y"] < 0:

                particle["y"] = (
                    self.screen_height
                )

                particle["x"] = random.randint(
                    0,
                    self.screen_width
                )

            size = particle["size"]

            pygame.draw.circle(
                surface,
                (
                    220,
                    220,
                    255
                ),
                (
                    int(particle["x"]),
                    int(particle["y"])
                ),
                size
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
        # PLATFORMS
        # ---------------------------------------------------------

        for platform in self.platforms:

            screen_rect = pygame.Rect(
                platform.x - int(self.camera.offset_x),
                platform.y - int(self.camera.offset_y),
                platform.width,
                platform.height
            )

            # Dark platform

            pygame.draw.rect(
                surface,
                (
                    25,
                    20,
                    45
                ),
                screen_rect
            )

            # Purple outline

            pygame.draw.rect(
                surface,
                (
                    100,
                    70,
                    150
                ),
                screen_rect,
                2
            )

            # Blue energy line

            pygame.draw.rect(
                surface,
                (
                    60,
                    130,
                    255
                ),
                (
                    screen_rect.x + 8,
                    screen_rect.bottom - 5,
                    screen_rect.width - 16,
                    2
                )
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