# ============================================================
# player/player_attack.py
# DOCTOR STRANGE PORTAL ESCAPE GAME
# SAFE COMPATIBLE ATTACK SYSTEM
# ============================================================

import pygame
import math
import random


# ============================================================
# ATTACK SETTINGS
# ============================================================

ATTACK_COOLDOWN = 0.40
ATTACK_DURATION = 0.25
ATTACK_DAMAGE = 30
ATTACK_RANGE = 120


# ============================================================
# MYSTIC FLAME
# ============================================================

class MysticFlame:

    # IMPORTANT:
    # player is optional so both MysticFlame()
    # and MysticFlame(player) work.

    def __init__(self, player=None):

        self.player = player

        self.damage = ATTACK_DAMAGE

        self.cooldown = ATTACK_COOLDOWN
        self.cooling = 0.0

        self.active = False
        self.timer = 0.0

        self.duration = ATTACK_DURATION

        self.angle = 0.0

    # ========================================================
    # COOLDOWN PERCENT
    # ========================================================

    @property
    def cooldown_pct(self):

        if self.cooldown <= 0:
            return 0.0

        value = self.cooling / self.cooldown

        return max(
            0.0,
            min(1.0, value)
        )

    # ========================================================
    # START ATTACK
    # ========================================================

    def start(self):

        if self.cooling > 0:
            return False

        self.active = True
        self.timer = self.duration
        self.cooling = self.cooldown

        # Get player direction if available
        if self.player is not None:

            if hasattr(self.player, "facing_right"):

                if self.player.facing_right:
                    self.angle = 0.0
                else:
                    self.angle = math.pi

            elif hasattr(self.player, "_facing"):

                direction = self.player._facing

                if direction == "left":
                    self.angle = math.pi

                elif direction == "up":
                    self.angle = -math.pi / 2

                elif direction == "down":
                    self.angle = math.pi / 2

                else:
                    self.angle = 0.0

        return True

    # ========================================================
    # TRY ATTACK
    # ========================================================

    def try_attack(
        self,
        player_rect,
        facing="right",
        keys=None
    ):

        if self.cooling > 0:
            return False

        directions = {

            "right": 0.0,

            "left": math.pi,

            "up": -math.pi / 2,

            "down": math.pi / 2,

        }

        self.angle = directions.get(
            facing,
            0.0
        )

        self.active = True

        self.timer = self.duration

        self.cooling = self.cooldown

        return True

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt,
        player_rect=None
    ):

        try:
            dt = float(dt)
        except:
            dt = 0.0

        dt = max(
            0.0,
            dt
        )

        # ----------------------------------------------------
        # COOLDOWN
        # ----------------------------------------------------

        if self.cooling > 0:

            self.cooling -= dt

            if self.cooling < 0:
                self.cooling = 0.0

        # ----------------------------------------------------
        # ACTIVE ATTACK
        # ----------------------------------------------------

        if self.active:

            self.timer -= dt

            if self.timer <= 0:

                self.timer = 0.0

                self.active = False

    # ========================================================
    # HITBOX
    # ========================================================

    def get_hitbox(
        self,
        player_rect
    ):

        if not self.active:

            return pygame.Rect(
                0,
                0,
                0,
                0
            )

        distance = ATTACK_RANGE * 0.5

        center_x = (
            player_rect.centerx
            + int(
                math.cos(self.angle)
                * distance
            )
        )

        center_y = (
            player_rect.centery
            + int(
                math.sin(self.angle)
                * distance
            )
        )

        radius = ATTACK_RANGE // 2

        return pygame.Rect(

            center_x - radius,

            center_y - radius,

            radius * 2,

            radius * 2
        )

    # ========================================================
    # DRAW ATTACK EFFECT
    # ========================================================

    def draw(
        self,
        surface,
        camera=None
    ):

        if not self.active:
            return

        if self.player is None:
            return

        if not hasattr(
            self.player,
            "rect"
        ):
            return

        rect = self.player.rect

        # ----------------------------------------------------
        # ATTACK CENTER
        # ----------------------------------------------------

        cx = (
            rect.centerx
            + int(
                math.cos(self.angle)
                * 45
            )
        )

        cy = (
            rect.centery
            + int(
                math.sin(self.angle)
                * 45
            )
        )

        # ----------------------------------------------------
        # MAGIC CIRCLE
        # ----------------------------------------------------

        pygame.draw.circle(

            surface,

            (255, 180, 40),

            (cx, cy),

            38,

            4
        )

        pygame.draw.circle(

            surface,

            (255, 230, 100),

            (cx, cy),

            28,

            3
        )

        # ----------------------------------------------------
        # FLAME PARTICLES
        # ----------------------------------------------------

        for _ in range(8):

            spread = random.uniform(
                -0.6,
                0.6
            )

            angle = (
                self.angle
                + spread
            )

            distance = random.randint(
                20,
                55
            )

            px = (
                cx
                + int(
                    math.cos(angle)
                    * distance
                )
            )

            py = (
                cy
                + int(
                    math.sin(angle)
                    * distance
                )
            )

            pygame.draw.circle(

                surface,

                random.choice(
                    [
                        (255, 100, 0),
                        (255, 180, 0),
                        (255, 230, 80),
                    ]
                ),

                (px, py),

                random.randint(
                    2,
                    5
                )
            )


# ============================================================
# COMPATIBILITY CLASS
# ============================================================

class PlayerAttack(MysticFlame):

    def __init__(
        self,
        player=None
    ):

        super().__init__(
            player
        )