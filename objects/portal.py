# objects/portal.py
"""Golden mystical portal — rendered with Pygame procedural graphics."""
import pygame
import math
import random

PORTAL_W = 80
PORTAL_H = 110
INTERACT_DIST = 90  # pixels from player center to portal center

class Portal:
    """A glowing mystical portal."""

    COLORS_BY_STAGE = {
        1: (255, 180, 0),    # golden
        2: (80, 200, 255),   # cosmic cyan
        3: (200, 100, 255),  # purple alien
        4: (150, 220, 255),  # icy
        5: (255, 80, 20),    # infernal
    }

    def __init__(self, x: int, y: int, stage: int, is_correct: bool,
                 label: str = "", portal_id: int = 0):
        self.rect       = pygame.Rect(x, y, PORTAL_W, PORTAL_H)
        self.stage      = stage
        self.is_correct = is_correct
        self.label      = label
        self.portal_id  = portal_id
        self.activated  = False
        self._angle     = 0.0
        self._pulse     = 0.0
        self._particles: list = []
        self._color     = self.COLORS_BY_STAGE.get(stage, (255, 180, 0))
        self._particle_timer = 0.0

    def update(self, dt: float):
        self._angle    = (self._angle + dt * 90) % 360
        self._pulse    = (self._pulse  + dt * 2.5) % (2 * math.pi)
        self._particle_timer += dt
        if self._particle_timer >= 0.06:
            self._particle_timer = 0
            self._spawn_particle()
        alive = []
        for p in self._particles:
            p[4] -= dt
            if p[4] > 0:
                p[0] += p[2]
                p[1] += p[3]
                alive.append(p)
        self._particles = alive

    def _spawn_particle(self):
        cx = self.rect.centerx
        cy = self.rect.centery
        ang = random.uniform(0, math.pi * 2)
        r   = random.uniform(30, 50)
        px  = cx + math.cos(ang) * r
        py  = cy + math.sin(ang) * r * 0.65
        vx  = math.cos(ang) * random.uniform(0.3, 1.0)
        vy  = math.sin(ang) * random.uniform(0.3, 1.0)
        life = random.uniform(0.4, 0.9)
        self._particles.append([px, py, vx, vy, life, life])

    def is_player_nearby(self, player_rect: pygame.Rect) -> bool:
        px, py = player_rect.centerx, player_rect.centery
        cx, cy = self.rect.centerx, self.rect.centery
        return math.hypot(px-cx, py-cy) < INTERACT_DIST

    def draw(self, surface: pygame.Surface, camera, font=None):
        cx = self.rect.centerx - int(camera.offset_x)
        cy = self.rect.centery - int(camera.offset_y)
        col = self._color

        pulse = math.sin(self._pulse)
        outer_r = 48 + int(pulse * 4)
        inner_r = 32 + int(pulse * 2)

        # --- Outer glow ---
        glow_surf = pygame.Surface((outer_r*4, outer_r*4), pygame.SRCALPHA)
        for gr in range(outer_r*2, 0, -4):
            alpha = int(60 * (1 - gr/(outer_r*2)))
            pygame.draw.ellipse(glow_surf, (*col, alpha),
                                (outer_r*2-gr, int(outer_r*2-gr*0.65),
                                 gr*2, int(gr*1.3)), 0)
        surface.blit(glow_surf, (cx - outer_r*2, cy - outer_r*2),
                     special_flags=pygame.BLEND_RGBA_ADD)

        # --- Portal oval body ---
        portal_surf = pygame.Surface((outer_r*2+10, int(outer_r*2*0.65)+10), pygame.SRCALPHA)
        ps_cx = outer_r + 5
        ps_cy = int(outer_r * 0.65) + 5
        # Dark interior
        pygame.draw.ellipse(portal_surf, (10, 5, 30, 220),
                            (5, 5, outer_r*2, int(outer_r*1.3)))
        # Interior shimmer
        shimmer = (min(255, col[0]//2), min(255, col[1]//2), min(255, col[2]//2))
        pygame.draw.ellipse(portal_surf, (*shimmer, 80),
                            (15, 15, outer_r*2-20, int(outer_r*1.3)-20))
        surface.blit(portal_surf, (cx-outer_r-5, cy-int(outer_r*0.65)-5))

        # --- Rotating rings ---
        for ring_idx in range(3):
            angle_off = self._angle + ring_idx * 40
            ring_r = outer_r - ring_idx * 6
            ring_a = 200 - ring_idx * 50
            ring_surf = pygame.Surface((ring_r*2+4, ring_r*2+4), pygame.SRCALPHA)
            pygame.draw.ellipse(ring_surf, (*col, ring_a),
                                (2, 2, ring_r*2, ring_r*2), 3)
            # Rotate by drawing arc-ish rotated points
            rotated = pygame.transform.rotate(ring_surf, angle_off)
            rw, rh = rotated.get_size()
            surface.blit(rotated, (cx-rw//2, cy-rh//2),
                         special_flags=pygame.BLEND_RGBA_ADD)

        # --- Outer solid ring frame ---
        pygame.draw.ellipse(surface, col,
                            (cx-outer_r, int(cy-outer_r*0.65), outer_r*2, int(outer_r*1.3)), 4)
        # Inner ring
        pygame.draw.ellipse(surface, (255, 255, 200),
                            (cx-inner_r, int(cy-inner_r*0.65), inner_r*2, int(inner_r*1.3)), 2)

        # --- Particles ---
        for p in self._particles:
            sx = int(p[0]) - int(camera.offset_x)
            sy = int(p[1]) - int(camera.offset_y)
            alpha = int(255 * (p[4] / p[5]))
            ps = pygame.Surface((6,6), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*col, alpha), (3,3), 3)
            surface.blit(ps, (sx-3, sy-3), special_flags=pygame.BLEND_RGBA_ADD)

        # --- Label ---
        if self.label and font:
            txt = font.render(self.label, True, (255, 220, 120))
            surface.blit(txt, (cx - txt.get_width()//2, cy + outer_r + 5))

    def draw_interact_prompt(self, surface, camera, font):
        if not font:
            return
        cx = self.rect.centerx - int(camera.offset_x)
        cy = self.rect.centery - int(camera.offset_y)
        txt = font.render("[E] ENTER PORTAL", True, (255, 220, 80))
        bg  = pygame.Surface((txt.get_width()+16, txt.get_height()+8), pygame.SRCALPHA)
        bg.fill((0,0,0,150))
        surface.blit(bg, (cx-bg.get_width()//2, cy-80))
        surface.blit(txt, (cx-txt.get_width()//2, cy-76))
