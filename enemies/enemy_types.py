# enemies/enemy_types.py
"""Concrete enemy subclasses with AI wired in."""
import pygame
import random
from enemies.enemy import Enemy, EnemyProjectile
from enemies.enemy_ai import PatrolAI, ChaserAI, AttackerAI, RangedAI, EliteAI


class PatrolEnemy(Enemy):
    def __init__(self, x, y, hp=None, speed=None, damage=None):
        super().__init__(x, y, 'patrol', hp, speed, damage)
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


class RangedEnemy(Enemy):
    """Fires projectiles at player from a distance."""

    def __init__(self, x, y, hp=None, speed=None, damage=None):
        super().__init__(x, y, 'ranged', hp, speed, damage)
        self.ai            = RangedAI()
        self._projectiles: list[EnemyProjectile] = []

    def think(self, player_rect, dt):
        result = self.ai.update(self, player_rect, dt)
        if isinstance(result, tuple) and result[0] == "fire":
            angle = result[1]
            proj  = EnemyProjectile(
                self.rect.centerx, self.rect.centery,
                angle, self.damage
            )
            self._projectiles.append(proj)
        return False   # melee attack never fires for ranged

    def update(self, dt, walls=None):
        super().update(dt, walls)
        for p in self._projectiles:
            p.update(dt)
        self._projectiles = [p for p in self._projectiles if p.alive]

    def draw(self, surface, camera):
        super().draw(surface, camera)
        for p in self._projectiles:
            p.draw(surface, camera)

    def get_projectiles(self) -> list:
        return self._projectiles


class EliteEnemy(Enemy):
    """Larger, more HP, slam attack."""

    def __init__(self, x, y, hp=None, speed=None, damage=None):
        # Elites are bigger
        super().__init__(x, y, 'elite',
                         hp=hp or 140,
                         speed=speed or 100,
                         damage=damage or 8)
        self.rect  = pygame.Rect(x, y, 64, 80)
        self._anims = None
        from enemies.enemy import build_enemy_animations
        self._anims = build_enemy_animations('elite', (64, 80))
        self.ai    = EliteAI()

    def think(self, player_rect, dt):
        return self.ai.update(self, player_rect, dt)
