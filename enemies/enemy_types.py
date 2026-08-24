# enemies/enemy_types.py
"""Concrete enemy subclasses with AI wired in."""
import pygame
import random
from enemies.enemy import Enemy
from enemies.enemy_ai import PatrolAI, ChaserAI, AttackerAI


class PatrolEnemy(Enemy):
    def __init__(self, x, y, hp=None, speed=None, damage=None):
        super().__init__(x, y, 'patrol', hp, speed, damage)
        # Patrol between start and a random offset
        p2 = (x + random.choice([-1, 1]) * random.randint(120, 280),
              y + random.choice([-1, 1]) * random.randint(80, 200))
        self.ai = PatrolAI((x, y), p2)

    def think(self, player_rect, dt):
        return self.ai.update(self, player_rect, dt)


class ChaserEnemy(Enemy):
    def __init__(self, x, y, hp=None, speed=None, damage=None):
        super().__init__(x, y, 'chaser', hp, speed, damage)
        self.ai = ChaserAI()

    def think(self, player_rect, dt):
        return self.ai.update(self, player_rect, dt)


class AttackerEnemy(Enemy):
    def __init__(self, x, y, hp=None, speed=None, damage=None):
        super().__init__(x, y, 'attacker', hp, speed, damage)
        self.ai = AttackerAI()

    def think(self, player_rect, dt):
        return self.ai.update(self, player_rect, dt)
