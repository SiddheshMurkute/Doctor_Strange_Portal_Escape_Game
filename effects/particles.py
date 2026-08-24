# effects/particles.py
import pygame
import random
import math

class Particle:
    __slots__ = ('x','y','vx','vy','life','max_life','r','g','b','a','radius','gravity')
    def __init__(self, x, y, vx, vy, life, color, radius=3, gravity=0):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.r, self.g, self.b = color[0], color[1], color[2]
        self.a = 255
        self.radius = radius
        self.gravity = gravity

class ParticleSystem:
    def __init__(self):
        self._particles: list[Particle] = []

    def emit(self, x, y, count, color, speed_range=(1,4), life_range=(0.3,0.9),
             radius_range=(2,5), gravity=0, spread=math.pi*2):
        for _ in range(count):
            angle = random.uniform(0, spread)
            spd   = random.uniform(*speed_range)
            life  = random.uniform(*life_range)
            r     = random.uniform(*radius_range)
            self._particles.append(Particle(x, y, math.cos(angle)*spd, math.sin(angle)*spd,
                                            life, color, r, gravity))

    def update(self, dt):
        alive = []
        for p in self._particles:
            p.life -= dt
            if p.life > 0:
                p.x += p.vx
                p.y += p.vy
                p.vy += p.gravity * dt
                p.a = int(255 * (p.life / p.max_life))
                alive.append(p)
        self._particles = alive

    def draw(self, surface, camera=None):
        for p in self._particles:
            sx = int(p.x) - (camera.offset_x if camera else 0)
            sy = int(p.y) - (camera.offset_y if camera else 0)
            rad = max(1, int(p.radius * (p.life / p.max_life)))
            s = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (p.r, p.g, p.b, p.a), (rad, rad), rad)
            surface.blit(s, (sx-rad, sy-rad))

    def clear(self):
        self._particles.clear()
