# ============================================================
# DOCTOR STRANGE STYLE PLAYER
# player/player.py
# ============================================================

import pygame
import math
import os

from config.controls import *
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from player.player_animation import build_animations
from player.player_attack import MysticFlame
from core.collision import collide_rects
from effects.particles import ParticleSystem


# ============================================================
# PLAYER SETTINGS
# ============================================================

PLAYER_SPEED = 220
PLAYER_HP = 100
IFRAMES = 0.6
DAMAGE_PER_HIT = 5


class Player:

    # ========================================================
    # INITIALIZE PLAYER
    # ========================================================

    def __init__(self, x: int, y: int):

        print("")
        print("🔥🔥🔥 DOCTOR STRANGE PLAYER.PY IS RUNNING 🔥🔥🔥")
        print("")

        # ----------------------------------------------------
        # COLLISION SIZE
        # ----------------------------------------------------

        self.SIZE = (64, 80)

        self.rect = pygame.Rect(
            x,
            y,
            self.SIZE[0],
            self.SIZE[1]
        )

        self.vel = pygame.Vector2(0, 0)

        # ----------------------------------------------------
        # HEALTH
        # ----------------------------------------------------

        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.alive = True
        self.iframes = 0.0

        # ----------------------------------------------------
        # ORIGINAL ANIMATION SYSTEM
        # ----------------------------------------------------

        self._anims = build_animations(self.SIZE)

        self._state = "idle"
        self._frame = 0.0
        self._frame_spd = 6.0
        self._facing = "right"

        # ----------------------------------------------------
        # CUSTOM DOCTOR STRANGE IMAGE
        # ----------------------------------------------------

        self.custom_player = None

        self.load_custom_player()

        # ----------------------------------------------------
        # ATTACK
        # ----------------------------------------------------

        self.attack = MysticFlame()

        # ----------------------------------------------------
        # PARTICLES
        # ----------------------------------------------------

        self._particles = ParticleSystem()

        # ----------------------------------------------------
        # DAMAGE FLASH
        # ----------------------------------------------------

        self._flash = 0.0

        # ----------------------------------------------------
        # FRAGMENTS
        # ----------------------------------------------------

        self.fragments_collected = 0

    # ========================================================
    # LOAD CUSTOM PLAYER
    # ========================================================

    def load_custom_player(self):

        print("==============================================")
        print("🪄 LOADING CUSTOM SORCERER PLAYER")
        print("==============================================")

        # ----------------------------------------------------
        # FIND PROJECT DIRECTORY
        # ----------------------------------------------------

        current_file = os.path.abspath(__file__)

        player_folder = os.path.dirname(
            current_file
        )

        project_folder = os.path.dirname(
            player_folder
        )

        # ----------------------------------------------------
        # PLAYER IMAGE FOLDER
        # ----------------------------------------------------

        player_folder_path = os.path.join(
            project_folder,
            "assets",
            "player"
        )

        print("Player asset folder:")
        print(player_folder_path)

        # ----------------------------------------------------
        # POSSIBLE IMAGE NAMES
        #
        # This is deliberately flexible so that the game
        # can find your image even if you forgot to rename it.
        # ----------------------------------------------------

        possible_images = [

            "mystical_sorcerer_player.jpg",

            "doctor_strange_player_120x145.jpg",

            "doctor_strange_player.jpg",

            "mystical_sorcerer_player.jpeg",

            "doctor_strange_player.jpeg",

            "mystical_sorcerer_player.png",

            "doctor_strange_player.png"
        ]

        image_path = None

        # ----------------------------------------------------
        # SEARCH FOR IMAGE
        # ----------------------------------------------------

        for filename in possible_images:

            test_path = os.path.join(
                player_folder_path,
                filename
            )

            if os.path.isfile(test_path):

                image_path = test_path

                print("")
                print("✅ FOUND PLAYER IMAGE:")
                print(filename)

                break

        # ----------------------------------------------------
        # IF NOTHING FOUND
        # ----------------------------------------------------

        if image_path is None:

            print("")
            print("❌❌❌ PLAYER IMAGE NOT FOUND ❌❌❌")
            print("")

            print(
                "Game searched in:"
            )

            print(
                player_folder_path
            )

            print("")

            print("Files currently found:")

            if os.path.isdir(
                player_folder_path
            ):

                for filename in os.listdir(
                    player_folder_path
                ):

                    print(
                        "   ->",
                        filename
                    )

            else:

                print(
                    "   PLAYER ASSET FOLDER DOES NOT EXIST!"
                )

            print("")
            print("Original player will be used.")
            print("==============================================")

            return

        # ====================================================
        # LOAD IMAGE
        # ====================================================

        try:

            image = pygame.image.load(
                image_path
            ).convert()

        except Exception as error:

            print("")
            print("❌ ERROR LOADING PLAYER IMAGE")
            print(error)
            print("==============================================")

            return

        # ----------------------------------------------------
        # IMAGE SIZE
        # ----------------------------------------------------

        print("")
        print(
            "Original image:",
            image.get_width(),
            "x",
            image.get_height()
        )

        # ====================================================
        # MAKE IMAGE ALPHA
        # ====================================================

        image = image.convert_alpha()

        # ====================================================
        # REMOVE LIGHT BACKGROUND
        # ====================================================

        width = image.get_width()
        height = image.get_height()

        for y in range(height):

            for x in range(width):

                r, g, b, a = image.get_at(
                    (x, y)
                )

                # Remove white/light gray background

                if (
                    r > 220
                    and g > 220
                    and b > 220
                ):

                    image.set_at(
                        (x, y),
                        (
                            r,
                            g,
                            b,
                            0
                        )
                    )

        # ====================================================
        # FINAL DISPLAY SIZE
        # ====================================================

        PLAYER_WIDTH = 120
        PLAYER_HEIGHT = 145

        image = pygame.transform.smoothscale(
            image,
            (
                PLAYER_WIDTH,
                PLAYER_HEIGHT
            )
        )

        # ====================================================
        # CREATE TRANSPARENT PLAYER SURFACE
        # ====================================================

        self.custom_player = pygame.Surface(
            (
                PLAYER_WIDTH,
                PLAYER_HEIGHT
            ),
            pygame.SRCALPHA
        )

        self.custom_player.fill(
            (
                0,
                0,
                0,
                0
            )
        )

        # ----------------------------------------------------
        # DRAW IMAGE
        # ----------------------------------------------------

        self.custom_player.blit(
            image,
            (
                0,
                0
            )
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        print("")
        print("==============================================")
        print("✅ CUSTOM SORCERER PLAYER LOADED!")
        print("==============================================")
        print(
            "Display size:",
            PLAYER_WIDTH,
            "x",
            PLAYER_HEIGHT
        )
        print(
            "Image:",
            os.path.basename(image_path)
        )
        print("==============================================")
        print("")

    # ========================================================
    # INPUT
    # ========================================================

    def handle_input(
        self,
        keys,
        dt: float
    ):

        if not self.alive:

            return

        dx = 0.0
        dy = 0.0

        # ----------------------------------------------------
        # LEFT
        # ----------------------------------------------------

        if any(
            keys[k]
            for k in MOVE_LEFT
        ):

            dx -= 1

            self._facing = "left"

        # ----------------------------------------------------
        # RIGHT
        # ----------------------------------------------------

        if any(
            keys[k]
            for k in MOVE_RIGHT
        ):

            dx += 1

            self._facing = "right"

        # ----------------------------------------------------
        # UP
        # ----------------------------------------------------

        if any(
            keys[k]
            for k in MOVE_UP
        ):

            dy -= 1

            self._facing = "up"

        # ----------------------------------------------------
        # DOWN
        # ----------------------------------------------------

        if any(
            keys[k]
            for k in MOVE_DOWN
        ):

            dy += 1

            self._facing = "down"

        # ----------------------------------------------------
        # DIAGONAL MOVEMENT
        # ----------------------------------------------------

        if dx != 0 and dy != 0:

            magnitude = math.sqrt(2)

            dx /= magnitude
            dy /= magnitude

        self.vel.x = (
            dx * PLAYER_SPEED
        )

        self.vel.y = (
            dy * PLAYER_SPEED
        )

        # ====================================================
        # ATTACK
        # ====================================================

        if any(
            keys[k]
            for k in ATTACK
        ):

            self.attack.try_attack(
                self.rect,
                self._facing,
                keys
            )

        # ====================================================
        # STATE
        # ====================================================

        if not self.alive:

            self._state = "death"

        elif self._flash > 0:

            self._state = "damage"

        elif self.attack.active:

            self._state = "attack"

        elif dx != 0 or dy != 0:

            self._state = "walk"

        else:

            self._state = "idle"

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt: float,
        walls: list,
        world_rect: pygame.Rect
    ):

        # ----------------------------------------------------
        # IFRAMES
        # ----------------------------------------------------

        if self.iframes > 0:

            self.iframes -= dt

        # ----------------------------------------------------
        # DAMAGE FLASH
        # ----------------------------------------------------

        if self._flash > 0:

            self._flash -= dt

        # ====================================================
        # X MOVEMENT
        # ====================================================

        self.rect.x += int(
            self.vel.x * dt
        )

        mtv = collide_rects(
            self.rect,
            walls
        )

        self.rect.x += int(
            mtv.x
        )

        # ====================================================
        # Y MOVEMENT
        # ====================================================

        self.rect.y += int(
            self.vel.y * dt
        )

        mtv = collide_rects(
            self.rect,
            walls
        )

        self.rect.y += int(
            mtv.y
        )

        # ====================================================
        # WORLD BOUNDARY
        # ====================================================

        self.rect.clamp_ip(
            world_rect
        )

        # ====================================================
        # ATTACK UPDATE
        # ====================================================

        self.attack.update(
            dt,
            self.rect
        )

        # ====================================================
        # PARTICLES
        # ====================================================

        self._particles.update(
            dt
        )

        # ====================================================
        # ANIMATION FRAME
        # ====================================================

        if self._state in self._anims:

            frames = self._anims[
                self._state
            ]

            if len(frames) > 0:

                self._frame = (
                    self._frame
                    + self._frame_spd * dt
                ) % len(frames)

    # ========================================================
    # DAMAGE
    # ========================================================

    def take_damage(
        self,
        amount: int
    ):

        if (
            self.iframes > 0
            or not self.alive
        ):

            return False

        self.hp = max(
            0,
            self.hp - amount
        )

        self.iframes = IFRAMES

        self._flash = 0.25

        self._particles.emit(
            self.rect.centerx,
            self.rect.centery,
            12,
            (255, 80, 80),
            (2, 5),
            (0.2, 0.5)
        )

        if self.hp <= 0:

            self.alive = False

        return True

    # ========================================================
    # HEAL
    # ========================================================

    def heal(
        self,
        amount: int
    ):

        self.hp = min(
            self.max_hp,
            self.hp + amount
        )

    # ========================================================
    # DRAW PLAYER
    # ========================================================

    def draw(
        self,
        surface: pygame.Surface,
        camera
    ):

        # ====================================================
        # INVULNERABILITY BLINK
        # ====================================================

        visible = True

        if self.iframes > 0:

            visible = (
                int(
                    self.iframes * 10
                ) % 2 == 0
            )

        if not visible:

            return

        # ====================================================
        # CUSTOM SORCERER
        # ====================================================

        if self.custom_player is not None:

            sprite = self.custom_player

            # ------------------------------------------------
            # FACE LEFT
            # ------------------------------------------------

            if self._facing == "left":

                sprite = pygame.transform.flip(
                    sprite,
                    True,
                    False
                )

            # ------------------------------------------------
            # DAMAGE FLASH
            # ------------------------------------------------

            if self._flash > 0:

                sprite = sprite.copy()

                flash = pygame.Surface(
                    sprite.get_size(),
                    pygame.SRCALPHA
                )

                flash.fill(
                    (
                        255,
                        60,
                        60,
                        80
                    )
                )

                sprite.blit(
                    flash,
                    (
                        0,
                        0
                    ),
                    special_flags=pygame.BLEND_RGBA_ADD
                )

            # =================================================
            # CAMERA
            # =================================================

            r = camera.apply(
                self.rect
            )

            # =================================================
            # CENTER PLAYER IMAGE
            # =================================================

            draw_x = (
                r.centerx
                - sprite.get_width() // 2
            )

            draw_y = (
                r.centery
                - sprite.get_height() // 2
            )

            # =================================================
            # DRAW
            # =================================================

            surface.blit(
                sprite,
                (
                    draw_x,
                    draw_y
                )
            )

        # ====================================================
        # ORIGINAL PLAYER FALLBACK
        # ====================================================

        else:

            frames = self._anims[
                self._state
            ]

            if len(frames) > 0:

                frame_idx = int(
                    self._frame
                ) % len(frames)

                sprite = frames[
                    frame_idx
                ]

                r = camera.apply(
                    self.rect
                )

                surface.blit(
                    sprite,
                    r.topleft
                )

        # ====================================================
        # ATTACK
        # ====================================================

        self.attack.draw(
            surface,
            camera
        )

        # ====================================================
        # PARTICLES
        # ====================================================

        self._particles.draw(
            surface,
            camera
        )

    # ========================================================
    # CENTER
    # ========================================================

    @property
    def center(self):

        return self.rect.center