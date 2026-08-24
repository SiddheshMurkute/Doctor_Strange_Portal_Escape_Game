# objects/portal_manager.py
"""Constrained random portal placement with validation."""
import pygame
import random
import math
from objects.portal import Portal
from config.stages import STAGE_CONFIG


def _valid_pos(x, y, pw, ph, walls: list, other_portals: list,
               player_start, min_portal_dist=200, min_player_dist=200,
               min_wall_margin=30) -> bool:
    r = pygame.Rect(x, y, pw, ph)
    # Not overlapping walls
    for w in walls:
        if r.inflate(min_wall_margin*2, min_wall_margin*2).colliderect(w):
            return False
    # Not too close to other portals
    for op in other_portals:
        if math.hypot(x-op.rect.x, y-op.rect.y) < min_portal_dist:
            return False
    # Not too close to player
    if math.hypot(x-player_start[0], y-player_start[1]) < min_player_dist:
        return False
    return True


class PortalManager:
    def __init__(self, stage: int, walls: list, player_start, world_rect: pygame.Rect):
        self.stage        = stage
        self.walls        = walls
        self.player_start = player_start
        self.world_rect   = world_rect
        self.portals: list[Portal] = []
        self._interacted  = set()  # portal ids already tried
        self._used_wrong  = set()

        cfg = STAGE_CONFIG[stage]
        self._count  = cfg["portal_count"]
        self._zones  = cfg["portal_zones"]
        self._labels = cfg.get("portal_labels", [])
        self._correct_label = cfg.get("correct_label", "")

    def generate(self):
        """Generate portals with constrained random placement."""
        from objects.portal import PORTAL_W, PORTAL_H
        correct_idx = random.randint(0, self._count - 1)
        placed: list[Portal] = []
        all_zones = list(self._zones)
        random.shuffle(all_zones)

        for i in range(self._count):
            label = self._labels[i] if i < len(self._labels) else ""
            portal_placed = False
            for attempt in range(60):
                zone = all_zones[i % len(all_zones)]
                zx, zy, zw, zh = zone
                x = random.randint(zx, max(zx+1, zx+zw-PORTAL_W))
                y = random.randint(zy, max(zy+1, zy+zh-PORTAL_H))
                if _valid_pos(x, y, PORTAL_W, PORTAL_H, self.walls, placed,
                               self.player_start):
                    p = Portal(x, y, self.stage, i == correct_idx, label, i)
                    placed.append(p)
                    portal_placed = True
                    break
            if not portal_placed:
                # fallback — place at zone origin
                zone = all_zones[i % len(all_zones)]
                p = Portal(zone[0]+10, zone[1]+10, self.stage, i == correct_idx, label, i)
                placed.append(p)

        self.portals = placed

    def update(self, dt: float):
        for p in self.portals:
            p.update(dt)

    def draw(self, surface, camera, font=None):
        for p in self.portals:
            p.draw(surface, camera, font)

    def check_interaction(self, player_rect, e_pressed: bool) -> str | None:
        """
        Returns:
          'correct'  — player entered the correct portal
          'wrong'    — player entered a wrong portal
          None       — no interaction
        Also draws prompt if nearby. Call draw_prompts separately.
        """
        if not e_pressed:
            return None
        for p in self.portals:
            if p.portal_id in self._used_wrong:
                continue
            if p.is_player_nearby(player_rect):
                if p.is_correct:
                    p.activated = True
                    return 'correct'
                else:
                    self._used_wrong.add(p.portal_id)
                    return 'wrong'
        return None

    def draw_prompts(self, surface, camera, player_rect, font):
        for p in self.portals:
            if p.is_player_nearby(player_rect):
                if p.portal_id not in self._used_wrong:
                    p.draw_interact_prompt(surface, camera, font)

    def nearest_portal_dist(self, pos) -> float:
        if not self.portals:
            return 9999
        return min(math.hypot(pos[0]-p.rect.centerx, pos[1]-p.rect.centery)
                   for p in self.portals)
