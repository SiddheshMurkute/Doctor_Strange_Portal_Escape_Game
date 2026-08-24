# levels/stage2_space.py
"""Stage 2 — Spaceship interior with space visible through windows."""
import pygame
import math
import random
from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG


class Stage2Space(BaseLevel):
    def __init__(self, difficulty: str):
        super().__init__(2, difficulty)
        self._stars = [(random.randint(0,1920), random.randint(0,1080),
                        random.randint(1,3)) for _ in range(300)]
        self.setup()

    def setup(self):
        cfg = STAGE_CONFIG[2]
        ps = cfg["player_start"]
        ww, wh = self.world_w, self.world_h

        # Boundary
        self.walls = [
            pygame.Rect(0,    0,    ww,  50),
            pygame.Rect(0,    wh-50,ww,  50),
            pygame.Rect(0,    0,    50,  wh),
            pygame.Rect(ww-50,0,    50,  wh),
        ]
        # Spaceship interior — corridors with walls/machinery
        ship_blocks = [
            # Outer hull sections
            (80,  80,  220, 180),
            (380, 80,  220, 180),
            (700, 80,  220, 180),
            (1020,80,  220, 180),
            (1360,80,  220, 180),
            (1620,80,  260, 180),
            (80,  400, 220, 180),
            (380, 400, 220, 180),
            (700, 400, 220, 180),
            (1020,400, 220, 180),
            (1360,400, 220, 180),
            (1620,400, 260, 180),
            (80,  720, 240, 280),
            (400, 720, 200, 280),
            (720, 720, 200, 280),
            (1040,720, 200, 280),
            (1360,720, 240, 280),
            (1620,720, 260, 280),
            # Center obstacles (corridor pillars)
            (600, 320, 80, 80),
            (900, 320, 80, 80),
            (1200,320, 80, 80),
        ]
        for bx,by,bw,bh in ship_blocks:
            self.walls.append(pygame.Rect(bx, by, bw, bh))

        self.generate_portals(ps)
        self.generate_fragments(cfg["fragment_count"])

    def draw_background(self, surface: pygame.Surface):
        ox = int(self.camera.offset_x)
        oy = int(self.camera.offset_y)
        sw, sh = 1280, 720

        # Space background (outside viewports)
        surface.fill((5, 5, 20))

        # Stars
        for sx, sy, sr in self._stars:
            screen_x = sx - ox
            screen_y = sy - oy
            if 0 < screen_x < sw and 0 < screen_y < sh:
                pygame.draw.circle(surface, (200,210,255), (screen_x, screen_y), sr)

        # Window portholes (circular space-views)
        t = pygame.time.get_ticks() / 1000
        for i, (wx, wy, wr) in enumerate([
            (200, 150, 70), (600, 100, 60), (1080, 150, 70),
            (300, 500, 65), (900, 550, 60), (1400, 200, 70),
        ]):
            sx2 = wx - ox; sy2 = wy - oy
            if -wr < sx2 < sw+wr and -wr < sy2 < sh+wr:
                pygame.draw.circle(surface, (8, 12, 35), (sx2, sy2), wr)
                # Planet glow
                col = [(70,50,120),(40,80,140),(90,40,100)][i%3]
                pygame.draw.circle(surface, col, (sx2+15, sy2+10), wr-20)
                pygame.draw.circle(surface, (0,0,0), (sx2, sy2), wr, 4)

        # Metallic floor
        floor_y = sh - 80 - oy % 40
        for fy in range(floor_y, sh, 40):
            pygame.draw.line(surface, (50, 55, 70), (0, fy), (sw, fy), 1)
        for fx in range(0, sw, 60):
            pygame.draw.line(surface, (50, 55, 70), (fx, 0), (fx, sh), 1)

        # Metal panels on ceiling and walls
        for i in range(8):
            px = (i * 180) % sw
            pygame.draw.rect(surface, (45,50,65), (px, 0, 150, 25))
            pygame.draw.rect(surface, (80,90,110), (px, 0, 150, 25), 2)

        # Plasma conduits (glowing lines)
        for i in range(3):
            lx = 200 + i * 350 - ox % 100
            col = [(0,200,255),(100,50,255),(0,255,180)][i]
            pulse = int(math.sin(t*3+i)*30)
            pygame.draw.line(surface, (*col, 180), (lx, 50), (lx, sh-50), 3)
            # Glow
            gs = pygame.Surface((20, sh), pygame.SRCALPHA)
            gs.fill((*col, max(0, min(255, 15+pulse))))
            surface.blit(gs, (lx-10, 0))

        # Electric sparks
        for i in range(4):
            sx3 = (i * 320 + int(t * 80)) % sw
            sy3 = random.randint(100, sh-100)
            if random.random() < 0.1:
                pygame.draw.line(surface, (100, 200, 255),
                                 (sx3, sy3), (sx3+random.randint(-20,20), sy3+random.randint(-20,20)), 1)
