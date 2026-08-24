# levels/stage3_titan.py
"""Stage 3 — Titan: alien cosmic battlefield with portal clues."""
import pygame
import math
import random
from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG


class Stage3Titan(BaseLevel):
    def __init__(self, difficulty: str):
        super().__init__(3, difficulty)
        self._rocks = [(random.randint(0,1920), random.randint(0,1080),
                        random.randint(30,90), random.randint(20,50)) for _ in range(40)]
        self.setup()

    def setup(self):
        cfg = STAGE_CONFIG[3]
        ps = cfg["player_start"]
        ww, wh = self.world_w, self.world_h

        # Boundary
        self.walls = [
            pygame.Rect(0,    0,    ww,  50),
            pygame.Rect(0,    wh-50,ww,  50),
            pygame.Rect(0,    0,    50,  wh),
            pygame.Rect(ww-50,0,    50,  wh),
        ]
        # Rock formations
        rock_walls = [
            (80,  80,  200, 180), (340,80,  160, 200), (620,80,  180, 160),
            (900, 80,  200, 200), (1180,80, 180, 180), (1460,80, 220, 200),
            (1680,80, 200, 240),
            (80,  420, 180, 200), (340,400, 200, 220), (620,400, 160, 200),
            (900, 420, 200, 200), (1180,400,180, 220), (1460,400,200, 200),
            (1680,400,200, 220),
            (80,  720, 200, 300), (380,720, 180, 280), (680,720, 180, 280),
            (980, 720, 200, 280), (1300,720,200, 280), (1600,720,280, 280),
            # Center large formation
            (780, 320, 160, 120),
        ]
        for bx,by,bw,bh in rock_walls:
            self.walls.append(pygame.Rect(bx, by, bw, bh))

        self.generate_portals(ps)
        self.generate_fragments(cfg["fragment_count"])

    def draw_background(self, surface: pygame.Surface):
        ox = int(self.camera.offset_x)
        oy = int(self.camera.offset_y)
        sw, sh = 1280, 720
        t = pygame.time.get_ticks() / 1000

        # Sky — alien orange/purple gradient
        for y in range(sh):
            frac = y / sh
            r = int(60  + frac * 90)
            g = int(20  + frac * 40)
            b = int(80  + frac * 60)
            pygame.draw.line(surface, (r, g, b), (0, y), (sw, y))

        # Alien ground
        pygame.draw.rect(surface, (70, 45, 35), (0, sh//2, sw, sh))
        for i in range(0, sw, 60):
            pygame.draw.line(surface, (85, 55, 40), (i, sh//2), (i+30, sh), 2)

        # Background rock formations
        for rx, ry, rw, rh in self._rocks:
            sx2 = rx - ox; sy2 = ry - oy
            if -rw < sx2 < sw+rw and -rh < sy2 < sh+rh:
                col1 = (85, 55, 40)
                col2 = (100, 65, 50)
                pygame.draw.ellipse(surface, col1, (sx2, sy2, rw, rh))
                pygame.draw.ellipse(surface, col2, (sx2+4, sy2+4, rw-8, rh//2))

        # Cosmic sky objects
        for i in range(3):
            planet_x = (200 + i * 450) - ox % 200
            planet_y = 80 + i * 40 - oy % 80
            planet_r = 40 + i * 15
            col = [(120,80,200),(200,100,80),(80,160,200)][i]
            pygame.draw.circle(surface, col, (planet_x, planet_y), planet_r)
            # Ring
            pygame.draw.ellipse(surface, (*col, 120),
                                (planet_x-planet_r-10, planet_y-6, (planet_r+10)*2, 12), 3)

        # Dimensional fractures
        for i in range(4):
            fx = (i*400 + int(math.sin(t*0.4+i)*50)) % sw
            fy = int(sh*0.3 + i*80)
            col = (180, 80, 255)
            pygame.draw.line(surface, col, (fx, fy), (fx+40, fy+25), 2)
            pygame.draw.line(surface, col, (fx+40, fy+25), (fx+20, fy+55), 2)
            # Glow
            gs = pygame.Surface((20, 60), pygame.SRCALPHA)
            pulse = int(math.sin(t*3+i)*40)
            gs.fill((150, 50, 255, max(0, min(255, 30+pulse))))
            surface.blit(gs, (fx+10, fy))

        # Cosmic dust clouds
        for i in range(5):
            dx = (i * 280) % sw
            dust = pygame.Surface((200, 100), pygame.SRCALPHA)
            dust.fill((100, 50, 150, 18))
            surface.blit(dust, (dx, sh//3 + i*40))
