# enemies/enemy_ai.py
"""AI behavior state machines for enemy types."""
import pygame
import math
import random
from core.collision import distance

PATROL_SPEED   = 75
CHASE_SPEED    = 130
ATTACK_SPEED   = 110
DETECT_RANGE   = 320
ATTACK_RANGE   = 68
RANGED_MIN     = 160   # ranged enemy preferred distance
RANGED_MAX     = 280
WANDER_SPEED   = 55


class PatrolAI:
    """Patrols between two points. Chases if player enters detect range."""

    def __init__(self, p1, p2):
        self.p1, self.p2 = p1, p2
        self.target = p2
        self.state  = 'patrol'

    def update(self, enemy, player_rect, dt):
        px, py = player_rect.centerx, player_rect.centery
        ex, ey = enemy.rect.centerx, enemy.rect.centery
        dist   = distance((ex, ey), (px, py))

        if dist < DETECT_RANGE:
            self.state = 'chase'
        elif self.state == 'chase' and dist > DETECT_RANGE * 1.5:
            self.state = 'patrol'

        if self.state == 'chase':
            dx = px - ex; dy = py - ey
            mag = math.hypot(dx, dy) or 1
            enemy.vel.x = dx / mag * enemy.speed
            enemy.vel.y = dy / mag * enemy.speed
        else:
            tx, ty = self.target
            dx = tx - ex; dy = ty - ey
            mag = math.hypot(dx, dy) or 1
            if mag < 10:
                self.target = self.p2 if self.target == self.p1 else self.p1
            enemy.vel.x = dx / mag * PATROL_SPEED
            enemy.vel.y = dy / mag * PATROL_SPEED

        # Attack with telegraph
        if dist < ATTACK_RANGE and enemy.can_attack():
            if enemy._tele_state == enemy.TELE_IDLE:
                enemy.begin_telegraph()
            if enemy.telegraph_done():
                enemy.reset_attack_cd()
                return True
        elif enemy._tele_state == enemy.TELE_WINDUP and dist > ATTACK_RANGE * 1.5:
            enemy._tele_state = enemy.TELE_IDLE  # player escaped

        return False


class ChaserAI:
    """Relentlessly chases the player."""

    def update(self, enemy, player_rect, dt):
        px, py = player_rect.centerx, player_rect.centery
        ex, ey = enemy.rect.centerx, enemy.rect.centery
        dist   = distance((ex, ey), (px, py))
        dx = px - ex; dy = py - ey
        mag = math.hypot(dx, dy) or 1
        enemy.vel.x = dx / mag * enemy.speed
        enemy.vel.y = dy / mag * enemy.speed

        if dist < ATTACK_RANGE and enemy.can_attack():
            if enemy._tele_state == enemy.TELE_IDLE:
                enemy.begin_telegraph()
            if enemy.telegraph_done():
                enemy.reset_attack_cd()
                return True
        return False


class AttackerAI:
    """Charges at player, attacks, retreats briefly."""

    def __init__(self):
        self.retreat_timer = 0.0

    def update(self, enemy, player_rect, dt):
        if self.retreat_timer > 0:
            self.retreat_timer -= dt
            px, py = player_rect.centerx, player_rect.centery
            ex, ey = enemy.rect.centerx, enemy.rect.centery
            dx = ex - px; dy = ey - py
            mag = math.hypot(dx, dy) or 1
            enemy.vel.x = dx / mag * ATTACK_SPEED * 0.4
            enemy.vel.y = dy / mag * ATTACK_SPEED * 0.4
            return False

        px, py = player_rect.centerx, player_rect.centery
        ex, ey = enemy.rect.centerx, enemy.rect.centery
        dist   = distance((ex, ey), (px, py))
        dx = px - ex; dy = py - ey
        mag = math.hypot(dx, dy) or 1
        enemy.vel.x = dx / mag * ATTACK_SPEED
        enemy.vel.y = dy / mag * ATTACK_SPEED

        if dist < ATTACK_RANGE and enemy.can_attack():
            if enemy._tele_state == enemy.TELE_IDLE:
                enemy.begin_telegraph()
            if enemy.telegraph_done():
                enemy.reset_attack_cd()
                self.retreat_timer = 0.6
                return True
        return False


class RangedAI:
    """Maintains safe distance and fires projectiles."""

    def __init__(self):
        self._fire_cd = 0.0
        self.FIRE_INTERVAL = 2.0

    def update(self, enemy, player_rect, dt):
        self._fire_cd = max(0.0, self._fire_cd - dt)

        px, py = player_rect.centerx, player_rect.centery
        ex, ey = enemy.rect.centerx, enemy.rect.centery
        dist   = distance((ex, ey), (px, py))
        dx = px - ex; dy = py - ey
        mag = math.hypot(dx, dy) or 1

        # Strafe / maintain distance
        if dist < RANGED_MIN:
            # Retreat
            enemy.vel.x = -(dx / mag) * enemy.speed * 0.8
            enemy.vel.y = -(dy / mag) * enemy.speed * 0.8
        elif dist > RANGED_MAX:
            # Approach
            enemy.vel.x = (dx / mag) * enemy.speed * 0.7
            enemy.vel.y = (dy / mag) * enemy.speed * 0.7
        else:
            # Strafe perpendicular
            perp_x = -dy / mag
            perp_y =  dx / mag
            enemy.vel.x = perp_x * enemy.speed * 0.5
            enemy.vel.y = perp_y * enemy.speed * 0.5

        # Fire condition
        if dist < RANGED_MAX * 1.3 and self._fire_cd <= 0 and enemy.can_attack():
            angle = math.atan2(dy, dx)
            if enemy._tele_state == enemy.TELE_IDLE:
                enemy.begin_telegraph()
            if enemy.telegraph_done():
                enemy.reset_attack_cd()
                self._fire_cd = self.FIRE_INTERVAL
                return ("fire", angle)  # signal to enemy: fire projectile

        return False


class EliteAI:
    """Aggressive chaser with slam telegraph."""

    def __init__(self):
        self.phase = "chase"
        self.charge_timer = 0.0

    def update(self, enemy, player_rect, dt):
        px, py = player_rect.centerx, player_rect.centery
        ex, ey = enemy.rect.centerx, enemy.rect.centery
        dist   = distance((ex, ey), (px, py))
        dx = px - ex; dy = py - ey
        mag = math.hypot(dx, dy) or 1

        if self.phase == "chase":
            enemy.vel.x = dx / mag * enemy.speed
            enemy.vel.y = dy / mag * enemy.speed
            if dist < ATTACK_RANGE * 1.5 and enemy.can_attack():
                if enemy._tele_state == enemy.TELE_IDLE:
                    enemy.begin_telegraph()
                if enemy.telegraph_done():
                    self.phase        = "slam"
                    self.charge_timer = 0.2
                    enemy.reset_attack_cd()
                    return True

        elif self.phase == "slam":
            # Brief heavy charge
            enemy.vel.x = dx / mag * enemy.speed * 3.0
            enemy.vel.y = dy / mag * enemy.speed * 3.0
            self.charge_timer -= dt
            if self.charge_timer <= 0:
                self.phase = "chase"

        return False
