# ui/hud.py
"""Stage-skinned HUD — consistent layout, skin changes per stage."""
import pygame
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# Per-stage HUD accent colors and skin names
STAGE_SKINS = {
    1: {'accent': (255, 160, 0),  'panel': (20, 15, 40, 190),  'name': 'NEW YORK'},
    2: {'accent': (0, 200, 255),  'panel': (5,  20, 50, 190),   'name': 'SPACESHIP'},
    3: {'accent': (180, 80, 255), 'panel': (25, 5,  40, 190),   'name': 'TITAN'},
    4: {'accent': (150, 220, 255),'panel': (10, 20, 50, 190),   'name': 'SNOW MTN'},
    5: {'accent': (255, 80, 20),  'panel': (40, 5,  5,  190),   'name': 'NETHERWORLD'},
}


class HUD:
    WHITE = (255, 255, 255)

    def __init__(self, font_med, font_small, stage: int):
        self.fm    = font_med
        self.fs    = font_small
        self.stage = stage
        self.skin  = STAGE_SKINS.get(stage, STAGE_SKINS[1])
        self._t    = 0.0
        self._warn_alpha = 0

    def update(self, dt):
        self._t += dt

    def _panel(self, surface, x, y, w, h):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(self.skin['panel'])
        pygame.draw.rect(s, (*self.skin['accent'], 200), (0, 0, w, h), 2, border_radius=6)
        surface.blit(s, (x, y))

    def draw(self, surface, hp, max_hp, score, time_left, max_time, stage, objective,
             attack_cooldown_pct=0.0, fragment_count=0):
        t = self._t
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        accent = self.skin['accent']
        skin_name = self.skin['name']

        # --- TOP BAR ---
        self._panel(surface, 0, 0, sw, 44)
        # Stage label
        sl = self.fm.render(f"STAGE {stage}  —  {skin_name}", True, accent)
        surface.blit(sl, (16, 12))

        # Timer
        mins = int(time_left) // 60
        secs = int(time_left) % 60
        low_time = time_left <= 10
        pulsing = low_time and int(t * 4) % 2 == 0
        timer_col = (255, 50, 50) if low_time else self.WHITE
        timer_str = f"TIME  {mins:02d}:{secs:02d}"
        # Warning pulse
        if low_time:
            warn = pygame.Surface((200, 40), pygame.SRCALPHA)
            alpha = int(60 + math.sin(t*6)*50)
            warn.fill((255, 0, 0, alpha if not pulsing else 0))
            surface.blit(warn, (sw//2 - 100, 2))
        timer_t = self.fm.render(timer_str, True, timer_col)
        surface.blit(timer_t, (sw//2 - timer_t.get_width()//2, 12))

        # Score
        score_t = self.fs.render(f"SCORE  {score:06d}", True, (220, 200, 100))
        surface.blit(score_t, (sw - score_t.get_width() - 16, 14))

        # --- HEALTH BAR (bottom-left) ---
        hpanel_w, hpanel_h = 260, 46
        self._panel(surface, 10, sh - hpanel_h - 10, hpanel_w, hpanel_h)
        hp_label = self.fs.render(f"HP  {hp} / {max_hp}", True, self.WHITE)
        surface.blit(hp_label, (20, sh - hpanel_h - 6))
        # Bar
        bx, by, bw, bh = 20, sh - 26, hpanel_w - 20, 12
        pygame.draw.rect(surface, (60, 15, 15), (bx, by, bw, bh), border_radius=5)
        fill = int(bw * max(0, hp) / max_hp)
        hp_col = (80, 220, 80) if hp > max_hp*0.5 else (220, 180, 0) if hp > max_hp*0.25 else (220, 40, 40)
        pygame.draw.rect(surface, hp_col, (bx, by, fill, bh), border_radius=5)

        # --- OBJECTIVE (bottom-right) ---
        obj_str = objective or "FIND THE CORRECT PORTAL"
        obj_w   = max(280, self.fs.size(obj_str)[0] + 30)
        self._panel(surface, sw - obj_w - 10, sh - 56, obj_w, 46)
        ot = self.fs.render("OBJECTIVE:", True, accent)
        ov = self.fs.render(obj_str, True, self.WHITE)
        surface.blit(ot, (sw - obj_w, sh - 52))
        surface.blit(ov, (sw - obj_w, sh - 32))

        # --- ATTACK COOLDOWN indicator (small arc near health) ---
        if attack_cooldown_pct > 0:
            pygame.draw.arc(surface, (255,150,0),
                            (280, sh - 46, 36, 36),
                            math.pi/2, math.pi/2 + (1-attack_cooldown_pct)*2*math.pi, 4)

        # --- Fragment count ---
        if fragment_count > 0:
            ft = self.fs.render(f"◆ ×{fragment_count}", True, (255, 220, 50))
            surface.blit(ft, (sw//2 - ft.get_width()//2, sh - 40))

        # --- LOW TIME full-screen warning ---
        if time_left <= 10:
            warn2 = pygame.Surface((sw, sh), pygame.SRCALPHA)
            alpha2 = int(25 + math.sin(t*5)*20)
            warn2.fill((255, 0, 0, alpha2))
            surface.blit(warn2, (0, 0))
            warn_t = self.fm.render("TIME IS RUNNING OUT!", True, (255,80,80))
            surface.blit(warn_t, (sw//2 - warn_t.get_width()//2, sh//2 - 30))
