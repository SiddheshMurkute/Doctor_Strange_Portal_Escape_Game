# ui/portal_result.py
"""Screen shown after portal interaction (correct or wrong)."""
import pygame
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class PortalResult:
    GOLD  = (255, 180, 0)
    GREEN = (80, 220, 80)
    RED   = (220, 60, 60)
    WHITE = (255, 255, 255)

    def __init__(self, font_large, font_med, font_small):
        self.fl = font_large
        self.fm = font_med
        self.fs = font_small
        self._t   = 0.0
        self._dur = 2.5    # seconds to auto-dismiss
        self.result   = 'correct'  # or 'wrong'
        self.penalty  = 0
        self.continue_flag = False

    def show(self, result: str, penalty: int = 0, duration: float = 2.5):
        self.result   = result
        self.penalty  = penalty
        self._t       = 0
        self._dur     = duration
        self.continue_flag = False

    def update(self, dt):
        self._t += dt
        if self._t >= self._dur:
            self.continue_flag = True

    def draw(self, surface):
        t  = self._t
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        is_correct = (self.result == 'correct')

        # Overlay
        col = self.GREEN if is_correct else self.RED
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        alpha = int(150 + math.sin(t*4)*30)
        overlay.fill((*col, min(200, alpha // 3)))
        surface.blit(overlay, (0, 0))

        # Big icon
        icon_size = 100
        icon_s = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.circle(icon_s, col, (icon_size//2, icon_size//2), icon_size//2)
        pygame.draw.circle(icon_s, (255,255,255), (icon_size//2, icon_size//2), icon_size//2, 4)
        # Check or X
        if is_correct:
            pts = [(25, 50),(45,70),(75,30)]
            pygame.draw.lines(icon_s, (255,255,255), False, pts, 8)
        else:
            pygame.draw.line(icon_s, (255,255,255), (25,25),(75,75), 8)
            pygame.draw.line(icon_s, (255,255,255), (75,25),(25,75), 8)
        surface.blit(icon_s, (sw//2 - icon_size//2, sh//3))

        if is_correct:
            title = self.fl.render("CORRECT PORTAL!", True, self.GREEN)
            sub   = self.fm.render("DIMENSION BREACHED — ADVANCING...", True, self.WHITE)
        else:
            title = self.fl.render("WRONG PORTAL!", True, self.RED)
            sub   = self.fm.render(f"PENALTY: {self.penalty:+d} POINTS   Stay and search...", True, self.WHITE)

        surface.blit(title, (sw//2 - title.get_width()//2, sh//2 + 20))
        surface.blit(sub,   (sw//2 - sub.get_width()//2,   sh//2 + 70))

        # Progress bar
        prog = min(1.0, self._t / self._dur)
        pygame.draw.rect(surface, (60,60,60), (sw//4, sh*3//4, sw//2, 8), border_radius=4)
        pygame.draw.rect(surface, col, (sw//4, sh*3//4, int(sw//2*prog), 8), border_radius=4)
