# core/collision.py
import pygame
import math

def collide_rects(r1: pygame.Rect, walls: list) -> pygame.Vector2:
    """Return MTV (minimum translation vector) to push r1 out of all walls."""
    offset = pygame.Vector2(0, 0)
    for wall in walls:
        if r1.colliderect(wall):
            dx1 = wall.right - r1.left
            dx2 = r1.right  - wall.left
            dy1 = wall.bottom - r1.top
            dy2 = r1.bottom  - wall.top
            dx = dx1 if dx1 < dx2 else -dx2
            dy = dy1 if dy1 < dy2 else -dy2
            if abs(dx) < abs(dy):
                offset.x += dx
            else:
                offset.y += dy
    return offset

def distance(a, b) -> float:
    return math.hypot(a[0]-b[0], a[1]-b[1])

def circle_rect_collide(cx, cy, radius, rect: pygame.Rect) -> bool:
    nearest_x = max(rect.left, min(cx, rect.right))
    nearest_y = max(rect.top,  min(cy, rect.bottom))
    return distance((cx, cy), (nearest_x, nearest_y)) <= radius
