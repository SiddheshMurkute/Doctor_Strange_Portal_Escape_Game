# core/camera.py
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    def __init__(self, world_w: int, world_h: int):
        self.world_w = world_w
        self.world_h = world_h
        self.offset_x = 0.0
        self.offset_y = 0.0
        # Shake
        self.shake_x = 0
        self.shake_y = 0

    def update(self, target_rect: pygame.Rect):
        # Smooth follow
        target_x = target_rect.centerx - SCREEN_WIDTH  // 2
        target_y = target_rect.centery - SCREEN_HEIGHT // 2
        self.offset_x += (target_x - self.offset_x) * 0.12
        self.offset_y += (target_y - self.offset_y) * 0.12
        # Clamp
        self.offset_x = max(0, min(self.offset_x, self.world_w - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y, self.world_h - SCREEN_HEIGHT))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(
            rect.x - int(self.offset_x) + self.shake_x,
            rect.y - int(self.offset_y) + self.shake_y,
            rect.width,
            rect.height,
        )

    def apply_point(self, pos) -> tuple:
        return (
            pos[0] - int(self.offset_x) + self.shake_x,
            pos[1] - int(self.offset_y) + self.shake_y,
        )

    def world_pos(self, screen_pos) -> tuple:
        return (
            screen_pos[0] + int(self.offset_x),
            screen_pos[1] + int(self.offset_y),
        )

    def set_shake(self, sx, sy):
        self.shake_x = sx
        self.shake_y = sy

    def clear_shake(self):
        self.shake_x = 0
        self.shake_y = 0
