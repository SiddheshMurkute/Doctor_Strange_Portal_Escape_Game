# enemies/enemy.py
"""Base enemy class with procedural Thanos-army visuals."""
import pygame
import math
import random
from effects.particles import ParticleSystem

ENEMY_HP_BASE    = 60
ENEMY_SPEED_BASE = 90   # px/sec
ENEMY_DMG_BASE   = 5
ENEMY_ATTACK_CD  = 1.0  # seconds

def _draw_enemy_frame(kind: str, frame: int, size=(52, 64)) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    t = (math.sin(frame * 0.5) + 1) / 2

    # Color palette based on kind
    body_col  = {'patrol':(60,30,90),  'chaser':(80,20,20),  'attacker':(40,60,20)}.get(kind, (60,30,90))
    armor_col = {'patrol':(130,80,180),'chaser':(180,50,50), 'attacker':(80,150,40)}.get(kind, (130,80,180))
    eye_col   = (255, 50, 0)

    # Legs with walk bob
    leg_off = int(math.sin(frame * 1.4) * 4)
    pygame.draw.rect(surf, body_col, (w//2-10, h//2+10, 8, 16 + leg_off), border_radius=3)
    pygame.draw.rect(surf, body_col, (w//2+2,  h//2+10, 8, 16 - leg_off), border_radius=3)

    # Torso/armor
    pygame.draw.rect(surf, body_col,  (w//2-13, h//2-10, 26, 22), border_radius=4)
    pygame.draw.polygon(surf, armor_col, [
        (w//2-13, h//2-10), (w//2+13, h//2-10),
        (w//2+10, h//2+5),  (w//2-10, h//2+5),
    ])

    # Arms
    arm_swing = int(math.sin(frame * 1.4) * 5)
    pygame.draw.line(surf, body_col, (w//2-13, h//2-4), (w//2-22, h//2+10+arm_swing), 5)
    pygame.draw.line(surf, body_col, (w//2+13, h//2-4), (w//2+22, h//2+10-arm_swing), 5)
    # Fists
    fist_col = armor_col
    pygame.draw.circle(surf, fist_col, (w//2-22, h//2+14+arm_swing), 5)
    pygame.draw.circle(surf, fist_col, (w//2+22, h//2+14-arm_swing), 5)

    # Head
    head_y = h//2 - 26
    pygame.draw.ellipse(surf, body_col, (w//2-10, head_y, 20, 20))
    # Helmet
    pygame.draw.arc(surf, armor_col, (w//2-11, head_y-2, 22, 14), 0, math.pi, 5)
    # Eyes
    pygame.draw.circle(surf, eye_col, (w//2-4, head_y+10), 3)
    pygame.draw.circle(surf, eye_col, (w//2+4, head_y+10), 3)

    return surf

def build_enemy_animations(kind: str, size=(52,64)) -> dict:
    states = {'walk': 8, 'attack': 6, 'death': 6, 'idle': 6}
    return {s: [_draw_enemy_frame(kind, f, size) for f in range(n)]
            for s, n in states.items()}


class Enemy:
    def __init__(self, x, y, kind='patrol', hp=None, speed=None, damage=None):
        self.kind   = kind
        self.rect   = pygame.Rect(x, y, 52, 64)
        self.hp     = hp    or ENEMY_HP_BASE
        self.max_hp = self.hp
        self.speed  = speed or ENEMY_SPEED_BASE
        self.damage = damage or ENEMY_DMG_BASE
        self.alive  = True

        self._anims = build_enemy_animations(kind, (52, 64))
        self._state = 'idle'
        self._frame = 0.0
        self._frame_speed = 8.0

        self._attack_cd = 0.0
        self._flash     = 0.0
        self._flash_col = (255, 255, 255)
        self._death_timer = 0.0

        self.particles = ParticleSystem()
        self.vel       = pygame.Vector2(0, 0)

    def take_damage(self, amount: int) -> bool:
        if not self.alive:
            return False
        self.hp -= amount
        self._flash = 0.2
        self.particles.emit(self.rect.centerx, self.rect.centery, 8,
                            (255, 150, 0), (2, 5), (0.1, 0.3))
        if self.hp <= 0:
            self.alive = False
            self._state = 'death'
            self._frame = 0.0
            self.particles.emit(self.rect.centerx, self.rect.centery, 20,
                                (200, 80, 20), (2, 6), (0.3, 0.7))
            return True  # just died
        return False

    def knockback(self, angle: float, distance: float = 70.0):
        """Push the enemy away from an attack direction."""
        self.rect.x += round(math.cos(angle) * distance)
        self.rect.y += round(math.sin(angle) * distance)

    def can_attack(self) -> bool:
        return self._attack_cd <= 0

    def reset_attack_cd(self):
        self._attack_cd = ENEMY_ATTACK_CD

    def update(self, dt, walls=None):
        if self._attack_cd > 0:
            self._attack_cd -= dt
        if self._flash > 0:
            self._flash -= dt

        if not self.alive:
            self._death_timer += dt
            self._frame = min(self._frame + self._frame_speed * dt,
                              len(self._anims['death']) - 1)
            self.particles.update(dt)
            return

        # Move
        if self.vel.length() > 0:
            self.rect.x += int(self.vel.x * dt)
            if walls:
                from core.collision import collide_rects
                mtv = collide_rects(self.rect, walls)
                self.rect.x += int(mtv.x)
            self.rect.y += int(self.vel.y * dt)
            if walls:
                from core.collision import collide_rects
                mtv = collide_rects(self.rect, walls)
                self.rect.y += int(mtv.y)
            self._state = 'walk'
        else:
            self._state = 'idle'

        self._frame = (self._frame + self._frame_speed * dt) % len(self._anims[self._state])
        self.particles.update(dt)

    def draw(self, surface, camera):
        if not self.alive and self._death_timer > 0.6:
            self.particles.draw(surface, camera)
            return
        r = camera.apply(self.rect)
        frame_idx = min(int(self._frame), len(self._anims[self._state]) - 1)
        sprite = self._anims[self._state][frame_idx]
        if self._flash > 0:
            fl = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            fl.fill((255, 255, 255, 180))
            sprite = sprite.copy()
            sprite.blit(fl, (0, 0))
        surface.blit(sprite, r.topleft)

        # Health bar
        if self.alive:
            bw = 44
            bh = 5
            bx = r.centerx - bw//2
            by = r.top - 10
            pygame.draw.rect(surface, (60, 10, 10), (bx, by, bw, bh), border_radius=2)
            fill = int(bw * self.hp / self.max_hp)
            pygame.draw.rect(surface, (200, 40, 40), (bx, by, fill, bh), border_radius=2)

        self.particles.draw(surface, camera)
