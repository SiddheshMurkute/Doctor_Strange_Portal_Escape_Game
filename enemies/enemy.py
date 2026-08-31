# enemies/enemy.py
"""
Base enemy class — Doctor Strange: Portal Escape.

Key improvements over prototype:
  - Telegraph state (IDLE / WINDING_UP / ATTACKING / RECOVERING)
  - Velocity-impulse knockback (slides back physically, not instant)
  - Hitflash: white silhouette on hit, red tint on damage
  - Procedural Thanos-army visuals (unchanged visual function)
  - Enemy projectile support for RangedEnemy
"""

import pygame
import math
import random
from effects.particles import ParticleSystem

# ----------------------------------------------------------------
# BASE STATS
# ----------------------------------------------------------------
ENEMY_HP_BASE    = 60
ENEMY_SPEED_BASE = 90   # px/sec
ENEMY_DMG_BASE   = 5
ENEMY_ATTACK_CD  = 1.0  # seconds

# Knockback drag — lower = further slide
KNOCKBACK_DRAG   = 8.0  # multiplied by velocity decay per second

# Telegraph duration
TELEGRAPH_TIME   = 0.35   # seconds before attack releases


# ----------------------------------------------------------------
# PROCEDURAL SPRITE
# ----------------------------------------------------------------

def _draw_enemy_frame(kind: str, frame: int, size=(52, 64)) -> pygame.Surface:
    w, h  = size
    surf  = pygame.Surface(size, pygame.SRCALPHA)

    body_col  = {'patrol': (60, 30, 90),  'chaser': (80, 20, 20),
                 'attacker': (40, 60, 20), 'ranged': (20, 50, 80),
                 'elite': (90, 10, 80)}.get(kind, (60, 30, 90))
    armor_col = {'patrol': (130, 80, 180), 'chaser': (180, 50, 50),
                 'attacker': (80, 150, 40), 'ranged': (40, 120, 200),
                 'elite': (220, 40, 200)}.get(kind, (130, 80, 180))
    eye_col   = (255, 50, 0)

    leg_off = int(math.sin(frame * 1.4) * 4)
    pygame.draw.rect(surf, body_col, (w//2-10, h//2+10, 8, 16 + leg_off), border_radius=3)
    pygame.draw.rect(surf, body_col, (w//2+2,  h//2+10, 8, 16 - leg_off), border_radius=3)

    pygame.draw.rect(surf, body_col,  (w//2-13, h//2-10, 26, 22), border_radius=4)
    pygame.draw.polygon(surf, armor_col, [
        (w//2-13, h//2-10), (w//2+13, h//2-10),
        (w//2+10, h//2+5),  (w//2-10, h//2+5),
    ])

    arm_swing = int(math.sin(frame * 1.4) * 5)
    pygame.draw.line(surf, body_col, (w//2-13, h//2-4), (w//2-22, h//2+10+arm_swing), 5)
    pygame.draw.line(surf, body_col, (w//2+13, h//2-4), (w//2+22, h//2+10-arm_swing), 5)
    fist_col = armor_col
    pygame.draw.circle(surf, fist_col, (w//2-22, h//2+14+arm_swing), 5)
    pygame.draw.circle(surf, fist_col, (w//2+22, h//2+14-arm_swing), 5)

    head_y = h//2 - 26
    pygame.draw.ellipse(surf, body_col,  (w//2-10, head_y, 20, 20))
    pygame.draw.arc(surf, armor_col,     (w//2-11, head_y-2, 22, 14), 0, math.pi, 5)
    pygame.draw.circle(surf, eye_col,    (w//2-4, head_y+10), 3)
    pygame.draw.circle(surf, eye_col,    (w//2+4, head_y+10), 3)

    # Elite gets extra shoulder spikes
    if kind == 'elite':
        pygame.draw.polygon(surf, armor_col, [
            (w//2-13, h//2-10), (w//2-20, h//2-20), (w//2-8, h//2-8)
        ])
        pygame.draw.polygon(surf, armor_col, [
            (w//2+13, h//2-10), (w//2+20, h//2-20), (w//2+8, h//2-8)
        ])

    # Ranged gets an orb in hand
    if kind == 'ranged':
        pygame.draw.circle(surf, (80, 180, 255), (w//2+22, h//2+10-arm_swing), 6)

    return surf


def build_enemy_animations(kind: str, size=(52, 64)) -> dict:
    states = {'walk': 8, 'attack': 6, 'death': 6, 'idle': 6}
    return {s: [_draw_enemy_frame(kind, f, size) for f in range(n)]
            for s, n in states.items()}


# ----------------------------------------------------------------
# ENEMY PROJECTILE (fired by RangedEnemy)
# ----------------------------------------------------------------

class EnemyProjectile:
    """Simple slow-moving enemy bolt."""
    RADIUS   = 6
    SPEED    = 220
    LIFETIME = 3.0
    DAMAGE   = 5

    def __init__(self, x: float, y: float, angle: float, damage: int = None):
        self.x       = x
        self.y       = y
        self.vx      = math.cos(angle) * self.SPEED
        self.vy      = math.sin(angle) * self.SPEED
        self.life    = self.LIFETIME
        self.alive   = True
        self.damage  = damage or self.DAMAGE
        self._color  = (255, 80, 20)

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt

    @property
    def rect(self) -> pygame.Rect:
        r = self.RADIUS
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.alive:
            return
        sx, sy = camera.apply_point((self.x, self.y))
        # Glow
        gs = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*self._color, 60), (12, 12), 12)
        surface.blit(gs, (sx - 12, sy - 12), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.circle(surface, self._color,      (sx, sy), self.RADIUS)
        pygame.draw.circle(surface, (255, 200, 100),  (sx, sy), max(2, self.RADIUS - 3))


# ----------------------------------------------------------------
# BASE ENEMY
# ----------------------------------------------------------------

class Enemy:

    # Telegraph states
    TELE_IDLE      = "idle"
    TELE_WINDUP    = "windup"    # bright warning ring
    TELE_ATTACK    = "attack"
    TELE_RECOVER   = "recover"

    def __init__(self, x, y, kind='patrol', hp=None, speed=None, damage=None):
        self.kind     = kind
        self.rect     = pygame.Rect(x, y, 52, 64)
        self.hp       = hp    or ENEMY_HP_BASE
        self.max_hp   = self.hp
        self.speed    = speed or ENEMY_SPEED_BASE
        self.damage   = damage or ENEMY_DMG_BASE
        self.alive    = True

        self._anims        = build_enemy_animations(kind, (52, 64))
        self._state        = 'idle'
        self._frame        = 0.0
        self._frame_speed  = 8.0

        self._attack_cd    = 0.0
        self._flash        = 0.0   # white silhouette duration
        self._death_timer  = 0.0

        self.particles     = ParticleSystem()

        # Velocity (float, used for knockback impulse)
        self.vel           = pygame.Vector2(0.0, 0.0)
        self._kb_vel       = pygame.Vector2(0.0, 0.0)   # knockback impulse

        # Telegraph
        self._tele_state   = self.TELE_IDLE
        self._tele_timer   = 0.0
        self._attacked_this_tele = False

        # Stagger (used by Reality Break)
        self._stagger_timer = 0.0

    # ----------------------------------------------------------
    # HIT / DEATH
    # ----------------------------------------------------------

    def take_damage(self, amount: int) -> bool:
        if not self.alive:
            return False
        self.hp   -= amount
        self._flash = 0.20
        self.particles.emit(
            self.rect.centerx, self.rect.centery,
            8, (255, 150, 0), speed_range=(2, 5), life_range=(0.1, 0.3)
        )
        if self.hp <= 0:
            self.alive         = False
            self._state        = 'death'
            self._frame        = 0.0
            self._tele_state   = self.TELE_IDLE
            self.particles.emit(
                self.rect.centerx, self.rect.centery,
                22, (200, 80, 20), speed_range=(2, 7), life_range=(0.3, 0.8)
            )
            return True   # just died
        return False

    # ----------------------------------------------------------
    # KNOCKBACK — velocity impulse (slides, not teleports)
    # ----------------------------------------------------------

    def knockback_impulse(self, angle: float, force: float = 180.0) -> None:
        """Apply velocity impulse away from attack direction."""
        self._kb_vel.x = math.cos(angle) * force
        self._kb_vel.y = math.sin(angle) * force

    def knockback(self, angle: float, distance: float = 70.0) -> None:
        """Legacy instant knockback shim (converted to impulse)."""
        self.knockback_impulse(angle, force=distance * 2.5)

    # ----------------------------------------------------------
    # TELEGRAPH
    # ----------------------------------------------------------

    def begin_telegraph(self) -> None:
        self._tele_state = self.TELE_WINDUP
        self._tele_timer = TELEGRAPH_TIME
        self._attacked_this_tele = False

    def telegraph_done(self) -> bool:
        """Returns True when telegraph winds-up and attack should fire."""
        if self._tele_state == self.TELE_WINDUP and self._tele_timer <= 0:
            self._tele_state = self.TELE_ATTACK
            return True
        return False

    def stagger(self, duration: float = 1.2) -> None:
        """Stagger (from Reality Break)."""
        self._stagger_timer = duration
        self._kb_vel *= 0.2   # kill knockback

    # ----------------------------------------------------------
    # ATTACK CD
    # ----------------------------------------------------------

    def can_attack(self) -> bool:
        return self._attack_cd <= 0 and self._stagger_timer <= 0

    def reset_attack_cd(self) -> None:
        self._attack_cd = ENEMY_ATTACK_CD

    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------

    def update(self, dt: float, walls=None) -> None:
        if self._attack_cd > 0:
            self._attack_cd -= dt
        if self._flash > 0:
            self._flash -= dt
        if self._stagger_timer > 0:
            self._stagger_timer = max(0.0, self._stagger_timer - dt)

        # Telegraph timer
        if self._tele_state == self.TELE_WINDUP:
            self._tele_timer -= dt
            if self._tele_timer <= 0:
                self._tele_timer = 0.0

        if not self.alive:
            self._death_timer += dt
            self._frame = min(
                self._frame + self._frame_speed * dt,
                len(self._anims['death']) - 1
            )
            self.particles.update(dt)
            return

        # Stagger: slow movement
        if self._stagger_timer > 0:
            self.vel *= 0.0   # freeze AI movement during stagger

        # Knockback velocity drag
        if self._kb_vel.length() > 1.0:
            self._kb_vel -= self._kb_vel * min(1.0, KNOCKBACK_DRAG * dt)
        else:
            self._kb_vel = pygame.Vector2(0.0, 0.0)

        # Move from AI vel + knockback
        total_vel = self.vel + self._kb_vel

        if total_vel.length() > 0:
            self.rect.x += int(total_vel.x * dt)
            if walls:
                from core.collision import collide_rects
                mtv = collide_rects(self.rect, walls)
                self.rect.x += int(mtv.x)
            self.rect.y += int(total_vel.y * dt)
            if walls:
                from core.collision import collide_rects
                mtv = collide_rects(self.rect, walls)
                self.rect.y += int(mtv.y)
            self._state = 'walk'
        else:
            self._state = 'idle'

        self._frame = (
            self._frame + self._frame_speed * dt
        ) % len(self._anims[self._state])

        self.particles.update(dt)

    # ----------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.alive and self._death_timer > 0.6:
            self.particles.draw(surface, camera)
            return

        r         = camera.apply(self.rect)
        frame_idx = min(int(self._frame), len(self._anims[self._state]) - 1)
        sprite    = self._anims[self._state][frame_idx]

        if self._flash > 0:
            wf = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            wf.fill((255, 255, 255, 200))
            sprite = sprite.copy()
            sprite.blit(wf, (0, 0))

        surface.blit(sprite, r.topleft)

        # Telegraph warning ring
        if self._tele_state == self.TELE_WINDUP and self.alive:
            frac   = 1.0 - (self._tele_timer / TELEGRAPH_TIME) if TELEGRAPH_TIME > 0 else 1.0
            alpha  = int(160 + 90 * frac)
            ring_r = 28 + int(12 * frac)
            ts     = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(ts, (255, 60, 0, min(255, alpha)),
                                (2, 2, ring_r * 2, ring_r * 2), 4)
            cx = r.centerx - ring_r - 2
            cy = r.centery - ring_r - 2
            surface.blit(ts, (cx, cy), special_flags=pygame.BLEND_RGBA_ADD)

        # Health bar
        if self.alive:
            bw = 44; bh = 5
            bx = r.centerx - bw // 2
            by = r.top - 10
            pygame.draw.rect(surface, (60, 10, 10), (bx, by, bw, bh), border_radius=2)
            fill = max(0, int(bw * self.hp / self.max_hp))
            pygame.draw.rect(surface, (200, 40, 40), (bx, by, fill, bh), border_radius=2)

        self.particles.draw(surface, camera)
