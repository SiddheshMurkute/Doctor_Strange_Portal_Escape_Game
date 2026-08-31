# enemies/enemy_manager.py
"""
Enemy manager — Doctor Strange: Portal Escape.

New features:
  - Uses attack.collect_hits() for projectile bolt collision
  - Triggers hitstop on hit / kill
  - Applies velocity-impulse knockback (not instant offset)
  - Tracks enemy projectiles and checks them against player
  - Encounter beat system: Beat1 → Lull → Beat2 → Elite
"""

import pygame
import math
import random

from enemies.enemy_types import (
    PatrolEnemy, ChaserEnemy, AttackerEnemy, RangedEnemy, EliteEnemy
)
from core.hitstop import hitstop, HitstopDuration
from effects.screen_shake import ScreenShake


# Map kind strings to classes
ENEMY_CLASSES = {
    'patrol':   PatrolEnemy,
    'chaser':   ChaserEnemy,
    'attacker': AttackerEnemy,
    'ranged':   RangedEnemy,
    'elite':    EliteEnemy,
}


class EnemyManager:

    def __init__(self, stage_config: dict, difficulty_mult: float = 1.0):
        self.stage_config    = stage_config
        self.difficulty_mult = difficulty_mult
        self.enemies: list   = []
        self._dead_pool: list = []   # brief death-animation enemies

        # Encounter beat timer
        self._encounter_timer  = 0.0
        self._beat_index       = 0
        self._encounter_active = False

        # Score callback (set externally by game)
        self.on_kill_callback = None

    # ----------------------------------------------------------
    # SPAWN
    # ----------------------------------------------------------

    def spawn_wave(self, zone_rects=None, stage_num: int = 1,
                   num_enemies: int = None) -> None:
        """Spawn a wave of enemies.
        zone_rects: list of pygame.Rect or (x,y,w,h) tuples, OR legacy int (num enemies).
        """
        cfg = self.stage_config

        # --- Legacy compat: spawn_wave(int) ---
        if isinstance(zone_rects, int):
            num_enemies = num_enemies or zone_rects
            zone_rects  = cfg.get('enemy_spawn_zones', [])

        if zone_rects is None:
            zone_rects = cfg.get('enemy_spawn_zones', [])

        base_count  = num_enemies or cfg.get('enemy_count', cfg.get('base_enemy_count', 4))
        count       = max(1, int(base_count * self.difficulty_mult))
        enemy_types = cfg.get('enemy_types', ['patrol', 'chaser'])

        for _ in range(count):
            raw_zone = random.choice(zone_rects) if zone_rects else None
            if raw_zone is not None:
                zone = raw_zone if isinstance(raw_zone, pygame.Rect) else pygame.Rect(raw_zone)
                x = random.randint(zone.left + 20, max(zone.left + 21, zone.right  - 70))
                y = random.randint(zone.top  + 20, max(zone.top  + 21, zone.bottom - 80))
            else:
                x, y = 200, 200

            kind  = random.choice(enemy_types)
            cls   = ENEMY_CLASSES.get(kind, PatrolEnemy)
            hp    = int(cfg.get('enemy_hp',    60)  * self.difficulty_mult)
            spd   = int(cfg.get('enemy_speed', 90)  * min(1.3, self.difficulty_mult))
            dmg   = int(cfg.get('enemy_damage', 5)  * self.difficulty_mult)
            enemy = cls(x, y, hp=hp, speed=spd, damage=dmg)
            self.enemies.append(enemy)

    def spawn_elite(self, zone_rects: list) -> None:
        zone = random.choice(zone_rects) if zone_rects else None
        if zone:
            x = random.randint(zone.left + 20, zone.right - 80)
            y = random.randint(zone.top  + 20, zone.bottom - 90)
        else:
            x, y = 300, 300
        hp  = int(140 * self.difficulty_mult)
        spd = int(100 * min(1.2, self.difficulty_mult))
        self.enemies.append(EliteEnemy(x, y, hp=hp, speed=spd))

    def clear(self) -> None:
        self.enemies = []
        self._dead_pool = []

    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------

    def update(self, dt: float, player, walls: list,
               shake: ScreenShake = None) -> list:
        """
        Update all enemies and run hit detection.
        Returns list of kill events: [{'enemy': enemy, 'pos': (x, y)}, ...]
        """
        kill_events = []

        alive = []
        for enemy in self.enemies:
            if not enemy.alive:
                self._dead_pool.append(enemy)
                continue
            alive.append(enemy)
        self.enemies = alive

        # --- AI think + melee damage to player ---
        for enemy in self.enemies:
            hit_player = enemy.think(player.rect, dt)
            if hit_player is True:
                if player.take_damage(enemy.damage):
                    if shake:
                        shake.add_trauma(0.25)
                    hitstop.trigger(HitstopDuration.HEAVY)

            enemy.update(dt, walls)

        # ---- Player BOLT hits on enemies ----
        hits = []
        if hasattr(player, 'attack') and hasattr(player.attack, 'collect_hits'):
            hits = player.attack.collect_hits(self.enemies)

        for bolt, enemy, angle in hits:
            dmg  = player.attack.damage

            # Momentum-based damage bonus
            bonus = player.momentum.bonuses.get("cast_rate", 1.0) - 1.0
            dmg   = int(dmg + dmg * bonus * 0.3)

            just_died = enemy.take_damage(dmg)
            # Knockback impulse away from bolt travel
            enemy.knockback_impulse(angle, force=200.0)

            player.momentum.on_attack_hit()

            if just_died:
                # Kill hitstop + shake
                hitstop.trigger(HitstopDuration.KILL)
                if shake:
                    shake.add_trauma(0.12)
                player.momentum.on_kill()
                kill_events.append({'enemy': enemy, 'pos': (enemy.rect.centerx, enemy.rect.centery)})
                if self.on_kill_callback:
                    self.on_kill_callback(enemy)
            else:
                # Light hit feedback
                hitstop.trigger(HitstopDuration.LIGHT)
                if shake:
                    shake.add_trauma(0.06)

        # ---- Enemy PROJECTILES hitting player ----
        for enemy in self.enemies:
            if not isinstance(enemy, RangedEnemy):
                continue
            for proj in enemy.get_projectiles():
                if proj.alive and proj.rect.colliderect(player.rect):
                    proj.alive = False
                    if player.take_damage(proj.damage):
                        if shake:
                            shake.add_trauma(0.20)
                        hitstop.trigger(HitstopDuration.HEAVY)

        # --- Reality Break stagger ---
        if hasattr(player, '_rb_active') and player._rb_active:
            for enemy in self.enemies:
                dist = math.hypot(
                    enemy.rect.centerx - player.rect.centerx,
                    enemy.rect.centery - player.rect.centery,
                )
                if dist < 400:
                    enemy.stagger(1.4)

        # --- Dead pool (finish death animation) ---
        alive_dead = []
        for e in self._dead_pool:
            e.update(dt, walls)
            if e._death_timer < 0.8:
                alive_dead.append(e)
        self._dead_pool = alive_dead

        return kill_events

    # ----------------------------------------------------------
    # DRAW
    # ----------------------------------------------------------

    def draw(self, surface: pygame.Surface, camera) -> None:
        for e in self._dead_pool:
            e.draw(surface, camera)
        for e in self.enemies:
            e.draw(surface, camera)

    # ----------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------

    @property
    def alive_count(self) -> int:
        return len(self.enemies)

    @property
    def all_dead(self) -> bool:
        return len(self.enemies) == 0

    def reality_break_active(self, player) -> bool:
        return getattr(player, '_rb_active', False)
