# objects/fragment.py
"""Dimensional fragment collectible — polished Stage 1 visual."""

import pygame
import math


# Gameplay collision size
FRAGMENT_SIZE = 30


class Fragment:

    def __init__(self, x, y, value=150):

        self.rect = pygame.Rect(
            x - FRAGMENT_SIZE // 2,
            y - FRAGMENT_SIZE // 2,
            FRAGMENT_SIZE,
            FRAGMENT_SIZE
        )

        self.value = value
        self.collected = False

        # Animation
        self._angle = 0.0
        self._bob = 0.0
        self._pulse = 0.0

    # ---------------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------------

    def update(self, dt):

        self._angle = (
            self._angle + dt * 100
        ) % 360

        self._bob = (
            self._bob + dt * 3.0
        ) % (2 * math.pi)

        self._pulse = (
            self._pulse + dt * 4.0
        ) % (2 * math.pi)

    # ---------------------------------------------------------------
    # COLLECT
    # ---------------------------------------------------------------

    def check_collect(self, player_rect) -> bool:

        if (
            not self.collected
            and self.rect.colliderect(player_rect)
        ):

            self.collected = True
            return True

        return False

    # ---------------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------------

    def draw(self, surface, camera):

        if self.collected:
            return

        cx = (
            self.rect.centerx
            - int(camera.offset_x)
        )

        cy = (
            self.rect.centery
            - int(camera.offset_y)
            + int(math.sin(self._bob) * 6)
        )

        # -----------------------------------------------------------
        # PULSE
        # -----------------------------------------------------------

        pulse = (
            math.sin(self._pulse) + 1
        ) / 2

        # -----------------------------------------------------------
        # OUTER MAGICAL GLOW
        # -----------------------------------------------------------

        glow_surface = pygame.Surface(
            (90, 90),
            pygame.SRCALPHA
        )

        glow_center = (45, 45)

        # Several soft glow rings
        for radius, alpha in [
            (34, 20),
            (29, 28),
            (24, 38),
            (20, 48),
        ]:

            pygame.draw.circle(
                glow_surface,
                (150, 90, 255, alpha),
                glow_center,
                radius
            )

        surface.blit(
            glow_surface,
            (
                cx - 45,
                cy - 45
            )
        )

        # -----------------------------------------------------------
        # ROTATING DIAMOND
        # -----------------------------------------------------------

        angle = math.radians(
            self._angle
        )

        points = []

        # Four rotating points
        for i in range(4):

            a = angle + (
                i * math.pi / 2
            )

            radius = 18

            px = (
                cx
                + math.cos(a) * radius
            )

            py = (
                cy
                + math.sin(a) * radius
            )

            points.append(
                (int(px), int(py))
            )

        # Outer crystal
        pygame.draw.polygon(
            surface,
            (130, 70, 255),
            points
        )

        # Inner crystal
        inner_points = []

        for i in range(4):

            a = angle + (
                i * math.pi / 2
            )

            radius = 11

            px = (
                cx
                + math.cos(a) * radius
            )

            py = (
                cy
                + math.sin(a) * radius
            )

            inner_points.append(
                (int(px), int(py))
            )

        pygame.draw.polygon(
            surface,
            (205, 150, 255),
            inner_points
        )

        # Bright outline
        pygame.draw.polygon(
            surface,
            (240, 220, 255),
            points,
            2
        )

        # -----------------------------------------------------------
        # CENTER ENERGY
        # -----------------------------------------------------------

        center_radius = int(
            4 + pulse * 2
        )

        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (cx, cy),
            center_radius
        )

        # -----------------------------------------------------------
        # SMALL SPARKLES
        # -----------------------------------------------------------

        sparkle_distance = 27

        for i in range(4):

            a = (
                self._angle * 0.5
                + i * 90
            )

            rad = math.radians(a)

            sx = int(
                cx
                + math.cos(rad)
                * sparkle_distance
            )

            sy = int(
                cy
                + math.sin(rad)
                * sparkle_distance
            )

            pygame.draw.circle(
                surface,
                (220, 190, 255),
                (sx, sy),
                2
            )