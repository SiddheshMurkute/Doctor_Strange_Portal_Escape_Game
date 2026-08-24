# ui/main_menu.py
"""Cinematic Doctor Strange main menu."""
import pygame
import math
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from effects.glow import draw_glow


class MainMenu:
    GOLD   = (255, 180, 0)
    ORANGE = (255, 100, 20)
    WHITE  = (255, 255, 255)
    DARK   = (10, 5, 20)

    def __init__(self, font_large, font_med, font_small):
        self.fl  = font_large
        self.fm  = font_med
        self.fs  = font_small
        self._t  = 0.0
        self._particles = [(random.uniform(0, SCREEN_WIDTH), random.uniform(0, SCREEN_HEIGHT),
                            random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.3),
                            random.uniform(0.8, 1.8)) for _ in range(120)]
        self._cracks    = [(random.randint(50, SCREEN_WIDTH-50),
                            random.randint(50, SCREEN_HEIGHT-50),
                            random.uniform(0, math.pi*2),
                            random.randint(40, 100)) for _ in range(8)]
        self.selected   = 0
        self._buttons   = ["PLAY", "HOW TO PLAY", "EXIT"]
        self.hovered    = -1
        self.clicked    = None

    def handle_event(self, event, mouse_pos):
        bx, by, bw, bh = self._button_rects()[self.selected]
        if event.type == pygame.MOUSEMOTION:
            self.hovered = -1
            for i, (rx, ry, rw, rh) in enumerate(self._button_rects()):
                if rx <= mouse_pos[0] <= rx+rw and ry <= mouse_pos[1] <= ry+rh:
                    self.hovered = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if 0 <= self.hovered < len(self._buttons):
                self.clicked = self._buttons[self.hovered]
                return self.clicked
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self._buttons)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self._buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.clicked = self._buttons[self.selected]
                return self.clicked
        return None

    def _button_rects(self):
        bw, bh = 280, 52
        cx = SCREEN_WIDTH // 2 - bw // 2
        base_y = SCREEN_HEIGHT * 2 // 3
        return [(cx, base_y + i * 68, bw, bh) for i in range(len(self._buttons))]

    def update(self, dt: float):
        self._t += dt
        # Update particles
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        new_p = []
        for (x, y, vx, vy, life) in self._particles:
            x += vx; y += vy
            if y < -10:
                y = sh + 10
                x = random.uniform(0, sw)
            new_p.append((x, y, vx, vy, life))
        self._particles = new_p

    def draw(self, surface: pygame.Surface):
        t = self._t
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT

        # --- Deep space background ---
        surface.fill(self.DARK)
        for y2 in range(sh):
            frac = y2 / sh
            r = int(8 + frac * 30)
            g = int(2 + frac * 10)
            b = int(30 + frac * 60)
            pygame.draw.line(surface, (r, g, b), (0, y2), (sw, y2))

        # --- Dimensional cracks ---
        for cx2, cy2, angle, length in self._cracks:
            for k in range(3):
                seg_angle = angle + k * 0.45
                x2 = cx2 + int(math.cos(seg_angle) * length * (k+1)/3)
                y2 = cy2 + int(math.sin(seg_angle) * length * (k+1)/3)
                alpha = int(100 + math.sin(t*2+cx2*0.01) * 60)
                crack_col = (80, 40, 200)
                pygame.draw.line(surface, crack_col, (cx2, cy2), (x2, y2), 2)

        # --- Mystical symbols (mandalas) ---
        sym_cx = sw // 2
        sym_cy = sh // 2 - 30
        for ring in range(4):
            r2 = 60 + ring * 40
            pts = 12 + ring * 6
            for p in range(pts):
                a = 2 * math.pi * p / pts + t * (0.3 if ring % 2 == 0 else -0.3)
                x2 = sym_cx + int(math.cos(a) * r2)
                y2 = sym_cy + int(math.sin(a) * r2)
                dot_col = (255, 180 - ring*30, 0)
                pygame.draw.circle(surface, dot_col, (x2, y2), 2 + (pts % 3))

        # --- Central golden portal ---
        portal_r = int(90 + math.sin(t*1.2) * 8)
        draw_glow(surface, (sym_cx, sym_cy), portal_r + 40, self.GOLD, 80)
        # Oval body
        inner_s = pygame.Surface((portal_r*2+20, int(portal_r*1.4)+20), pygame.SRCALPHA)
        pygame.draw.ellipse(inner_s, (5, 2, 30, 230),
                            (10, 10, portal_r*2, int(portal_r*1.3)))
        surface.blit(inner_s, (sym_cx-portal_r-10, sym_cy-int(portal_r*0.65)-10))
        # Rotating rings
        for ring_i in range(3):
            ring_r = portal_r - ring_i * 12
            ang = t * (60 + ring_i*20) * (1 if ring_i%2==0 else -1)
            ring_s = pygame.Surface((ring_r*2+6, ring_r*2+6), pygame.SRCALPHA)
            col_a = 220 - ring_i*50
            pygame.draw.ellipse(ring_s, (*self.GOLD, col_a), (3, 3, ring_r*2, ring_r*2), 3)
            rot = pygame.transform.rotate(ring_s, ang)
            rw, rh = rot.get_size()
            surface.blit(rot, (sym_cx-rw//2, sym_cy-rh//2), special_flags=pygame.BLEND_RGBA_ADD)
        # Portal frame
        pygame.draw.ellipse(surface, self.GOLD,
                            (sym_cx-portal_r, sym_cy-int(portal_r*0.65),
                             portal_r*2, int(portal_r*1.3)), 4)

        # --- Particles ---
        for (px, py, _, _, _) in self._particles:
            alpha = int(180 + math.sin(t*2+px*0.05)*60)
            s2 = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s2, (255, 180, 50, alpha), (2,2), 2)
            surface.blit(s2, (int(px), int(py)))

        # --- Title ---
        title1 = self.fl.render("DOCTOR STRANGE:", True, self.GOLD)
        title2 = self.fl.render("PORTAL ESCAPE", True, self.WHITE)
        tx1 = sw//2 - title1.get_width()//2
        ty  = 60
        surface.blit(title1, (tx1, ty))
        surface.blit(title2, (sw//2 - title2.get_width()//2, ty + title1.get_height() + 6))

        # --- Subtitle ---
        sub = self.fs.render("FIND THE RIGHT PORTAL BEFORE THE MULTIVERSE COLLAPSES",
                             True, (200, 160, 80))
        surface.blit(sub, (sw//2 - sub.get_width()//2, ty + title1.get_height()*2 + 16))

        # --- Buttons ---
        highlight = self.hovered if self.hovered >= 0 else self.selected
        for i, (rx, ry, rw, rh) in enumerate(self._button_rects()):
            is_sel = (i == highlight)
            # Panel
            panel = pygame.Surface((rw, rh), pygame.SRCALPHA)
            if is_sel:
                panel.fill((255, 180, 0, 50))
                pygame.draw.rect(panel, self.GOLD, (0, 0, rw, rh), 2, border_radius=6)
            else:
                panel.fill((30, 20, 60, 150))
                pygame.draw.rect(panel, (100, 60, 180), (0, 0, rw, rh), 1, border_radius=6)
            surface.blit(panel, (rx, ry))
            col = self.GOLD if is_sel else (200, 190, 220)
            scale = 1.06 if is_sel else 1.0
            txt = self.fm.render(self._buttons[i], True, col)
            if is_sel:
                txt = pygame.transform.scale(txt, (int(txt.get_width()*scale), int(txt.get_height()*scale)))
            surface.blit(txt, (rx + rw//2 - txt.get_width()//2,
                               ry + rh//2 - txt.get_height()//2))
