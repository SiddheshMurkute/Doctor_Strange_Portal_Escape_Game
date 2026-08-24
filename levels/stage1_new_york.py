# levels/stage1_new_york.py
"""Stage 1 — New York City: dark urban night, mystical invasion."""
import pygame
import math
import random
from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG


def _draw_building(surface, x, y, w, h, col_base, col_window):
    pygame.draw.rect(surface, col_base, (x, y, w, h))
    pygame.draw.rect(surface, (col_base[0]+20, col_base[1]+20, col_base[2]+20), (x, y, w, h), 2)
    # Windows
    for wy in range(y+10, y+h-20, 22):
        for wx in range(x+8, x+w-8, 18):
            if random.random() < 0.65:
                pygame.draw.rect(surface, col_window, (wx, wy, 10, 14))


class Stage1NewYork(BaseLevel):
    def __init__(self, difficulty: str):
        super().__init__(1, difficulty)
        self._bg: pygame.Surface | None = None
        self._bg_size = (0,0)
        self.setup()

    def setup(self):
        cfg = STAGE_CONFIG[1]
        ps = cfg["player_start"]

        # --- Walls: street layout ---
        ww, wh = self.world_w, self.world_h
        # Outer boundary walls
        self.walls = [
            pygame.Rect(0,       0,       ww, 40),      # top
            pygame.Rect(0,       wh-40,   ww, 40),      # bottom
            pygame.Rect(0,       0,       40, wh),      # left
            pygame.Rect(ww-40,   0,       40, wh),      # right
        ]
        # Interior urban blocks (buildings)
        blocks = [
            (80, 80,  260, 200),
            (400,80,  260, 200),
            (720,80,  260, 200),
            (1040,80, 260, 200),
            (1380,80, 260, 200),
            (1640,80, 220, 200),
            (80, 380, 240, 200),
            (400,380, 240, 200),
            (720,380, 240, 200),
            (1040,380,240, 200),
            (1380,380,220, 200),
            (1640,380,220, 200),
            (80, 700, 220, 280),
            (380,700, 220, 280),
            (700,700, 220, 280),
            (1040,700,220, 280),
            (1380,700,220, 280),
            (1640,700,220, 280),
        ]
        for bx, by, bw, bh in blocks:
            self.walls.append(pygame.Rect(bx, by, bw, bh))

        # Portals + fragments
        self.generate_portals(ps)
        self.generate_fragments(cfg["fragment_count"])

    def draw_background(self, surface: pygame.Surface):
        ox = int(self.camera.offset_x)
        oy = int(self.camera.offset_y)
        sw, sh = 1280, 720

        # Sky gradient
        for y in range(sh):
            t = y / sh
            r = int(8  + t * 20)
            g = int(5  + t * 15)
            b = int(25 + t * 40)
            pygame.draw.line(surface, (r, g, b), (0, y), (sw, y))

        # Ground (street)
        pygame.draw.rect(surface, (45, 40, 50), (0, 0, sw, sh))
        # Road markings
        road_y = sh // 2 - oy % 80
        for ry in range(road_y, sh, 80):
            pygame.draw.line(surface, (80, 75, 65), (0, ry), (sw, ry), 2)

        # Buildings (parallax-ish, drawn at camera offset)
        rng = random.Random(42)
        building_colors = [(35,30,55),(40,35,60),(28,25,48),(50,40,65)]
        window_colors   = [(200,180,80),(80,180,230),(255,220,100),(180,200,255)]
        for i in range(30):
            bx = (i * 130) % self.world_w - ox
            bw = rng.randint(80, 160)
            bh = rng.randint(120, 320)
            by = -bh + rng.randint(60, 160) - oy % 30
            bc = building_colors[i % len(building_colors)]
            wc = window_colors[i % len(window_colors)]
            if -bw < bx < sw + bw:
                _draw_building(surface, bx, by, bw, bh, bc, wc)

        # Mystical dimensional cracks
        t = pygame.time.get_ticks() / 1000
        for idx in range(5):
            x1 = (idx * 280 + int(math.sin(t*0.5+idx)*30)) % sw
            y1 = int(sh * 0.2 + idx * 40)
            pts = [(x1, y1), (x1+30, y1+15), (x1+10, y1+35), (x1+45, y1+55)]
            for k in range(len(pts)-1):
                alpha = 120 + int(math.sin(t*2+idx)*60)
                pygame.draw.line(surface, (100, 60, 255), pts[k], pts[k+1],
                                 2 + (idx % 2))

        # Purple/blue ambient fog patches
        for i in range(6):
            fx = (i * 220) % sw
            fy = sh // 2 + (i * 30) % 200
            fog = pygame.Surface((200, 120), pygame.SRCALPHA)
            fog.fill((60, 20, 120, 25))
            surface.blit(fog, (fx, fy))
