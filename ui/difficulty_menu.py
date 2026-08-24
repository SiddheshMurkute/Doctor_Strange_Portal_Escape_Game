# ui/difficulty_menu.py
import pygame
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class DifficultyMenu:
    GOLD  = (255, 180, 0)
    WHITE = (255, 255, 255)
    DARK  = (10, 5, 20)

    DESCRIPTIONS = {
        "EASY":   "Fewer enemies, slower pace.\nPerfect for learning the game.",
        "MEDIUM": "Balanced challenge.\nThe intended experience.",
        "HARD":   "Maximum pressure.\nOnly the strongest escape.",
    }

    def __init__(self, font_large, font_med, font_small):
        self.fl = font_large
        self.fm = font_med
        self.fs = font_small
        self.options   = ["EASY", "MEDIUM", "HARD"]
        self.selected  = 1
        self.confirmed = None
        self._t = 0.0

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % 3
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.confirmed = self.options[self.selected]
                return self.confirmed
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(mouse_pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(mouse_pos):
                    self.confirmed = self.options[i]
                    return self.confirmed
        return None

    def _option_rects(self):
        bw, bh = 200, 70
        cy = SCREEN_HEIGHT // 2
        spacing = 240
        start_x = SCREEN_WIDTH // 2 - spacing
        return [pygame.Rect(start_x + i*spacing - bw//2, cy, bw, bh) for i in range(3)]

    def update(self, dt):
        self._t += dt

    def draw(self, surface):
        t = self._t
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        surface.fill((8, 4, 18))
        # Gradient
        for y in range(sh):
            frac = y/sh
            pygame.draw.line(surface, (int(8+frac*25), int(4+frac*10), int(18+frac*50)),
                             (0,y),(sw,y))

        title = self.fl.render("SELECT DIFFICULTY", True, self.GOLD)
        surface.blit(title, (sw//2 - title.get_width()//2, 80))

        for i, (text, rect) in enumerate(zip(self.options, self._option_rects())):
            is_sel = (i == self.selected)
            col   = [(80,220,80),(255,180,0),(220,60,60)][i]
            panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            if is_sel:
                pulse = int(math.sin(t*3)*15)
                panel.fill((*col, max(0, min(255, 60+pulse))))
                pygame.draw.rect(panel, col, (0,0,rect.w,rect.h), 3, border_radius=8)
            else:
                panel.fill((30,20,55,120))
                pygame.draw.rect(panel, (80,60,120), (0,0,rect.w,rect.h), 1, border_radius=8)
            surface.blit(panel, (rect.x, rect.y))
            txt = self.fm.render(text, True, col if is_sel else (160,140,200))
            surface.blit(txt, (rect.centerx-txt.get_width()//2, rect.centery-txt.get_height()//2))

        # Description
        if 0 <= self.selected < 3:
            desc = self.DESCRIPTIONS[self.options[self.selected]]
            for j, line in enumerate(desc.split('\n')):
                d = self.fs.render(line, True, (190, 180, 210))
                surface.blit(d, (sw//2 - d.get_width()//2, sh//2 + 100 + j*30))

        hint = self.fs.render("← → to select   ENTER to confirm", True, (120, 100, 160))
        surface.blit(hint, (sw//2 - hint.get_width()//2, sh - 60))
