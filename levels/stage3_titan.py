# levels/stage3_titan.py

"""
STAGE 3 — TITAN

Stable Titan cosmic battlefield.

IMPORTANT:
Do not change base_level.py.
Do not change asset_manager.py.
Do not change stages.py.

Only replace this file.
"""

import pygame
import random

from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG
from core.asset_manager import assets
from objects.fragment import Fragment


class Stage3Titan(BaseLevel):

    def __init__(self, difficulty: str):

        # ---------------------------------------------------------
        # BASE LEVEL
        # ---------------------------------------------------------

        super().__init__(3, difficulty)

        # ---------------------------------------------------------
        # SCREEN
        # ---------------------------------------------------------

        self.screen_width = 1280
        self.screen_height = 720

        # ---------------------------------------------------------
        # TITAN BACKGROUND
        # ---------------------------------------------------------

        self.bg_image = assets.get_image(
            "backgrounds/stage3_titan.jpg",
            size=(
                1280,
                720
            )
        )

        # ---------------------------------------------------------
        # DECORATION
        # ---------------------------------------------------------

        self.platforms = []

        self.space_particles = []

        # ---------------------------------------------------------
        # SETUP
        # ---------------------------------------------------------

        self.setup()

    # =============================================================
    # SETUP
    # =============================================================

    def setup(self):

        cfg = STAGE_CONFIG[3]

        # ---------------------------------------------------------
        # PLAYER START
        # ---------------------------------------------------------

        self.player_start = cfg.get(
            "player_start",
            (150, 360)
        )

        # ---------------------------------------------------------
        # WORLD
        # ---------------------------------------------------------

        self.world_w = cfg.get(
            "world_size",
            (1920, 1080)
        )[0]

        self.world_h = cfg.get(
            "world_size",
            (1920, 1080)
        )[1]

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

        # Top boundary

        self.walls.append(
            pygame.Rect(
                0,
                0,
                self.world_w,
                35
            )
        )

        # Bottom boundary

        self.walls.append(
            pygame.Rect(
                0,
                self.world_h - 35,
                self.world_w,
                35
            )
        )

        # Left boundary

        self.walls.append(
            pygame.Rect(
                0,
                0,
                35,
                self.world_h
            )
        )

        # Right boundary

        self.walls.append(
            pygame.Rect(
                self.world_w - 35,
                0,
                35,
                self.world_h
            )
        )

        # ---------------------------------------------------------
        # TITAN BATTLEFIELD
        # ---------------------------------------------------------

        platform_data = [

            # Main battlefield
            (50, 780, 1720, 60),

            # Left platform
            (100, 570, 280, 45),

            # Middle-left
            (430, 430, 280, 45),

            # Centre
            (720, 580, 280, 45),

            # Upper centre
            (850, 390, 280, 45),

            # Upper right
            (1100, 460, 280, 45),

            # Lower right
            (1220, 650, 280, 45),

            # Far right
            (1500, 520, 280, 45),
        ]

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
            (380, 520),
            (620, 370),
            (900, 520),
            (1210, 410),
            (1510, 460),
        ]

        for x, y in fragment_positions:

            self.fragments.append(
                Fragment(
                    x,
                    y
                )
            )

        # ---------------------------------------------------------
        # COSMIC PARTICLES
        # ---------------------------------------------------------

        self.space_particles = []

        for _ in range(80):

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
                        5.0,
                        15.0
                    )
                }
            )

    # =============================================================
    # BACKGROUND
    # =============================================================

    def draw_background(
        self,
        surface
    ):

        # ---------------------------------------------------------
        # TITAN IMAGE
        # ---------------------------------------------------------

        surface.blit(
            self.bg_image,
            (
                0,
                0
            )
        )

        # ---------------------------------------------------------
        # COSMIC DUST
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

            pygame.draw.circle(
                surface,
                (
                    235,
                    225,
                    255
                ),
                (
                    int(particle["x"]),
                    int(particle["y"])
                ),
                particle["size"]
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
        # TITAN PLATFORMS
        # ---------------------------------------------------------

        for platform in self.platforms:

            sx = (
                platform.x
                - int(self.camera.offset_x)
            )

            sy = (
                platform.y
                - int(self.camera.offset_y)
            )

            screen_rect = pygame.Rect(
                sx,
                sy,
                platform.width,
                platform.height
            )

            # Rocky platform

            pygame.draw.rect(
                surface,
                (
                    38,
                    30,
                    42
                ),
                screen_rect
            )

            # Purple stone border

            pygame.draw.rect(
                surface,
                (
                    105,
                    70,
                    135
                ),
                screen_rect,
                2
            )

            # Orange energy strip

            pygame.draw.rect(
                surface,
                (
                    220,
                    100,
                    40
                ),
                (
                    screen_rect.x + 10,
                    screen_rect.bottom - 7,
                    screen_rect.width - 20,
                    3
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

        if (
            self.portal_mgr
            and label_font
        ):

            self.portal_mgr.draw_prompts(
                surface,
                self.camera,
                player_rect,
                label_font
            )


# ================================================================
# COMPATIBILITY ALIASES
# ================================================================
#
# These make the file compatible if the main game imports the
# stage using one of these class names.
#

Stage3 = Stage3Titan
Stage3Level = Stage3Titan
TitanLevel = Stage3Titan