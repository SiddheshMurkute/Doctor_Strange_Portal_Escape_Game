# objects/fragment.py
"""Dimensional fragment collectible — bonus points."""
import pygame
import math
import random

FRAGMENT_SIZE = 24

class Fragment:
    def __init__(self, x, y, value=150):
        self.rect    = pygame.Rect(x - FRAGMENT_SIZE//2, y - FRAGMENT_SIZE//2,
                                   FRAGMENT_SIZE, FRAGMENT_SIZE)
        self.value   = value
        self.collected = False
        self._angle  = 0.0
        self._bob    = 0.0

    def update(self, dt):
        self._angle = (self._angle + dt * 120) % 360
        self._bob   = (self._bob   + dt * 3.0) % (2*math.pi)

    def check_collect(self, player_rect) -> bool:
        if not self.collected and self.rect.colliderect(player_rect):
            self.collected = True
            return True
        return False

    def draw(self, surface, camera):
        if self.collected:
            return
        cx = self.rect.centerx - int(camera.offset_x)
        cy = self.rect.centery - int(camera.offset_y) + int(math.sin(self._bob)*5)

        # Diamond shape
        pts = [
            (cx,          cy - 14),
            (cx + 10,     cy),
            (cx,          cy + 14),
            (cx - 10,     cy),
        ]
        colors = [(255, 220, 50), (255, 150, 0), (200, 255, 100), (255, 200, 0)]
        col = colors[int(self._angle / 90) % 4]
        pygame.draw.polygon(surface, col, pts)
        pygame.draw.polygon(surface, (255, 255, 200), pts, 2)
        # Glow dot center
        pygame.draw.circle(surface, (255,255,200), (cx, cy), 4)
