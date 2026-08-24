# ui/result_screen.py
"""Defeat screen, Stage Failed, Final Escape, and Final Result screens."""
import pygame
import math
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

GOLD  = (255, 180, 0)
WHITE = (255, 255, 255)
RED   = (220, 50, 50)
GREEN = (80, 220, 80)


class FinalEscapeScreen:
    """Short cinematic shown after clearing Stage 5 portal."""
    def __init__(self, font_large, font_med):
        self.fl = font_large
        self.fm = font_med
        self._t   = 0.0
        self._dur = 4.0
        self.done = False
        self._particles = []
        for _ in range(80):
            self._particles.append([
                random.uniform(0, SCREEN_WIDTH),
                random.uniform(0, SCREEN_HEIGHT),
                random.uniform(-3, 3), random.uniform(-4, -1),
                random.uniform(0.5, 2.0)
            ])

    def update(self, dt):
        self._t += dt
        if self._t >= self._dur:
            self.done = True
        for p in self._particles:
            p[0] += p[2]; p[1] += p[3]
            if p[1] < -20:
                p[0] = random.uniform(0, SCREEN_WIDTH)
                p[1] = SCREEN_HEIGHT + 20

    def draw(self, surface):
        t  = self._t
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        frac   = min(1.0, t / self._dur)

        # Flash transition
        surface.fill((0, 0, 0))
        flash_alpha = int(255 * max(0, 1 - frac * 3))
        if flash_alpha > 0:
            flash = pygame.Surface((sw, sh), pygame.SRCALPHA)
            flash.fill((255, 220, 100, flash_alpha))
            surface.blit(flash, (0, 0))

        # Background shimmer
        for y in range(sh):
            r = int(10 + frac * 20)
            g = int(5  + frac * 10)
            b = int(30 + frac * 70)
            pygame.draw.line(surface, (r, g, b), (0, y), (sw, y))

        # Portal burst
        cx, cy = sw//2, sh//2
        ring_r = int(frac * 300)
        for i in range(4):
            r2 = ring_r - i*30
            if r2 > 0:
                pygame.draw.ellipse(surface, (*GOLD, max(0, 200-i*50)),
                                    (cx-r2, cy-int(r2*0.65), r2*2, int(r2*1.3)), 3)

        # Particles
        for p in self._particles:
            alpha = int(200 * (1 - frac))
            ps = pygame.Surface((5,5), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*GOLD, alpha), (2,2), 2)
            surface.blit(ps, (int(p[0]), int(p[1])))

        # Text sequence
        if t > 0.5:
            t1 = self.fl.render("CORRECT PORTAL FOUND", True, GOLD)
            surface.blit(t1, (sw//2 - t1.get_width()//2, sh//2 - 80))
        if t > 1.2:
            t2 = self.fm.render("MULTIVERSE FRACTURE SEALED", True, WHITE)
            surface.blit(t2, (sw//2 - t2.get_width()//2, sh//2 - 20))
        if t > 2.0:
            t3 = self.fm.render("ESCAPE COMPLETE", True, GREEN)
            surface.blit(t3, (sw//2 - t3.get_width()//2, sh//2 + 40))


class FinalResultScreen:
    def __init__(self, font_large, font_med, font_small):
        self.fl = font_large; self.fm = font_med; self.fs = font_small
        self.options  = ["PLAY AGAIN", "MAIN MENU"]
        self.selected = 0

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected-1) % 2
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected+1) % 2
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.options[self.selected]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._btns()):
                if rect.collidepoint(mouse_pos):
                    return self.options[i]
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._btns()):
                if rect.collidepoint(mouse_pos):
                    self.selected = i
        return None

    def _btns(self):
        bw, bh = 240, 52
        cy = SCREEN_HEIGHT * 3 // 4
        return [pygame.Rect(SCREEN_WIDTH//2-bw//2, cy + i*64, bw, bh) for i in range(2)]

    def draw(self, surface, score, total_time, stages):
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        t2 = pygame.time.get_ticks() / 1000
        for y in range(sh):
            frac = y/sh
            pygame.draw.line(surface, (int(5+frac*20), int(10+frac*30), int(25+frac*60)), (0,y),(sw,y))
        title = self.fl.render("MULTIVERSE ESCAPE COMPLETE", True, GOLD)
        surface.blit(title, (sw//2-title.get_width()//2, 60))
        # Stats
        lines = [
            ("FINAL SCORE",    f"{score:,}"),
            ("TOTAL TIME",     f"{int(total_time)//60:02d}:{int(total_time)%60:02d}"),
            ("STAGES COMPLETED", f"{stages} / 5"),
            ("ESCAPE STATUS",  "SUCCESS"),
        ]
        for i, (lbl, val) in enumerate(lines):
            l = self.fm.render(lbl, True, (180, 160, 200))
            v = self.fm.render(val, True, GOLD)
            surface.blit(l, (sw//2 - 200, 180 + i*60))
            surface.blit(v, (sw//2 + 20,  180 + i*60))
        for i, rect in enumerate(self._btns()):
            is_sel = (i == self.selected)
            btn = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            btn.fill((255,180,0,40) if is_sel else (30,20,55,120))
            pygame.draw.rect(btn, GOLD if is_sel else (80,60,120), (0,0,rect.w,rect.h), 2, border_radius=6)
            surface.blit(btn, (rect.x, rect.y))
            col = GOLD if is_sel else WHITE
            txt = self.fm.render(self.options[i], True, col)
            surface.blit(txt, (rect.centerx-txt.get_width()//2, rect.centery-txt.get_height()//2))


class FailureScreen:
    def __init__(self, font_large, font_med, font_small):
        self.fl = font_large; self.fm = font_med; self.fs = font_small
        self.options  = ["RETRY STAGE", "RESTART GAME", "MAIN MENU"]
        self.selected = 0
        self.reason   = "STAGE FAILED"

    def set_reason(self, defeated: bool):
        self.reason = "DOCTOR STRANGE DEFEATED" if defeated else "DIMENSION COLLAPSED"

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected-1) % 3
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected+1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.options[self.selected]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._btns()):
                if rect.collidepoint(mouse_pos):
                    return self.options[i]
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._btns()):
                if rect.collidepoint(mouse_pos):
                    self.selected = i
        return None

    def _btns(self):
        bw, bh = 240, 52
        cy = SCREEN_HEIGHT//2 + 40
        return [pygame.Rect(SCREEN_WIDTH//2-bw//2, cy+i*64, bw, bh) for i in range(3)]

    def draw(self, surface, score, stage):
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        # Dark red overlay
        surface.fill((15, 5, 10))
        for y in range(sh):
            frac = y/sh
            pygame.draw.line(surface, (int(15+frac*40), int(5+frac*5), int(10+frac*15)), (0,y),(sw,y))
        t2 = self.fl.render(self.reason, True, RED)
        surface.blit(t2, (sw//2-t2.get_width()//2, 80))
        lines = [
            ("SCORE",   f"{score:,}"),
            ("STAGE",   f"{stage} / 5"),
        ]
        for i, (lbl,val) in enumerate(lines):
            l = self.fm.render(lbl, True, (180,140,140))
            v = self.fm.render(val, True, WHITE)
            surface.blit(l, (sw//2-180, 200+i*55))
            surface.blit(v, (sw//2+20,  200+i*55))
        for i, rect in enumerate(self._btns()):
            is_sel = (i == self.selected)
            btn = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            btn.fill((220,50,50,40) if is_sel else (30,10,15,120))
            pygame.draw.rect(btn, RED if is_sel else (100,40,40), (0,0,rect.w,rect.h), 2, border_radius=6)
            surface.blit(btn, (rect.x, rect.y))
            col = WHITE if is_sel else (180,140,140)
            txt = self.fm.render(self.options[i], True, col)
            surface.blit(txt, (rect.centerx-txt.get_width()//2, rect.centery-txt.get_height()//2))
