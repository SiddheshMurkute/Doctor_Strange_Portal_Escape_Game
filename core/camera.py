# core/camera.py
"""
Camera with dt-correct exponential smoothing and look-ahead.

The follow target is:
    player_center
    + player_velocity * VELOCITY_AHEAD   (lead in direction of travel)
    + aim_direction   * AIM_AHEAD        (lean toward aim point)

Dynamic zoom hooks allow Reality Break / heavy hits to punch
the zoom in or out briefly.
"""

import math
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


VELOCITY_AHEAD   = 0.30    # pixels of lead per px/s of velocity
AIM_AHEAD        = 55      # pixels of lean toward aim direction
SMOOTH_SPEED     = 8.0     # exponential follow speed (higher = tighter)
ZOOM_SMOOTH      = 6.0     # zoom recovery speed


class Camera:

    def __init__(self, world_w: int, world_h: int):
        self.world_w   = world_w
        self.world_h   = world_h
        self.offset_x  = 0.0
        self.offset_y  = 0.0

        # Shake offset (set externally by ScreenShake)
        self.shake_x   = 0
        self.shake_y   = 0

        # Look-ahead inputs (set externally each frame)
        self._vel_x:    float = 0.0
        self._vel_y:    float = 0.0
        self._aim_dx:   float = 0.0   # normalised aim direction x
        self._aim_dy:   float = 0.0   # normalised aim direction y

        # Zoom
        self._zoom:        float = 1.0
        self._zoom_target: float = 1.0

    # ------------------------------------------------------------------
    # PUBLIC SETTERS
    # ------------------------------------------------------------------

    def set_lookahead(self, vel_x: float, vel_y: float,
                      aim_dx: float = 0.0, aim_dy: float = 0.0) -> None:
        """Supply player velocity and aim direction each frame."""
        self._vel_x  = vel_x
        self._vel_y  = vel_y
        self._aim_dx = aim_dx
        self._aim_dy = aim_dy

    def zoom_punch(self, target: float, duration: float = 0.0) -> None:
        """
        Set a temporary zoom target (e.g. 0.95 for slight out, 1.08 for in).
        Camera will smoothly return to 1.0 afterward via ZOOM_SMOOTH.
        """
        self._zoom_target = target

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, target_rect: pygame.Rect, dt: float = 0.016) -> None:
        """
        dt-correct exponential follow.
            factor = 1 - exp(-SMOOTH_SPEED * dt)
        Avoids frame-rate dependence of the old 0.12 multiplier.
        """
        factor = 1.0 - math.exp(-SMOOTH_SPEED * dt)

        # Desired camera origin (top-left) to centre on player
        cx = target_rect.centerx - SCREEN_WIDTH  // 2
        cy = target_rect.centery - SCREEN_HEIGHT // 2

        # Look-ahead offset
        cx += self._vel_x * VELOCITY_AHEAD + self._aim_dx * AIM_AHEAD
        cy += self._vel_y * VELOCITY_AHEAD + self._aim_dy * AIM_AHEAD

        # Smooth
        self.offset_x += (cx - self.offset_x) * factor
        self.offset_y += (cy - self.offset_y) * factor

        # Clamp to world bounds
        self.offset_x = max(0.0, min(self.offset_x, self.world_w - SCREEN_WIDTH))
        self.offset_y = max(0.0, min(self.offset_y, self.world_h - SCREEN_HEIGHT))

        # Smooth zoom recovery
        zoom_factor = 1.0 - math.exp(-ZOOM_SMOOTH * dt)
        self._zoom += (self._zoom_target - self._zoom) * zoom_factor
        # Return target to 1.0
        self._zoom_target += (1.0 - self._zoom_target) * zoom_factor * 0.5

    # ------------------------------------------------------------------
    # APPLY
    # ------------------------------------------------------------------

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(
            int(rect.x - self.offset_x) + self.shake_x,
            int(rect.y - self.offset_y) + self.shake_y,
            rect.width,
            rect.height,
        )

    def apply_point(self, pos) -> tuple:
        return (
            int(pos[0] - self.offset_x) + self.shake_x,
            int(pos[1] - self.offset_y) + self.shake_y,
        )

    def world_pos(self, screen_pos) -> tuple:
        return (
            screen_pos[0] + int(self.offset_x),
            screen_pos[1] + int(self.offset_y),
        )

    def set_shake(self, sx: int, sy: int) -> None:
        self.shake_x = sx
        self.shake_y = sy

    def clear_shake(self) -> None:
        self.shake_x = 0
        self.shake_y = 0

    @property
    def zoom(self) -> float:
        return self._zoom
