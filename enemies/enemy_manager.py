# enemies/enemy_manager.py
import pygame
import random
from enemies.enemy_types import PatrolEnemy, ChaserEnemy, AttackerEnemy
from config.difficulty import DIFFICULTIES, STAGE_SCALE
from config.scoring import SCORING

class EnemyManager:
    def __init__(self, stage: int, difficulty: str, spawn_zones: list,
                 player_start, world_rect: pygame.Rect):
        self.stage       = stage
        self.difficulty  = difficulty
        self.spawn_zones = spawn_zones
        self.player_start= player_start
        self.world_rect  = world_rect
        self.enemies: list = []
        self._kill_count  = 0
        self._kill_cap    = SCORING["enemy_kill_cap"]
        self._enemies_created = 0

        diff  = DIFFICULTIES[difficulty]
        scale = STAGE_SCALE[stage]
        self._count_mult  = diff["enemy_count_mult"]  * scale
        self._speed_mult  = diff["enemy_speed_mult"]  * scale
        self._damage_mult = diff["damage_mult"]

    def _safe_spawn_pos(self, size=(52,64)):
        """Pick random pos inside a random spawn zone, away from player."""
        for _ in range(30):
            zone = random.choice(self.spawn_zones)
            x = random.randint(zone[0], zone[0]+zone[2]-size[0])
            y = random.randint(zone[1], zone[1]+zone[3]-size[1])
            px, py = self.player_start
            if abs(x-px) > 200 or abs(y-py) > 200:
                return x, y
        # fallback
        return self.spawn_zones[0][0], self.spawn_zones[0][1]

    def spawn_wave(self, base_count: int):
        """Spawn a wave of enemies scaled by difficulty + stage."""
        count = max(1, int(base_count * self._count_mult))
        types = [PatrolEnemy, ChaserEnemy, AttackerEnemy]
        # Later stages get more attackers/chasers
        weights = {
            1: [0.5, 0.3, 0.2],
            2: [0.35,0.4, 0.25],
            3: [0.25,0.4, 0.35],
            4: [0.2, 0.4, 0.4],
            5: [0.1, 0.45,0.45],
        }.get(self.stage, [0.33, 0.33, 0.34])

        for _ in range(count):
            EClass = random.choices(types, weights=weights)[0]
            x, y = self._safe_spawn_pos()
            from enemies.enemy import ENEMY_HP_BASE, ENEMY_SPEED_BASE, ENEMY_DMG_BASE
            e = EClass(x, y,
                       hp     = int(ENEMY_HP_BASE * self._count_mult * 0.7),
                       speed  = int(ENEMY_SPEED_BASE * self._speed_mult),
                       damage = int(ENEMY_DMG_BASE * self._damage_mult))
            self.enemies.append(e)
        self._enemies_created += count

    def update(self, dt: float, player, walls: list) -> int:
        """Returns score delta from kills this update."""
        score_delta = 0
        for e in self.enemies:
            if not e.alive:
                e.update(dt, walls)
                continue
            hit_player = e.think(player.rect, dt)
            e.update(dt, walls)

            # Enemy attacks player
            if hit_player:
                player.take_damage(e.damage)

            # Player attack hits enemy
            hitbox = player.attack.get_hitbox(player.rect)
            if hitbox and e.alive and hitbox.colliderect(e.rect):
                from player.player_attack import ATTACK_DAMAGE
                just_died = e.take_damage(ATTACK_DAMAGE)
                if just_died and self._kill_count < self._kill_cap:
                    self._kill_count += 1
                    score_delta += SCORING["enemy_kill_bonus"]

        # Remove fully dead (after death anim)
        self.enemies = [e for e in self.enemies if not (not e.alive and e._death_timer > 1.0)]
        return score_delta

    def draw(self, surface, camera):
        for e in self.enemies:
            e.draw(surface, camera)

    def all_dead(self) -> bool:
        return all(not e.alive for e in self.enemies)

    def living_count(self) -> int:
        return sum(1 for e in self.enemies if e.alive)

    def cleanup(self):
        self.enemies.clear()
