# levels/stage1_new_york.py

"""Stage 1 — New York City."""

import pygame
import math
import random

from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG
from core.asset_manager import assets


class Stage1NewYork(BaseLevel):

    def __init__(self, difficulty: str):

        super().__init__(1, difficulty)

        # -----------------------------------------------------------
        # NEW YORK BACKGROUND
        # -----------------------------------------------------------

        self.bg_image = assets.get_image(
            "backgrounds/stage1_bg.jpg",
            size=(1280, 720)
        )

        self.setup()

    # ---------------------------------------------------------------
    # SETUP
    # ---------------------------------------------------------------

    def setup(self):

        cfg = STAGE_CONFIG[1]

        ps = cfg["player_start"]

        ww = self.world_w
        wh = self.world_h

        # -----------------------------------------------------------
        # OUTER WALLS
        # -----------------------------------------------------------

        self.walls = [

            pygame.Rect(
                0,
                0,
                ww,
                40
            ),

            pygame.Rect(
                0,
                wh - 40,
                ww,
                40
            ),

            pygame.Rect(
                0,
                0,
                40,
                wh
            ),

            pygame.Rect(
                ww - 40,
                0,
                40,
                wh
            ),
        ]

        # -----------------------------------------------------------
        # NYC BUILDING / STREET BLOCKS
        # -----------------------------------------------------------

        blocks = [

            (80, 80, 260, 200),

            (400, 80, 260, 200),

            (720, 80, 260, 200),

            (1040, 80, 260, 200),

            (1380, 80, 260, 200),

            (1640, 80, 220, 200),

            (80, 380, 240, 200),

            (400, 380, 240, 200),

            (720, 380, 240, 200),

            (1040, 380, 240, 200),

            (1380, 380, 220, 200),

            (1640, 380, 220, 200),

            (80, 700, 220, 280),

            (380, 700, 220, 280),

            (700, 700, 220, 280),

            (1040, 700, 220, 280),

            (1380, 700, 220, 280),

            (1640, 700, 220, 280),
        ]

        for bx, by, bw, bh in blocks:

            self.walls.append(
                pygame.Rect(
                    bx,
                    by,
                    bw,
                    bh
                )
            )

        # -----------------------------------------------------------
        # PORTALS
        # -----------------------------------------------------------

        self.generate_portals(ps)

        # -----------------------------------------------------------
        # FRAGMENTS
        # -----------------------------------------------------------

        self.generate_fragments(
            cfg["fragment_count"]
        )

    # ---------------------------------------------------------------
    # BACKGROUND
    # ---------------------------------------------------------------

    def draw_background(
        self,
        surface: pygame.Surface
    ):

        # Draw the new NYC background
        surface.blit(
            self.bg_image,
            (0, 0)
        )