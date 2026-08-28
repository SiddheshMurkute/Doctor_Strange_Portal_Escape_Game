# levels/base_level.py

"""
Base level system for Doctor Strange Portal Escape.

The base level handles:
- camera
- portals
- fragments
- environment effects
- collisions
- visible rooftop collision blocks
"""

import heapq
import random

import pygame

from abc import ABC, abstractmethod

from core.camera import Camera
from config.stages import STAGE_CONFIG
from objects.portal_manager import PortalManager
from objects.fragment import Fragment
from effects.environment_effects import EnvironmentEffects


class BaseLevel(ABC):

    def __init__(
        self,
        stage: int,
        difficulty: str
    ):

        self.stage = stage
        self.difficulty = difficulty

        # ---------------------------------------------------------
        # STAGE CONFIG
        # ---------------------------------------------------------

        cfg = STAGE_CONFIG[stage]

        self.world_w = cfg["world_size"][0]
        self.world_h = cfg["world_size"][1]

        self.world_rect = pygame.Rect(
            0,
            0,
            self.world_w,
            self.world_h
        )

        # ---------------------------------------------------------
        # COLLISION WALLS
        # ---------------------------------------------------------

        self.walls = []

        # ---------------------------------------------------------
        # CAMERA
        # ---------------------------------------------------------

        self.camera = Camera(
            self.world_w,
            self.world_h
        )

        # ---------------------------------------------------------
        # PORTALS
        # ---------------------------------------------------------

        self.portal_mgr = None

        # ---------------------------------------------------------
        # FRAGMENTS
        # ---------------------------------------------------------

        self.fragments = []

        # ---------------------------------------------------------
        # ENVIRONMENT EFFECTS
        # ---------------------------------------------------------

        self.env_fx = EnvironmentEffects(
            stage,
            self.world_w,
            self.world_h
        )

        # ---------------------------------------------------------
        # STATUS
        # ---------------------------------------------------------

        self.portal_entered = False
        self.stage_failed = False

    # =============================================================
    # ABSTRACT METHODS
    # =============================================================

    @abstractmethod
    def setup(self):
        """
        Build:
        - walls
        - portals
        - enemies
        - fragments
        """
        pass

    @abstractmethod
    def draw_background(
        self,
        surface: pygame.Surface
    ):
        pass

    # =============================================================
    # PORTALS
    # =============================================================

    def generate_portals(
        self,
        player_start
    ):

        self.portal_mgr = PortalManager(
            self.stage,
            self.walls,
            player_start,
            self.world_rect
        )

        self.portal_mgr.generate()

    # =============================================================
    # FRAGMENTS
    # =============================================================

    def generate_fragments(
        self,
        count,
        exclusion_rects=None
    ):

        self.fragments = []

        for _ in range(count):

            for _attempt in range(100):

                x = random.randint(
                    100,
                    self.world_w - 100
                )

                y = random.randint(
                    100,
                    self.world_h - 100
                )

                rect = pygame.Rect(
                    x - 20,
                    y - 20,
                    40,
                    40
                )

                blocked = False

                # -------------------------------------------------
                # CHECK WALLS
                # -------------------------------------------------

                for wall in self.walls:

                    if rect.colliderect(wall):
                        blocked = True
                        break

                # -------------------------------------------------
                # CHECK EXCLUSIONS
                # -------------------------------------------------

                if (
                    not blocked
                    and exclusion_rects
                ):

                    for exclusion in exclusion_rects:

                        if rect.colliderect(exclusion):
                            blocked = True
                            break

                # -------------------------------------------------
                # CREATE FRAGMENT
                # -------------------------------------------------

                if not blocked:

                    self.fragments.append(
                        Fragment(
                            x,
                            y
                        )
                    )

                    break

        # ---------------------------------------------------------
        # VALIDATE LAYOUT ACCESSIBILITY
        # ---------------------------------------------------------

        if (
            self.stage in STAGE_CONFIG
            and "player_start" in STAGE_CONFIG[self.stage]
        ):
            self.ensure_accessibility(
                STAGE_CONFIG[self.stage]["player_start"]
            )

    # =============================================================
    # ACCESSIBILITY VALIDATION
    # =============================================================

    def ensure_accessibility(
        self,
        player_start: tuple
    ):
        """
        Validate that essential destinations remain reachable.

        If a destination is blocked by an internal wall, remove the
        blocking internal wall while never removing the outer
        boundary walls.
        """

        destinations = []

        # ---------------------------------------------------------
        # PORTAL DESTINATIONS
        # ---------------------------------------------------------

        if getattr(self, "portal_mgr", None):

            for portal in self.portal_mgr.portals:
                destinations.append(
                    portal.rect.center
                )

        # ---------------------------------------------------------
        # FRAGMENT DESTINATIONS
        # ---------------------------------------------------------

        for fragment in getattr(
            self,
            "fragments",
            []
        ):

            destinations.append(
                fragment.rect.center
            )

        if not destinations:
            return

        # ---------------------------------------------------------
        # PATHFINDING CONFIG
        # ---------------------------------------------------------

        grid_size = 30

        cols = (
            self.world_w // grid_size
        ) + 1

        rows = (
            self.world_h // grid_size
        ) + 1

        # Approximate player collision footprint
        player_w = 64
        player_h = 80

        start_cx = int(
            player_start[0] // grid_size
        )

        start_cy = int(
            player_start[1] // grid_size
        )

        # ---------------------------------------------------------
        # PROCESS EACH DESTINATION
        # ---------------------------------------------------------

        for destination in destinations:

            target_cx = int(
                destination[0] // grid_size
            )

            target_cy = int(
                destination[1] // grid_size
            )

            memo = {}

            def get_wall_collisions(cx, cy):

                if (cx, cy) in memo:
                    return memo[(cx, cy)]

                bx = (
                    cx * grid_size
                    + grid_size // 2
                )

                by = (
                    cy * grid_size
                    + grid_size // 2
                )

                player_rect = pygame.Rect(
                    bx - player_w // 2,
                    by - player_h // 2,
                    player_w,
                    player_h
                )

                hits = [
                    wall
                    for wall in self.walls
                    if player_rect.colliderect(wall)
                ]

                memo[(cx, cy)] = hits

                return hits

            def heuristic(cx, cy):
                return (
                    abs(cx - target_cx)
                    + abs(cy - target_cy)
                )

            # -----------------------------------------------------
            # A* SEARCH
            # -----------------------------------------------------

            queue = [
                (
                    heuristic(
                        start_cx,
                        start_cy
                    ),
                    0,
                    start_cx,
                    start_cy,
                    []
                )
            ]

            visited = {}
            found_path = None

            while queue:

                (
                    estimated_cost,
                    cost,
                    cx,
                    cy,
                    path
                ) = heapq.heappop(queue)

                # ---------------------------------------------
                # TARGET REACHED
                # ---------------------------------------------

                if (
                    cx == target_cx
                    and cy == target_cy
                ):

                    found_path = path
                    break

                # ---------------------------------------------
                # SKIP EXPENSIVE VISITS
                # ---------------------------------------------

                if (
                    (cx, cy) in visited
                    and visited[(cx, cy)] <= cost
                ):
                    continue

                visited[(cx, cy)] = cost

                # ---------------------------------------------
                # NEIGHBOURS
                # ---------------------------------------------

                for dx, dy in [
                    (-1, 0),
                    (1, 0),
                    (0, -1),
                    (0, 1)
                ]:

                    nx = cx + dx
                    ny = cy + dy

                    if not (
                        0 <= nx < cols
                        and 0 <= ny < rows
                    ):
                        continue

                    walls_hit = get_wall_collisions(
                        nx,
                        ny
                    )

                    step_cost = 1

                    is_boundary = False

                    if walls_hit:

                        for wall in walls_hit:

                            if (
                                wall.x <= 0
                                or wall.y <= 0
                                or wall.right >= self.world_w
                                or wall.bottom >= self.world_h
                            ):

                                is_boundary = True
                                break

                        # Never remove or cross world boundaries.
                        if is_boundary:
                            continue

                        # Internal wall = expensive but potentially
                        # removable for accessibility repair.
                        step_cost += 1000

                    new_cost = cost + step_cost

                    if (
                        (nx, ny) not in visited
                        or visited[(nx, ny)] > new_cost
                    ):

                        heapq.heappush(
                            queue,
                            (
                                new_cost
                                + heuristic(nx, ny),
                                new_cost,
                                nx,
                                ny,
                                path + [(nx, ny)]
                            )
                        )

            # -----------------------------------------------------
            # REMOVE BLOCKING INTERNAL WALLS
            # -----------------------------------------------------

            if found_path:

                for px, py in found_path:

                    hits = get_wall_collisions(
                        px,
                        py
                    )

                    for wall in hits:

                        if wall not in self.walls:
                            continue

                        is_outer_boundary = (
                            wall.x <= 0
                            or wall.y <= 0
                            or wall.right >= self.world_w
                            or wall.bottom >= self.world_h
                        )

                        if not is_outer_boundary:
                            self.walls.remove(wall)

    # =============================================================
    # UPDATE
    # =============================================================

    def update(
        self,
        dt: float,
        player,
        e_pressed: bool,
        score_callback
    ) -> str | None:
        """
        Returns:
            'correct' -> player entered the correct portal
            'wrong'   -> player interacted with a wrong portal
            None      -> normal gameplay
        """

        # ---------------------------------------------------------
        # CAMERA
        # ---------------------------------------------------------

        self.camera.update(
            player.rect
        )

        # ---------------------------------------------------------
        # ENVIRONMENT
        # ---------------------------------------------------------

        self.env_fx.update(
            dt,
            self.camera.offset_x,
            self.camera.offset_y
        )

        # ---------------------------------------------------------
        # PORTALS
        # ---------------------------------------------------------

        if self.portal_mgr:

            self.portal_mgr.update(
                dt
            )

            result = self.portal_mgr.check_interaction(
                player.rect,
                e_pressed
            )

            if result == "correct":

                self.portal_entered = True

                return "correct"

            if result == "wrong":

                return "wrong"

        # ---------------------------------------------------------
        # FRAGMENTS
        # ---------------------------------------------------------

        for fragment in self.fragments:

            if fragment.collected:
                continue

            fragment.update(
                dt
            )

            if fragment.check_collect(
                player.rect
            ):

                score_callback(
                    fragment.value
                )

        return None

    # =============================================================
    # DRAW
    # =============================================================

    def draw(
        self,
        surface,
        label_font=None
    ):

        # ---------------------------------------------------------
        # BACKGROUND
        # ---------------------------------------------------------

        self.draw_background(
            surface
        )

        # ---------------------------------------------------------
        # VISIBLE COLLISION WALLS
        # ---------------------------------------------------------
        #
        # Original style:
        # dark purple blocks
        #
        # Outer boundary walls remain invisible.
        #
        # ---------------------------------------------------------

        for wall in self.walls:

            if (
                wall.width == self.world_w
                or wall.height == self.world_h
            ):
                continue

            screen_rect = pygame.Rect(
                wall.x - self.camera.offset_x,
                wall.y - self.camera.offset_y,
                wall.width,
                wall.height
            )

            pygame.draw.rect(
                surface,
                (30, 20, 50),
                screen_rect
            )

        # ---------------------------------------------------------
        # PORTALS
        # ---------------------------------------------------------

        if self.portal_mgr:

            self.portal_mgr.draw(
                surface,
                self.camera,
                label_font
            )

        # ---------------------------------------------------------
        # FRAGMENTS
        # ---------------------------------------------------------

        for fragment in self.fragments:

            fragment.draw(
                surface,
                self.camera
            )

        # ---------------------------------------------------------
        # ENVIRONMENT PARTICLES
        # ---------------------------------------------------------

        self.env_fx.draw(
            surface,
            self.camera
        )

    # =============================================================
    # INTERACTION PROMPTS
    # =============================================================

    def draw_interact_prompts(
        self,
        surface,
        player_rect,
        label_font
    ):

        if (
            self.portal_mgr
            and label_font
        ):

            self.portal_mgr.draw_prompts(
                surface,
                self.camera,
                player_rect,
                label_font
            )