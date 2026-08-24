# player/player.py
import pygame
import math
from config.controls import *
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from player.player_animation import build_animations
from player.player_attack import MysticFlame
from core.collision import collide_rects
from effects.particles import ParticleSystem

PLAYER_SPEED   = 220   # pixels per second
PLAYER_HP      = 100
IFRAMES        = 0.6   # invulnerability seconds after being hit
DAMAGE_PER_HIT = 5     # configurable base (difficulty can multiply)

class Player:
    def __init__(self, x: int, y: int):
        self.SIZE = (64, 80)
        self.rect = pygame.Rect(x, y, self.SIZE[0], self.SIZE[1])
        self.vel  = pygame.Vector2(0, 0)

        # Health
        self.hp       = PLAYER_HP
        self.max_hp   = PLAYER_HP
        self.alive    = True
        self.iframes  = 0.0      # invulnerability timer

        # Animation
        self._anims    = build_animations(self.SIZE)
        self._state    = 'idle'
        self._frame    = 0.0
        self._frame_spd= 6.0     # frames per second
        self._facing   = 'right'

        # Attack
        self.attack    = MysticFlame()

        # Particles (on damage)
        self._particles = ParticleSystem()

        # Flash on damage
        self._flash    = 0.0

        # Fragment count collected this stage
        self.fragments_collected = 0

    # ------------------------------------------------------------------ INPUT
    def handle_input(self, keys, dt: float):
        if not self.alive:
            return

        dx, dy = 0.0, 0.0
        if any(keys[k] for k in MOVE_LEFT):
            dx -= 1; self._facing = 'left'
        if any(keys[k] for k in MOVE_RIGHT):
            dx += 1; self._facing = 'right'
        if any(keys[k] for k in MOVE_UP):
            dy -= 1; self._facing = 'up'
        if any(keys[k] for k in MOVE_DOWN):
            dy += 1; self._facing = 'down'

        # Normalise
        if dx != 0 and dy != 0:
            mag = math.sqrt(2)
            dx /= mag; dy /= mag

        self.vel.x = dx * PLAYER_SPEED
        self.vel.y = dy * PLAYER_SPEED

        # Attack
        if any(keys[k] for k in ATTACK):
            if self.attack.try_attack(self.rect, self._facing, keys):
                pass  # audio handled by game

        # Determine animation state
        if not self.alive:
            self._state = 'death'
        elif self._flash > 0:
            self._state = 'damage'
        elif self.attack.active:
            self._state = 'attack'
        elif dx != 0 or dy != 0:
            self._state = 'walk'
        else:
            self._state = 'idle'

    def update(self, dt: float, walls: list, world_rect: pygame.Rect):
        if self.iframes > 0:
            self.iframes -= dt
        if self._flash > 0:
            self._flash -= dt

        # Move X
        self.rect.x += int(self.vel.x * dt)
        mtv = collide_rects(self.rect, walls)
        self.rect.x += int(mtv.x)

        # Move Y
        self.rect.y += int(self.vel.y * dt)
        mtv = collide_rects(self.rect, walls)
        self.rect.y += int(mtv.y)

        # World boundary clamp
        self.rect.clamp_ip(world_rect)

        # Attack update
        self.attack.update(dt, self.rect)

        # Particle update
        self._particles.update(dt)

        # Advance animation frame
        self._frame = (self._frame + self._frame_spd * dt) % len(self._anims[self._state])

    def take_damage(self, amount: int):
        if self.iframes > 0 or not self.alive:
            return False
        self.hp = max(0, self.hp - amount)
        self.iframes = IFRAMES
        self._flash  = 0.25
        # Emit damage particles
        self._particles.emit(self.rect.centerx, self.rect.centery, 12,
                             (255, 80, 80), (2, 5), (0.2, 0.5))
        if self.hp <= 0:
            self.alive = False
        return True

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

    def draw(self, surface: pygame.Surface, camera):
        frame_idx = int(self._frame) % len(self._anims[self._state])
        sprite    = self._anims[self._state][frame_idx]
        # iframes blink
        visible = True
        if self.iframes > 0:
            visible = int(self.iframes * 10) % 2 == 0
        if visible:
            r = camera.apply(self.rect)
            surface.blit(sprite, r.topleft)
        # Attack particles
        self.attack.draw(surface, camera)
        # Damage particles
        self._particles.draw(surface, camera)

    @property
    def center(self):
        return self.rect.center
