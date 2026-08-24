# effects/environment_effects.py
import pygame
import random
import math

class EnvParticle:
    __slots__ = ('x','y','vx','vy','life','color','radius')
    def __init__(self, x, y, vx, vy, life, color, radius):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.color = color
        self.radius = radius

class EnvironmentEffects:
    """Ambient environmental particles: snow, embers, space dust, smog."""

    def __init__(self, stage: int, world_w: int, world_h: int):
        self.stage   = stage
        self.world_w = world_w
        self.world_h = world_h
        self._particles: list[EnvParticle] = []
        self._timer  = 0.0

    def _spawn(self, camera_x, camera_y):
        sw, sh = 1280, 720
        stage = self.stage
        if stage == 1:   # city smog / sparks
            for _ in range(2):
                self._new(random.randint(int(camera_x), int(camera_x)+sw),
                          random.randint(int(camera_y), int(camera_y)+sh),
                          random.uniform(-0.3, 0.3), random.uniform(-0.5, -0.1),
                          random.uniform(1.5, 3.0), (180,180,180), random.randint(2,5))
        elif stage == 2:  # space dust
            for _ in range(2):
                self._new(random.randint(int(camera_x), int(camera_x)+sw),
                          random.randint(int(camera_y), int(camera_y)+sh),
                          random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2),
                          random.uniform(2.0, 4.0), (150,200,255), random.randint(1,3))
        elif stage == 3:  # alien dust
            for _ in range(2):
                self._new(int(camera_x) + random.randint(0, sw),
                          int(camera_y) + sh,
                          random.uniform(-0.3, 0.3), random.uniform(-1.0, -0.3),
                          random.uniform(1.5, 3.0), (180,120,60), random.randint(2,4))
        elif stage == 4:  # falling snow
            for _ in range(6):
                self._new(int(camera_x) + random.randint(0, sw),
                          int(camera_y),
                          random.uniform(-0.5, 0.5), random.uniform(1.0, 2.5),
                          random.uniform(2.0, 5.0), (220,240,255), random.randint(2,5))
        elif stage == 5:  # embers
            for _ in range(4):
                self._new(int(camera_x) + random.randint(0, sw),
                          int(camera_y) + sh,
                          random.uniform(-1.0, 1.0), random.uniform(-2.5, -0.8),
                          random.uniform(1.0, 2.5), random.choice([(255,100,0),(255,50,0),(255,200,0)]),
                          random.randint(2,5))

    def _new(self, x, y, vx, vy, life, color, radius):
        self._particles.append(EnvParticle(x, y, vx, vy, life, color, radius))

    def update(self, dt, camera_x=0, camera_y=0):
        self._timer += dt
        if self._timer >= 0.06:
            self._timer = 0
            self._spawn(camera_x, camera_y)
        alive = []
        for p in self._particles:
            p.life -= dt
            if p.life > 0:
                p.x += p.vx
                p.y += p.vy
                alive.append(p)
        self._particles = alive

    def draw(self, surface, camera=None):
        ox = int(camera.offset_x) if camera else 0
        oy = int(camera.offset_y) if camera else 0
        for p in self._particles:
            sx = int(p.x) - ox
            sy = int(p.y) - oy
            if -10 < sx < 1300 and -10 < sy < 740:
                pygame.draw.circle(surface, p.color, (sx, sy), p.radius)
