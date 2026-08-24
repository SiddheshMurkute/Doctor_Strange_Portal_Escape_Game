# levels/base_level.py
"""Abstract base for all five stages."""
import pygame
import random
import math
from abc import ABC, abstractmethod
from core.camera import Camera
from config.stages import STAGE_CONFIG
from objects.portal_manager import PortalManager
from objects.fragment import Fragment
from effects.environment_effects import EnvironmentEffects


class BaseLevel(ABC):
    def __init__(self, stage: int, difficulty: str):
        self.stage      = stage
        self.difficulty = difficulty
        cfg             = STAGE_CONFIG[stage]
        self.world_w    = cfg["world_size"][0]
        self.world_h    = cfg["world_size"][1]
        self.world_rect = pygame.Rect(0, 0, self.world_w, self.world_h)

        self.walls: list[pygame.Rect] = []
        self.camera = Camera(self.world_w, self.world_h)

        # Portals
        self.portal_mgr: PortalManager | None = None

        # Fragments
        self.fragments: list[Fragment] = []

        # Environment particles
        self.env_fx = EnvironmentEffects(stage, self.world_w, self.world_h)

        # Status flags
        self.portal_entered   = False  # True when correct portal touched
        self.stage_failed     = False

    # -------------------------------------------------------------- abstract
    @abstractmethod
    def setup(self):
        """Build walls, portals, enemies, fragments."""
        ...

    @abstractmethod
    def draw_background(self, surface: pygame.Surface):
        """Draw the stage-specific background/environment."""
        ...

    # -------------------------------------------------------------- common
    def generate_portals(self, player_start):
        self.portal_mgr = PortalManager(self.stage, self.walls, player_start, self.world_rect)
        self.portal_mgr.generate()

    def generate_fragments(self, count, exclusion_rects=None):
        cfg = STAGE_CONFIG[self.stage]
        for _ in range(count):
            for attempt in range(40):
                x = random.randint(100, self.world_w - 100)
                y = random.randint(100, self.world_h - 100)
                r = pygame.Rect(x-20, y-20, 40, 40)
                blocked = any(r.colliderect(w) for w in self.walls)
                if exclusion_rects:
                    blocked = blocked or any(r.colliderect(ex) for ex in exclusion_rects)
                if not blocked:
                    self.fragments.append(Fragment(x, y))
                    break

    def update(self, dt: float, player, e_pressed: bool, score_callback) -> str | None:
        """
        Returns:
          'correct'  — player hit the right portal → stage complete
          'wrong'    — penalty interaction
          None       — normal tick
        """
        self.camera.update(player.rect)
        self.env_fx.update(dt, self.camera.offset_x, self.camera.offset_y)

        if self.portal_mgr:
            self.portal_mgr.update(dt)
            result = self.portal_mgr.check_interaction(player.rect, e_pressed)
            if result == 'correct':
                self.portal_entered = True
                return 'correct'
            elif result == 'wrong':
                return 'wrong'

        # Fragment collection
        for frag in self.fragments:
            if not frag.collected:
                frag.update(dt)
                if frag.check_collect(player.rect):
                    score_callback(frag.value)

        return None

    def draw(self, surface: pygame.Surface, label_font=None):
        self.draw_background(surface)
        # Walls (debug tint — remove if too ugly or paint over in subclass)
        ox = int(self.camera.offset_x)
        oy = int(self.camera.offset_y)
        for w in self.walls:
            r = pygame.Rect(w.x-ox, w.y-oy, w.width, w.height)
            if -w.width < r.x < 1290 and -w.height < r.y < 730:
                pygame.draw.rect(surface, (30, 20, 50), r, border_radius=4)
                pygame.draw.rect(surface, (80, 60, 120), r, 2, border_radius=4)

        # Portals
        if self.portal_mgr:
            self.portal_mgr.draw(surface, self.camera, label_font)

        # Fragments
        for frag in self.fragments:
            frag.draw(surface, self.camera)

        # Env particles
        self.env_fx.draw(surface, self.camera)

    def draw_interact_prompts(self, surface, player_rect, label_font):
        if self.portal_mgr and label_font:
            self.portal_mgr.draw_prompts(surface, self.camera, player_rect, label_font)
