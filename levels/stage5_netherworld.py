# levels/stage5_netherworld.py
"""Stage 5 — Netherworld/Hell: volcanic, final, most intense."""
import pygame
import math
import random
from levels.base_level import BaseLevel
from config.stages import STAGE_CONFIG


class Stage5Netherworld(BaseLevel):
    def __init__(self, difficulty: str):
        super().__init__(5, difficulty)
        self._lava_t = 0.0
        self._cracks = [(random.randint(0,1920), random.randint(0,1080),
                         random.randint(30,80), random.randint(60, 160)) for _ in range(20)]
        self.setup()

    def setup(self):
        cfg = STAGE_CONFIG[5]
        ps = cfg["player_start"]
        ww, wh = self.world_w, self.world_h

        self.walls = [
            pygame.Rect(0,    0,    ww,  50),
            pygame.Rect(0,    wh-50,ww,  50),
            pygame.Rect(0,    0,    50,  wh),
            pygame.Rect(ww-50,0,    50,  wh),
        ]
        # Volcanic rockscape
        rock_walls = [
            (80,  80,  200, 200), (360, 80,  160, 180), (580, 80,  180, 200),
            (840, 80,  200, 200), (1100,80,  180, 200), (1360,80,  200, 200),
            (1620,80,  260, 200),
            (80,  440, 200, 200), (360, 420, 160, 220), (580, 440, 180, 200),
            (840, 440, 200, 220), (1100,440, 180, 200), (1360,440, 200, 220),
            (1620,440, 260, 200),
            (80,  760, 200, 300), (380, 760, 160, 280), (660, 760, 180, 280),
            (940, 760, 200, 280), (1220,760, 180, 280), (1520,760, 200, 280),
            (1720,760, 180, 280),
            # Center lava pillars
            (700, 280, 100, 80), (1050,300, 100, 80), (1300,280, 80, 100),
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
        self._lava_t = t

        # Dark infernal sky
        for y in range(sh):
            frac = y / sh
            r = int(30  + frac * 80)
            g = int(5   + frac * 20)
            b = int(5   + frac * 10)
            pygame.draw.line(surface, (r, g, b), (0, y), (sw, y))

        # Black volcanic ground
        pygame.draw.rect(surface, (20, 10, 5), (0, sh//2, sw, sh))

        # Lava cracks (glowing orange lines)
        for i in range(12):
            lx = (i * 120) % sw
            ly = sh//2 + (i*35) % (sh//2)
            glow_alpha = int(100 + math.sin(t*2+i)*60)
            col = (255, max(0, 80-i*5), 0)
            pygame.draw.line(surface, col, (lx, ly), (lx+40, ly+20), 3)
            pygame.draw.line(surface, col, (lx+40, ly+20), (lx+15, ly+50), 2)
            # Glow
            gs = pygame.Surface((50, 60), pygame.SRCALPHA)
            gs.fill((*col, max(0, glow_alpha//3)))
            surface.blit(gs, (lx-5, ly-5))

        # Lava pools
        for i in range(5):
            lx = (i * 250 + 80) % sw
            ly = sh//2 + 40 + i * 50
            lw = 140 + i * 20
            lh = 40
            pulse = int(math.sin(t*3+i)*8)
            lava_col = (200+pulse, 80+pulse//2, 0)
            pygame.draw.ellipse(surface, lava_col, (lx, ly, lw, lh))
            # Shimmer
            pygame.draw.ellipse(surface, (255, 180, 50), (lx+10, ly+5, lw-20, lh-10), 2)

        # Ground cracks with glow
        for cx2, cy2, cw, ch in self._cracks:
            sx2 = cx2 - ox; sy2 = cy2 - oy
            if -cw < sx2 < sw+cw and -ch < sy2 < sh+ch:
                glow = int(80 + math.sin(t*4+cx2)*50)
                pygame.draw.line(surface, (255, glow, 0), (sx2, sy2), (sx2+cw, sy2+ch), 2)
                glow_s = pygame.Surface((cw+10, ch+10), pygame.SRCALPHA)
                glow_s.fill((255, glow//2, 0, 30))
                surface.blit(glow_s, (sx2-5, sy2-5))

        # Fire columns
        for i in range(6):
            fx = (i * 200 + 100) % sw
            fy = sh//2 - 50
            for flame in range(5):
                frad = 8 - flame * 1.5
                foff = int(math.sin(t*4+i+flame)*10)
                col = [(255,50,0),(255,100,0),(255,150,20),(255,200,50),(255,240,100)][flame]
                pygame.draw.circle(surface, col, (fx+foff, fy-flame*15), max(1,int(frad)))

        # Dark atmospheric smoke
        for i in range(8):
            sy3 = (int(t*40) + i*90) % sh
            smoke = pygame.Surface((200, 60), pygame.SRCALPHA)
            smoke.fill((15, 5, 5, 35))
            surface.blit(smoke, ((i*190) % sw - 100, sy3))

        # Dimensional fractures — red/orange
        for i in range(3):
            fx2 = (i*450+int(math.sin(t*0.6+i)*60)) % sw
            fy2 = sh//4 + i*100
            pygame.draw.line(surface, (255, 50, 0), (fx2, fy2), (fx2+50, fy2+30), 3)
            pygame.draw.line(surface, (255, 150, 20), (fx2+50, fy2+30), (fx2+20, fy2+70), 2)

    def update_instability(self, time_remaining: float, total_time: float, camera, screen_shake):
        """Increase intensity as time runs out."""
        if total_time <= 0:
            return
        frac = 1.0 - max(0, time_remaining / total_time)
        if frac > 0.5:
            # Increase shake
            intensity = int((frac - 0.5) * 8)
            if random.random() < 0.1:
                screen_shake.trigger(intensity, 0.3)
