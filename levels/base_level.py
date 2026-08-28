# levels/base_level.py

"""
Base level system for Doctor Strange Portal Escape.

The base level handles:
- camera
- portals
- fragments
- environment effects
- collisions
- visible rooftop collision blocks
"""

import pygame
import random

from abc import ABC, abstractmethod

from core.camera import Camera
from config.stages import STAGE_CONFIG
from objects.portal_manager import PortalManager
from objects.fragment import Fragment
from effects.environment_effects import EnvironmentEffects


class BaseLevel(ABC):

    def __init__(
        self,
        stage: int,
        difficulty: str
    ):

        self.stage = stage
        self.difficulty = difficulty

        # ---------------------------------------------------------
        # STAGE CONFIG
        # ---------------------------------------------------------

        cfg = STAGE_CONFIG[stage]

        self.world_w = cfg["world_size"][0]
        self.world_h = cfg["world_size"][1]

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

        # ---------------------------------------------------------
        # CAMERA
        # ---------------------------------------------------------

        self.camera = Camera(
            self.world_w,
            self.world_h
        )

        # ---------------------------------------------------------
        # PORTALS
        # ---------------------------------------------------------

        self.portal_mgr = None

        # ---------------------------------------------------------
        # FRAGMENTS
        # ---------------------------------------------------------

        self.fragments = []

        # ---------------------------------------------------------
        # ENVIRONMENT EFFECTS
        # ---------------------------------------------------------

        self.env_fx = EnvironmentEffects(
            stage,
            self.world_w,
            self.world_h
        )

        # ---------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------

        self.portal_entered = False

        self.stage_failed = False

    # =============================================================
    # ABSTRACT METHODS
    # =============================================================

    @abstractmethod
    def setup(self):
        """
        Build:
        - walls
        - portals
        - enemies
        - fragments
        """
        pass

    @abstractmethod
    def draw_background(
        self,
        surface: pygame.Surface
    ):
        pass

    # =============================================================
    # PORTALS
    # =============================================================

    def generate_portals(
        self,
        player_start
    ):

        self.portal_mgr = PortalManager(
            self.stage,
            self.walls,
            player_start,
            self.world_rect
        )

        self.portal_mgr.generate()

    # =============================================================
    # FRAGMENTS
    # =============================================================

    def generate_fragments(
        self,
        count,
        exclusion_rects=None
    ):

        self.fragments = []

        for _ in range(count):

            for _attempt in range(100):

                x = random.randint(
                    100,
                    self.world_w - 100
                )

                y = random.randint(
                    100,
                    self.world_h - 100
                )

                rect = pygame.Rect(
                    x - 20,
                    y - 20,
                    40,
                    40
                )

                blocked = False

                # -------------------------------------------------
                # CHECK WALLS
                # -------------------------------------------------

                for wall in self.walls:

                    if rect.colliderect(
                        wall
                    ):

                        blocked = True
                        break

                # -------------------------------------------------
                # CHECK EXCLUSIONS
                # -------------------------------------------------

                if (
                    not blocked
                    and exclusion_rects
                ):

                    for exclusion in exclusion_rects:

                        if rect.colliderect(
                            exclusion
                        ):

                            blocked = True
                            break

                # -------------------------------------------------
                # CREATE FRAGMENT
                # -------------------------------------------------

                if not blocked:

                    self.fragments.append(
                        Fragment(
                            x,
                            y
                        )
                    )

                    break

    # =============================================================
    # UPDATE
    # =============================================================

    def update(
        self,
        dt: float,
        player,
        e_pressed: bool,
        score_callback
    ):

        # ---------------------------------------------------------
        # CAMERA
        # ---------------------------------------------------------

        self.camera.update(
            player.rect
        )

        # ---------------------------------------------------------
        # ENVIRONMENT
        # ---------------------------------------------------------

        self.env_fx.update(
            dt,
            self.camera.offset_x,
            self.camera.offset_y
        )

        # ---------------------------------------------------------
        # PORTALS
        # ---------------------------------------------------------

        if self.portal_mgr:

            self.portal_mgr.update(
                dt
            )

            result = self.portal_mgr.check_interaction(
                player.rect,
                e_pressed
            )

            if result == "correct":

                self.portal_entered = True

                return "correct"

            if result == "wrong":

                return "wrong"

        # ---------------------------------------------------------
        # FRAGMENTS
        # ---------------------------------------------------------

        for fragment in self.fragments:

            if fragment.collected:

                continue

            fragment.update(
                dt
            )

            if fragment.check_collect(
                player.rect
            ):

                score_callback(
                    fragment.value
                )

        return None

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
        # VISIBLE COLLISION WALLS
        # ---------------------------------------------------------
        #
        # Original style:
        # dark purple blocks
        #
        # ---------------------------------------------------------

        for wall in self.walls:

            # Don't show the outer boundary walls.
            # Only show actual level/platform blocks.

            if (
                wall.width == self.world_w
                or wall.height == self.world_h
            ):
                continue

            screen_rect = pygame.Rect(
                wall.x - self.camera.offset_x,
                wall.y - self.camera.offset_y,
                wall.width,
                wall.height
            )

            pygame.draw.rect(
                surface,
                (30, 20, 50),
                screen_rect
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
        # ENVIRONMENT PARTICLES
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