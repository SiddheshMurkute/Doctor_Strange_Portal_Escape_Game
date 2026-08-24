# ui/stage_intro.py
import pygame
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from config.stages import STAGE_CONFIG

STAGE_SUBTITLES = {
    1: "NEW YORK CITY",
    2: "SPACESHIP",
    3: "TITAN",
    4: "SNOW MOUNTAIN",
    5: "NETHERWORLD",
}

STAGE_COLORS = {
    1: (255, 160, 0),
    2: (0,  200, 255),
    3: (180, 80, 255),
    4: (150, 220, 255),
    5: (255, 80,  20),
}

class StageIntro:
    def __init__(self, font_large, font_med, font_small, stage: int, timer: int):
        self.fl = font_large
        self.fm = font_med
        self.fs = font_small
        self.stage   = stage
        self.timer   = timer
        self._t      = 0.0
        self.col     = STAGE_COLORS.get(stage, (255,180,0))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return 'start'
        return None

    def update(self, dt):
        self._t += dt

    def draw(self, surface):
        t      = self._t
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        col    = self.col

        # Background
        surface.fill((8, 4, 18))
        for y in range(sh):
            frac = y/sh
            r = int(col[0]*frac*0.3)
            g = int(col[1]*frac*0.2)
            b = int(col[2]*frac*0.25 + 18*frac)
            pygame.draw.line(surface, (r,g,b), (0,y),(sw,y))

        # Animated ring
        cx, cy = sw//2, sh//2 - 40
        ring_r = int(80 + math.sin(t*1.5)*6)
        for i in range(3):
            r2 = ring_r - i*15
            a  = t*50*(1 if i%2==0 else -1)
            rs = pygame.Surface((r2*2+4, r2*2+4), pygame.SRCALPHA)
            pygame.draw.ellipse(rs, (*col, 200-i*50), (2,2,r2*2,r2*2), 3)
            rot = pygame.transform.rotate(rs, a)
            rw, rh = rot.get_size()
            surface.blit(rot, (cx-rw//2, cy-rh//2), special_flags=pygame.BLEND_RGBA_ADD)

        # Stage label
        stage_nh = int(sh * 0.18)
        stitle = self.fl.render(f"STAGE {self.stage}", True, col)
        surface.blit(stitle, (sw//2 - stitle.get_width()//2, stage_nh))

        subtitle = self.fl.render(STAGE_SUBTITLES.get(self.stage, ""), True, (255,255,255))
        surface.blit(subtitle, (sw//2 - subtitle.get_width()//2, stage_nh + stitle.get_height() + 4))

        # Mission
        mission = self.fm.render("MISSION: FIND AND ENTER THE CORRECT PORTAL", True, (200, 200, 200))
        surface.blit(mission, (sw//2 - mission.get_width()//2, sh//2 + 40))

        # Timer
        timer_txt = self.fm.render(f"TIME LIMIT: {self.timer} SECONDS", True, (255, 200, 80))
        surface.blit(timer_txt, (sw//2 - timer_txt.get_width()//2, sh//2 + 90))

        # Press enter
        blink = int(t * 2) % 2 == 0
        if blink:
            press = self.fs.render("PRESS ENTER TO BEGIN", True, (180, 180, 180))
            surface.blit(press, (sw//2 - press.get_width()//2, sh - 80))
