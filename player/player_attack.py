# player/player_attack.py
import pygame
import math
from effects.particles import ParticleSystem

ATTACK_COOLDOWN  = 0.4    # seconds
ATTACK_DURATION  = 0.25   # seconds for hitbox to be active
ATTACK_DAMAGE    = 30     # base damage
ATTACK_RANGE     = 120    # pixel radius

class MysticFlame:
    def __init__(self):
        self.cooling = 0.0
        self.active  = False
        self.timer   = 0.0
        self.particles = ParticleSystem()
        self.angle   = 0.0   # direction of attack

    def try_attack(self, player_rect: pygame.Rect, facing: str, keys) -> bool:
        """Returns True if attack just fired."""
        if self.cooling > 0:
            return False
        # Determine angle from facing
        angles = {'right': 0, 'left': math.pi, 'up': -math.pi/2, 'down': math.pi/2}
        self.angle = angles.get(facing, 0)
        self.active = True
        self.timer  = ATTACK_DURATION
        self.cooling = ATTACK_COOLDOWN
        return True

    def update(self, dt: float, player_rect: pygame.Rect):
        if self.cooling > 0:
            self.cooling -= dt
        if self.active:
            self.timer -= dt
            cx, cy = player_rect.centerx, player_rect.centery
            for _ in range(5):
                speed = __import__('random').uniform(3, 7)
                spread = __import__('random').uniform(-0.4, 0.4)
                ang = self.angle + spread
                vx = math.cos(ang) * speed
                vy = math.sin(ang) * speed
                col = __import__('random').choice([(255,180,0),(255,100,0),(255,220,80)])
                self.particles.emit(cx + math.cos(self.angle)*20,
                                    cy + math.sin(self.angle)*20,
                                    1, col, (3,7), (0.15,0.35), (2,5))
            if self.timer <= 0:
                self.active = False
        self.particles.update(dt)

    def get_hitbox(self, player_rect: pygame.Rect) -> pygame.Rect | None:
        if not self.active:
            return None
        cx = player_rect.centerx + int(math.cos(self.angle) * ATTACK_RANGE * 0.5)
        cy = player_rect.centery + int(math.sin(self.angle) * ATTACK_RANGE * 0.5)
        r = ATTACK_RANGE // 2
        return pygame.Rect(cx - r, cy - r, r*2, r*2)

    def draw(self, surface: pygame.Surface, camera):
        self.particles.draw(surface, camera)
        # Draw cooldown ring above player would be in HUD

    @property
    def cooldown_pct(self) -> float:
        return max(0.0, self.cooling / ATTACK_COOLDOWN)
