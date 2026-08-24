# ui/pause_menu.py
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class PauseMenu:
    GOLD  = (255, 180, 0)
    WHITE = (255, 255, 255)

    def __init__(self, font_large, font_med, font_small):
        self.fl = font_large
        self.fm = font_med
        self.fs = font_small
        self.options  = ["RESUME", "RESTART", "MAIN MENU"]
        self.selected = 0
        self.action   = None

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.action = self.options[self.selected]
                return self.action
            elif event.key == pygame.K_ESCAPE:
                return 'RESUME'
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(mouse_pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(mouse_pos):
                    self.action = self.options[i]
                    return self.action
        return None

    def _option_rects(self):
        bw, bh = 240, 52
        cy = SCREEN_HEIGHT // 2 + 20
        return [pygame.Rect(SCREEN_WIDTH//2-bw//2, cy + i*64, bw, bh) for i in range(3)]

    def draw(self, surface):
        # Dim overlay
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 165))
        surface.blit(dim, (0, 0))

        # Panel
        pw, ph = 380, 320
        px = SCREEN_WIDTH//2 - pw//2
        py = SCREEN_HEIGHT//2 - ph//2
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((15, 10, 35, 230))
        pygame.draw.rect(panel, self.GOLD, (0, 0, pw, ph), 2, border_radius=10)
        surface.blit(panel, (px, py))

        title = self.fl.render("PAUSED", True, self.GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, py + 20))

        for i, (text, rect) in enumerate(zip(self.options, self._option_rects())):
            is_sel = (i == self.selected)
            btn = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            if is_sel:
                btn.fill((255, 180, 0, 40))
                pygame.draw.rect(btn, self.GOLD, (0, 0, rect.w, rect.h), 2, border_radius=6)
            else:
                btn.fill((30, 20, 55, 120))
                pygame.draw.rect(btn, (80, 60, 120), (0, 0, rect.w, rect.h), 1, border_radius=6)
            surface.blit(btn, (rect.x, rect.y))
            col = self.GOLD if is_sel else (200, 190, 220)
            txt = self.fm.render(text, True, col)
            surface.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
