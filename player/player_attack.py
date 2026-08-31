# player/player_attack.py
"""
Doctor Strange — Bolts of Balthakk (Mystic Flame)

Architecture
------------
BoltProjectile   — a single flying projectile
BoltsOfBalthakk  — manages projectile list, cooldown, firing
MysticFlame      — alias kept for backward compatibility

Firing is separated from input:
    player.handle_input() detects fire request → calls attack.try_fire()
    attack.update(dt)     advances all bolts and cooldown
    attack.collect_hits() returns (enemy_rect hits) to enemy_manager

Mouse-aim is used when possible; falls back to _facing direction.
"""

import pygame
import math
import random


# ============================================================
# SETTINGS  — all tweak here, nowhere else
# ============================================================

BOLT_SPEED       = 640      # px/s
BOLT_COOLDOWN    = 0.28    # seconds between shots
BOLT_DAMAGE      = 30
BOLT_LIFETIME    = 1.8     # seconds before despawn
BOLT_RADIUS      = 7       # collision/draw radius
BOLT_TRAIL_LEN   = 12      # trail history points

# Direction map for keyboard-only fallback
_DIR_MAP = {
    "right": ( 1.0,  0.0),
    "left":  (-1.0,  0.0),
    "up":    ( 0.0, -1.0),
    "down":  ( 0.0,  1.0),
}


# ============================================================
# BOLT PROJECTILE
# ============================================================

class BoltProjectile:
    """A single magical bolt."""

    __slots__ = (
        "x", "y", "vx", "vy", "life", "alive",
        "trail", "_trail_timer", "angle"
    )

    def __init__(self, x: float, y: float, angle: float):
        self.x     = x
        self.y     = y
        self.vx    = math.cos(angle) * BOLT_SPEED
        self.vy    = math.sin(angle) * BOLT_SPEED
        self.life  = BOLT_LIFETIME
        self.alive = True
        self.angle = angle
        self.trail: list[tuple[float, float]] = []
        self._trail_timer = 0.0

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Trail
        self._trail_timer += dt
        if self._trail_timer >= 0.018:
            self._trail_timer = 0.0
            self.trail.append((self.x, self.y))
            if len(self.trail) > BOLT_TRAIL_LEN:
                self.trail.pop(0)

    @property
    def rect(self) -> pygame.Rect:
        r = BOLT_RADIUS
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.alive:
            return
        # Trail
        trail_len = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            sx, sy = camera.apply_point((tx, ty))
            alpha  = int(220 * (i / max(trail_len, 1)))
            radius = max(1, int(BOLT_RADIUS * 0.55 * (i / max(trail_len, 1))))
            ts = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (255, 180, 40, alpha), (radius, radius), radius)
            surface.blit(ts, (sx - radius, sy - radius),
                         special_flags=pygame.BLEND_RGBA_ADD)

        # Core bolt
        sx, sy = camera.apply_point((self.x, self.y))
        # Outer glow
        glow_r = BOLT_RADIUS + 5
        gs = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (255, 160, 0, 90), (glow_r, glow_r), glow_r)
        surface.blit(gs, (sx - glow_r, sy - glow_r),
                     special_flags=pygame.BLEND_RGBA_ADD)
        # Core
        pygame.draw.circle(surface, (255, 230, 100), (sx, sy), BOLT_RADIUS)
        pygame.draw.circle(surface, (255, 255, 255), (sx, sy), max(2, BOLT_RADIUS - 3))


# ============================================================
# BOLTS OF BALTHAKK
# ============================================================

class BoltsOfBalthakk:
    """
    Manages active bolt projectiles, cooldown, and firing.

    Interaction model:
        try_fire(origin, angle)  — called from player input
        update(dt)               — advances all bolts + cooldown
        collect_hits(enemies)    — tests collision, returns hit list
        draw(surface, camera)    — renders all bolts
    """

    def __init__(self):
        self.damage: int              = BOLT_DAMAGE
        self.cooldown: float          = BOLT_COOLDOWN
        self._cooling: float          = 0.0
        self._bolts: list[BoltProjectile] = []
        # Legacy compat
        self.active: bool             = False
        self.angle: float             = 0.0

    # ----------------------------------------------------------
    # FIRE
    # ----------------------------------------------------------

    def try_fire(self, origin: tuple[float, float], angle: float) -> bool:
        """
        Attempt to fire a bolt.
        Returns True if fired, False if on cooldown.
        origin: world-space (x, y) of the bolt spawn point.
        """
        if self._cooling > 0:
            return False
        bolt = BoltProjectile(origin[0], origin[1], angle)
        self._bolts.append(bolt)
        self._cooling = self.cooldown
        self.active   = True
        self.angle    = angle   # for legacy hitbox compat
        return True

    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------

    def update(self, dt: float, player_rect: pygame.Rect = None) -> None:
        if self._cooling > 0:
            self._cooling = max(0.0, self._cooling - dt)

        for bolt in self._bolts:
            bolt.update(dt)

        # Remove dead bolts
        self._bolts = [b for b in self._bolts if b.alive]
        self.active  = len(self._bolts) > 0

    # ----------------------------------------------------------
    # HIT DETECTION (called by enemy_manager)
    # ----------------------------------------------------------

    def collect_hits(self, enemies: list) -> list[tuple]:
        """
        Check all bolts against enemy list.
        Returns list of (bolt, enemy, angle) tuples for hits.
        Each bolt can only hit one enemy per frame; on hit it despawns.
        """
        hits = []
        for bolt in self._bolts:
            if not bolt.alive:
                continue
            for enemy in enemies:
                if not enemy.alive:
                    continue
                if bolt.rect.colliderect(enemy.rect):
                    bolt.alive = False
                    hits.append((bolt, enemy, bolt.angle))
                    break   # bolt is consumed
        return hits

    # ----------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------

    def draw(self, surface: pygame.Surface, camera=None) -> None:
        for bolt in self._bolts:
            bolt.draw(surface, camera)

    # ----------------------------------------------------------
    # LEGACY COMPAT
    # ----------------------------------------------------------

    @property
    def cooldown_pct(self) -> float:
        if self.cooldown <= 0:
            return 0.0
        return max(0.0, min(1.0, self._cooling / self.cooldown))

    def get_hitbox(self, player_rect: pygame.Rect) -> pygame.Rect:
        """Legacy: returns union rect of all active bolts (for old enemy_manager code)."""
        if not self._bolts:
            return pygame.Rect(0, 0, 0, 0)
        # Return first alive bolt rect as best approximation
        for bolt in self._bolts:
            if bolt.alive:
                return bolt.rect
        return pygame.Rect(0, 0, 0, 0)

    def try_attack(self, player_rect: pygame.Rect,
                   facing: str = "right", keys=None) -> bool:
        """Legacy shim used by old player.handle_input."""
        dx, dy = _DIR_MAP.get(facing, (1.0, 0.0))
        origin = (float(player_rect.centerx), float(player_rect.centery))
        return self.try_fire(origin, math.atan2(dy, dx))

    def start(self) -> bool:
        return False   # Not applicable for ranged


# ============================================================
# ALIAS — backward compat
# ============================================================

class MysticFlame(BoltsOfBalthakk):
    """Alias so existing code using MysticFlame() still works."""
    pass


class PlayerAttack(BoltsOfBalthakk):
    """Alias."""
    pass