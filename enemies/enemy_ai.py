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
ATTACK_RANGE   = 70
WANDER_SPEED   = 55

class PatrolAI:
    """Patrols between two points. Chases if player enters detect range."""
    def __init__(self, p1, p2):
        self.p1, self.p2 = p1, p2
        self.target = p2
        self.state  = 'patrol'
        self.wander_timer = 0.0

    def update(self, enemy, player_rect, dt):
        px, py = player_rect.centerx, player_rect.centery
        ex, ey = enemy.rect.centerx, enemy.rect.centery
        dist   = distance((ex,ey), (px,py))

        if dist < DETECT_RANGE:
            self.state = 'chase'
        elif self.state == 'chase' and dist > DETECT_RANGE * 1.5:
            self.state = 'patrol'

        if self.state == 'chase':
            dx = px - ex; dy = py - ey
            mag = math.hypot(dx, dy) or 1
            enemy.vel.x = dx/mag * enemy.speed
            enemy.vel.y = dy/mag * enemy.speed
        else:
            tx, ty = self.target
            dx = tx-ex; dy = ty-ey
            mag = math.hypot(dx,dy) or 1
            if mag < 10:
                self.target = self.p2 if self.target == self.p1 else self.p1
            enemy.vel.x = dx/mag * PATROL_SPEED
            enemy.vel.y = dy/mag * PATROL_SPEED

        # Attack
        if dist < ATTACK_RANGE and enemy.can_attack():
            enemy.reset_attack_cd()
            return True  # signal: attack hit
        return False


class ChaserAI:
    """Relentlessly chases the player."""
    def update(self, enemy, player_rect, dt):
        px, py = player_rect.centerx, player_rect.centery
        ex, ey = enemy.rect.centerx, enemy.rect.centery
        dist   = distance((ex,ey),(px,py))
        dx = px-ex; dy = py-ey
        mag = math.hypot(dx,dy) or 1
        enemy.vel.x = dx/mag * enemy.speed
        enemy.vel.y = dy/mag * enemy.speed
        if dist < ATTACK_RANGE and enemy.can_attack():
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
            dx = ex-px; dy = ey-py
            mag = math.hypot(dx,dy) or 1
            enemy.vel.x = dx/mag * ATTACK_SPEED * 0.5
            enemy.vel.y = dy/mag * ATTACK_SPEED * 0.5
            return False

        px, py = player_rect.centerx, player_rect.centery
        ex, ey = enemy.rect.centerx, enemy.rect.centery
        dist   = distance((ex,ey),(px,py))
        dx = px-ex; dy = py-ey
        mag = math.hypot(dx,dy) or 1
        enemy.vel.x = dx/mag * ATTACK_SPEED
        enemy.vel.y = dy/mag * ATTACK_SPEED

        if dist < ATTACK_RANGE and enemy.can_attack():
            enemy.reset_attack_cd()
            self.retreat_timer = 0.5
            return True
        return False
