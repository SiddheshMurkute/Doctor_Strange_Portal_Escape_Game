# levels/stage4_snow.py
"""Stage 4 — Snow Mountain: icy, isolated, dangerous."""
import pygame
import math
import random
from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG


class Stage4Snow(BaseLevel):
    def __init__(self, difficulty: str):
        super().__init__(4, difficulty)
        self.setup()

    def setup(self):
        cfg = STAGE_CONFIG[4]
        ps = cfg["player_start"]
        ww, wh = self.world_w, self.world_h

        self.walls = [
            pygame.Rect(0,    0,    ww,  50),
            pygame.Rect(0,    wh-50,ww,  50),
            pygame.Rect(0,    0,    50,  wh),
            pygame.Rect(ww-50,0,    50,  wh),
        ]
        # Snow mountain terrain — cliffs and rock outcrops
        mountain_walls = [
            (80,  80,  180, 240),  (320, 80,  140, 200), (540, 80,  160, 200),
            (780, 80,  180, 240),  (1040,80,  160, 200), (1280,80,  160, 220),
            (1540,80,  200, 240),  (1700,80,  180, 200),
            (80,  440, 160, 200),  (320, 420, 140, 220), (540, 440, 160, 200),
            (780, 440, 180, 220),  (1040,440, 160, 200), (1280,440, 160, 220),
            (1540,440, 200, 200),  (1700,440, 180, 220),
            (80,  740, 180, 300),  (360, 740, 160, 280), (640, 740, 180, 280),
            (920, 740, 180, 280),  (1200,740, 180, 280), (1500,740, 200, 280),
            (1720,740, 180, 280),
            # Ice pillar obstacles
            (650, 280, 60, 100),   (1000,280, 60, 100),
            (650, 500, 60, 60),    (1350,380, 60, 100),
        ]
        for bx,by,bw,bh in mountain_walls:
            self.walls.append(pygame.Rect(bx, by, bw, bh))

        self.generate_portals(ps)
        self.generate_fragments(cfg["fragment_count"])

    def draw_background(self, surface: pygame.Surface):
        ox = int(self.camera.offset_x)
        oy = int(self.camera.offset_y)
        sw, sh = 1280, 720
        t = pygame.time.get_ticks() / 1000

        # Sky — cold grey-blue gradient
        for y in range(sh):
            frac = y / sh
            r = int(80  + frac * 40)
            g = int(90  + frac * 50)
            b = int(130 + frac * 70)
            pygame.draw.line(surface, (r, g, b), (0, y), (sw, y))

        # Snow ground
        pygame.draw.rect(surface, (200, 210, 230), (0, sh//2, sw, sh))
        # Snow texture lines
        for i in range(0, sw, 80):
            pygame.draw.line(surface, (185, 195, 220), (i, sh//2), (i+60, sh//2+10), 2)

        # Mountain silhouettes (background)
        mountain_pts = []
        rng = random.Random(99)
        x = -100
        while x < sw + 100:
            peak_h = rng.randint(100, 350)
            mountain_pts += [(x, sh-100), (x+rng.randint(80,160), sh-100-peak_h),
                             (x+rng.randint(120,200), sh-100)]
            x += rng.randint(150, 250)
        if len(mountain_pts) >= 3:
            pygame.draw.polygon(surface, (140, 155, 185), mountain_pts)
            pygame.draw.polygon(surface, (190, 200, 220), mountain_pts, 2)

        # Ice crystals
        for i in range(8):
            cx2 = (i * 180 + 60) % sw
            cy2 = sh//2 - 5
            for j in range(5):
                a = math.pi/2 + j * math.pi/2.5
                ex2 = cx2 + int(math.cos(a) * 20)
                ey2 = cy2 + int(math.sin(a) * 20)
                pygame.draw.line(surface, (180, 220, 255), (cx2, cy2), (ex2, ey2), 2)

        # Fog patches
        for i in range(10):
            fx = (i * 140) % sw
            fy = sh//3 + i*20
            fog = pygame.Surface((300, 80), pygame.SRCALPHA)
            fog.fill((220, 230, 250, 25))
            surface.blit(fog, (fx - 150, fy))

        # Wind streaks
        for i in range(15):
            wx2 = (int(t*200) + i*90) % (sw+200) - 100
            wy2 = i * 50
            wlen = random.Random(i*7).randint(40, 120)
            pygame.draw.line(surface, (200, 220, 255), (wx2, wy2), (wx2+wlen, wy2+2), 1)

        # Mystical blue glow patches
        mx = int(math.sin(t*0.5) * 100) + sw//2
        my = sh//3
        glow = pygame.Surface((300, 150), pygame.SRCALPHA)
        glow.fill((80, 120, 255, 20))
        surface.blit(glow, (mx-150, my-75))
