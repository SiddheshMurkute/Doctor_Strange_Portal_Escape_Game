# ui/hud.py
"""Stage-skinned HUD — Momentum bar, Reality Break gem, compass pulse."""
import pygame
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.momentum import (
    TIER_FOCUSED, TIER_ASCENDANT, TIER_SORCERER_SUPREME, MAX_MOMENTUM
)

# Per-stage HUD accent colors and skin names
STAGE_SKINS = {
    1: {'accent': (255, 160, 0),  'panel': (20, 15, 40, 190),  'name': 'NEW YORK'},
    2: {'accent': (0, 200, 255),  'panel': (5,  20, 50, 190),   'name': 'SPACESHIP'},
    3: {'accent': (180, 80, 255), 'panel': (25, 5,  40, 190),   'name': 'TITAN'},
    4: {'accent': (150, 220, 255),'panel': (10, 20, 50, 190),   'name': 'SNOW MTN'},
    5: {'accent': (255, 80, 20),  'panel': (40, 5,  5,  190),   'name': 'NETHERWORLD'},
}

TIER_COLORS = {
    "NONE":             (80,  80,  80),
    "FOCUSED":          (255, 200, 50),
    "ASCENDANT":        (120, 60,  255),
    "SORCERER_SUPREME": (0,   220, 255),
}


class HUD:
    WHITE = (255, 255, 255)

    def __init__(self, font_med, font_small, stage: int):
        self.fm    = font_med
        self.fs    = font_small
        self.stage = stage
        self.skin  = STAGE_SKINS.get(stage, STAGE_SKINS[1])
        self._t    = 0.0

    def update(self, dt):
        self._t += dt

    def _panel(self, surface, x, y, w, h):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(self.skin['panel'])
        pygame.draw.rect(s, (*self.skin['accent'], 200), (0, 0, w, h), 2, border_radius=6)
        surface.blit(s, (x, y))

    # ------------------------------------------------------------------
    # MAIN DRAW
    # ------------------------------------------------------------------

    def draw(self, surface, hp, max_hp, score, time_left, max_time, stage, objective,
             attack_cooldown_pct=0.0, fragment_count=0,
             momentum=None, dash_cooldown_pct=0.0):
        """
        Draws the full HUD.
        momentum: core.momentum.Momentum instance (optional — skips bar if None)
        """
        t  = self._t
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        accent    = self.skin['accent']
        skin_name = self.skin['name']

        # --- TOP BAR ---
        self._panel(surface, 0, 0, sw, 44)
        # Stage label
        sl = self.fm.render(f"STAGE {stage}  —  {skin_name}", True, accent)
        surface.blit(sl, (16, 12))

        # Timer
        mins = int(time_left) // 60
        secs = int(time_left) % 60
        low_time  = time_left <= 10
        timer_col = (255, 50, 50) if low_time else self.WHITE
        timer_str = f"TIME  {mins:02d}:{secs:02d}"
        # Warning pulse background
        if low_time:
            alpha = int(50 + math.sin(t * 6) * 40)
            warn  = pygame.Surface((200, 40), pygame.SRCALPHA)
            warn.fill((255, 0, 0, max(0, alpha)))
            surface.blit(warn, (sw // 2 - 100, 2))
        timer_t = self.fm.render(timer_str, True, timer_col)
        surface.blit(timer_t, (sw // 2 - timer_t.get_width() // 2, 12))

        # Score
        score_t = self.fs.render(f"SCORE  {score:06d}", True, (220, 200, 100))
        surface.blit(score_t, (sw - score_t.get_width() - 16, 14))

        # --- HEALTH BAR (bottom-left) ---
        hpanel_w, hpanel_h = 270, 48
        self._panel(surface, 10, sh - hpanel_h - 10, hpanel_w, hpanel_h)
        hp_label = self.fs.render(f"HP  {hp} / {max_hp}", True, self.WHITE)
        surface.blit(hp_label, (20, sh - hpanel_h - 4))
        bx, by, bw, bh = 20, sh - 24, hpanel_w - 20, 10
        pygame.draw.rect(surface, (60, 15, 15), (bx, by, bw, bh), border_radius=4)
        fill    = int(bw * max(0, hp) / max(1, max_hp))
        hp_col  = (80, 220, 80) if hp > max_hp * 0.5 else (220, 180, 0) if hp > max_hp * 0.25 else (220, 40, 40)
        pygame.draw.rect(surface, hp_col, (bx, by, fill, bh), border_radius=4)

        # --- MOMENTUM BAR (left, below HP panel) ---
        if momentum is not None:
            self._draw_momentum_bar(surface, momentum, sh)

        # --- DASH COOLDOWN arc (near momentum panel) ---
        if dash_cooldown_pct > 0:
            cx, cy = 280, sh - hpanel_h - 22
            pygame.draw.arc(
                surface, (100, 180, 255),
                (cx - 16, cy - 16, 32, 32),
                math.pi / 2,
                math.pi / 2 + (1.0 - dash_cooldown_pct) * 2 * math.pi,
                4
            )
            dash_t = pygame.font.SysFont("arial", 12).render("DASH", True, (120, 180, 255))
            surface.blit(dash_t, (cx - dash_t.get_width() // 2, cy + 12))

        # --- OBJECTIVE (bottom-right) ---
        obj_str = objective or "FIND THE CORRECT PORTAL"
        obj_w   = max(280, self.fs.size(obj_str)[0] + 30)
        self._panel(surface, sw - obj_w - 10, sh - 56, obj_w, 46)
        ot = self.fs.render("OBJECTIVE:", True, accent)
        ov = self.fs.render(obj_str, True, self.WHITE)
        surface.blit(ot, (sw - obj_w, sh - 52))
        surface.blit(ov, (sw - obj_w, sh - 32))

        # --- ATTACK COOLDOWN indicator ---
        if attack_cooldown_pct > 0:
            pygame.draw.arc(surface, (255, 150, 0),
                            (sw - obj_w - 50, sh - 46, 36, 36),
                            math.pi / 2,
                            math.pi / 2 + (1 - attack_cooldown_pct) * 2 * math.pi, 4)

        # --- Fragment count ---
        if fragment_count > 0:
            ft = self.fs.render(f"◆ ×{fragment_count}", True, (255, 220, 50))
            surface.blit(ft, (sw // 2 - ft.get_width() // 2, sh - 40))

        # --- LOW TIME full-screen vignette ---
        if time_left <= 10:
            warn2  = pygame.Surface((sw, sh), pygame.SRCALPHA)
            alpha2 = int(20 + math.sin(t * 5) * 18)
            warn2.fill((255, 0, 0, max(0, alpha2)))
            surface.blit(warn2, (0, 0))
            warn_t = self.fm.render("TIME IS RUNNING OUT!", True, (255, 80, 80))
            surface.blit(warn_t, (sw // 2 - warn_t.get_width() // 2, sh // 2 - 30))

        # --- LOW HP vignette ---
        if hp > 0 and hp <= max_hp * 0.25:
            vig       = pygame.Surface((sw, sh), pygame.SRCALPHA)
            vig_alpha = int(30 + math.sin(t * 4) * 25)
            vig.fill((220, 0, 0, max(0, vig_alpha)))
            surface.blit(vig, (0, 0))

    # ------------------------------------------------------------------
    # MOMENTUM BAR
    # ------------------------------------------------------------------

    def _draw_momentum_bar(self, surface, momentum, sh):
        from core.momentum import Momentum
        tier    = momentum.tier
        frac    = momentum.fraction   # 0–1
        rb_ready = momentum.reality_break_ready

        panel_x, panel_y = 10, sh - 115
        panel_w, panel_h = 270, 38
        self._panel(surface, panel_x, panel_y, panel_w, panel_h)

        # Label
        tier_col = TIER_COLORS.get(tier, (80, 80, 80))
        label    = f"MOMENTUM — {tier.replace('_', ' ')}"
        lt       = self.fs.render(label, True, tier_col)
        surface.blit(lt, (panel_x + 6, panel_y + 4))

        # Bar segments
        bx  = panel_x + 6
        by  = panel_y + 22
        bw  = panel_w - 12
        bh  = 10
        # Background
        pygame.draw.rect(surface, (30, 10, 50), (bx, by, bw, bh), border_radius=4)

        # Filled portion
        fill = int(bw * frac)
        if fill > 0:
            pygame.draw.rect(surface, tier_col, (bx, by, fill, bh), border_radius=4)

        # Tier boundary ticks
        for pct in (TIER_FOCUSED / MAX_MOMENTUM, TIER_ASCENDANT / MAX_MOMENTUM):
            tx = bx + int(bw * pct)
            pygame.draw.line(surface, (200, 200, 200), (tx, by - 2), (tx, by + bh + 2), 2)

        # Reality Break gem (blinks when ready)
        gem_x = panel_x + panel_w - 22
        gem_y = panel_y + 6
        if rb_ready:
            gem_alpha = int(180 + 70 * abs(math.sin(self._t * 5)))
            gs = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.polygon(gs, (0, 230, 255, gem_alpha),
                                [(9, 0), (18, 7), (14, 18), (4, 18), (0, 7)])
            surface.blit(gs, (gem_x, gem_y))
            # "Q" label
            ql = pygame.font.SysFont("arial", 11).render("[Q]", True, (0, 220, 255))
            surface.blit(ql, (gem_x - 4, gem_y + 18))
        else:
            # Dim placeholder
            pygame.draw.polygon(surface, (40, 40, 80),
                                [(gem_x + 9, gem_y), (gem_x + 18, gem_y + 7),
                                 (gem_x + 14, gem_y + 18), (gem_x + 4, gem_y + 18),
                                 (gem_x, gem_y + 7)])
