# ============================================================
# DOCTOR STRANGE PLAYER
# player/player.py
# ============================================================

import pygame
import math
import os
import random

from config.controls import (
    MOVE_LEFT, MOVE_RIGHT, MOVE_UP, MOVE_DOWN,
        ATTACK, INTERACT, DEFLECT
)
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from player.player_animation import build_animations
from player.player_attack import BoltsOfBalthakk
from core.collision import collide_rects
from core.momentum import Momentum
from effects.particles import ParticleSystem


# ============================================================
# SETTINGS
# ============================================================

PLAYER_SPEED     = 230      # px/s normal
PLAYER_HP        = 100
IFRAMES          = 0.65     # seconds after taking damage
DAMAGE_PER_HIT   = 5

# Dash
DASH_SPEED       = 500      # px/s burst
DASH_DURATION    = 0.18     # seconds
DASH_COOLDOWN    = 0.80     # seconds
DASH_IFRAMES     = 0.40     # iframes during dash (> dash duration → brief window)

# Reality Break
RB_DURATION      = 2.0      # seconds of Reality Break effect
RB_STAGGER_RANGE = 400      # px radius to stagger enemies

# Dash key
DASH_KEYS = [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_SPACE]
RB_KEY    = pygame.K_q


class Player:

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self, x: int, y: int):

        # ------- collision -------
        self.SIZE = (64, 80)
        self.rect = pygame.Rect(x, y, self.SIZE[0], self.SIZE[1])
        self._fx   = float(x)    # float position for sub-pixel accuracy
        self._fy   = float(y)

        self.vel   = pygame.Vector2(0.0, 0.0)

        # ------- health -------
        self.hp      = PLAYER_HP
        self.max_hp  = PLAYER_HP
        self.alive   = True
        self.iframes = 0.0

        # ------- animations -------
        self._anims      = build_animations(self.SIZE)
        self._state      = "idle"
        self._frame      = 0.0
        self._frame_spd  = 6.0
        self._facing     = "right"

        # ------- custom image -------
        self.custom_player = None
        self.load_custom_player()

        # ------- attack -------
        self.attack = BoltsOfBalthakk()

        # ------- dash -------
        self._dashing        = False
        self._dash_timer     = 0.0
        self._dash_cooldown  = 0.0
        self._dash_vel       = pygame.Vector2(0.0, 0.0)
        self._dash_particles = ParticleSystem()
        self._dash_afterimages: list[dict] = []

        # ------- momentum -------
        self.momentum = Momentum()

        # ------- Reality Break -------
        self._rb_active  = False
        self._rb_timer   = 0.0
        self._rb_surface = None   # mirror-dimension overlay (built lazily)

        # ------- Deflect (Tao Mandala) -------
        self._deflect_active = False
        self._deflect_timer  = 0.0
        self._deflect_window = 0.12
        self._deflect_cooldown = 0.0
        self._prev_deflect_key = False

        # ------- particles -------
        self._particles  = ParticleSystem()

        # ------- visual -------
        self._flash      = 0.0   # damage red flash
        self._hit_white  = 0.0   # hit-white flash (brief)

        # ------- fragment count -------
        self.fragments_collected = 0

        # ------- aim -------
        self._aim_angle = 0.0    # radians; updated from mouse each frame

    # ========================================================
    # CUSTOM IMAGE LOADER (unchanged)
    # ========================================================

    def load_custom_player(self):
        current_file = os.path.abspath(__file__)
        player_folder = os.path.dirname(current_file)
        project_folder = os.path.dirname(player_folder)
        player_folder_path = os.path.join(project_folder, "assets", "player")

        possible_images = [
            "doctor_strange_player.jpeg",
            "doctor_strange_player.jpg",
            "doctor_strange_player.png",
        ]

        image_path = None

        for filename in possible_images:
            test_path = os.path.join(player_folder_path, filename)

            if os.path.isfile(test_path):
                image_path = test_path
                break

        if image_path is None:
            print("PLAYER IMAGE NOT FOUND")
            return
        print("PLAYER IMAGE FOUND:", image_path)

        try:
            image = pygame.image.load(image_path).convert()
        except Exception:
            return

        image = image.convert_alpha()

        w, h = image.get_width(), image.get_height()

        for y in range(h):
            for x in range(w):
                r, g, b, a = image.get_at((x, y))

                if r > 220 and g > 220 and b > 220:
                    image.set_at((x, y), (r, g, b, 0))

        PLAYER_WIDTH  = 120
        PLAYER_HEIGHT = 145
        image         = pygame.transform.smoothscale(image, (PLAYER_WIDTH, PLAYER_HEIGHT))

        self.custom_player = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        self.custom_player.fill((0, 0, 0, 0))
        self.custom_player.blit(image, (0, 0))

    # ========================================================
    # INPUT
    # ========================================================

    def handle_input(self, keys, dt: float, mouse_pos=None, camera=None, events=None) -> None:
        if not self.alive:
            return

        # --- Movement direction ---
        dx, dy = 0.0, 0.0

        if any(keys[k] for k in MOVE_LEFT):
            dx -= 1.0
            self._facing = "left"

        if any(keys[k] for k in MOVE_RIGHT):
            dx += 1.0
            self._facing = "right"

        if any(keys[k] for k in MOVE_UP):
            dy -= 1.0
            if dx == 0:
                self._facing = "up"

        if any(keys[k] for k in MOVE_DOWN):
            dy += 1.0
            if dx == 0:
                self._facing = "down"

        # Diagonal normalise
        if dx != 0 and dy != 0:
            mag = math.sqrt(2)
            dx /= mag
            dy /= mag

        # --- Aim: prefer mouse, fallback to facing ---
        if mouse_pos is not None and camera is not None:
            world_mouse = camera.world_pos(mouse_pos)
            mdx = world_mouse[0] - self.rect.centerx
            mdy = world_mouse[1] - self.rect.centery
            dist = math.hypot(mdx, mdy)
            if dist > 5:
                self._aim_angle = math.atan2(mdy, mdx)
                #   Update facing for flip
                if abs(mdx) >= abs(mdy):
                    self._facing = "right" if mdx >= 0 else "left"
        else:
            # Fallback facing → angle
            dirs = {"right": 0.0, "left": math.pi,
                    "up": -math.pi / 2, "down": math.pi / 2}
            self._aim_angle = dirs.get(self._facing, 0.0)

        # --- Velocity (unless dashing) ---
        if not self._dashing:
            speed = PLAYER_SPEED * self.momentum.bonuses["speed_mult"]
            self.vel.x = dx * speed
            self.vel.y = dy * speed

        # Signal momentum that player is active
        if dx != 0 or dy != 0 or self.attack.active:
            self.momentum.signal_active()

        # --- Dash ---
        dash_pressed = any(keys[k] for k in DASH_KEYS)
        if dash_pressed and self._dash_cooldown <= 0 and not self._dashing:
            self._start_dash(dx, dy)

        # --- Attack: detect held fire button ---
        fire_held = any(keys[k] for k in ATTACK)
        # Also support left mouse button
        try:
            fire_held = fire_held or pygame.mouse.get_pressed()[0]
        except Exception:
            pass

        if fire_held and not self._dashing:
            origin = (float(self.rect.centerx), float(self.rect.centery))
            fired  = self.attack.try_fire(origin, self._aim_angle)
            if fired:
                self.momentum.signal_active()
        # --- Deflect (Tao Mandala) ---
        deflect_key_down = any(keys[k] for k in DEFLECT)
        if deflect_key_down and not self._prev_deflect_key and self._deflect_cooldown <= 0:
            self._deflect_active = True
            self._deflect_timer  = self._deflect_window
            self._deflect_cooldown = 0.6   # tune later
            self._prev_deflect_key = deflect_key_down
            print("DEFLECT ACTIVE")

        # --- Reality Break ---
        try:
            rb_pressed = bool(keys[RB_KEY])
        except Exception:
            rb_pressed = False
        if rb_pressed and self.momentum.reality_break_ready and not self._rb_active:
            self._activate_reality_break()

        # --- Animation state ---
        if not self.alive:
            self._state = "death"
        elif self._dashing:
            self._state = "walk"
        elif self._flash > 0:
            self._state = "damage"
        elif self.attack.active:
            self._state = "attack"
        elif dx != 0 or dy != 0:
            self._state = "walk"
        else:
            self._state = "idle"

    # ========================================================
    # DASH
    # ========================================================

    def _start_dash(self, dx: float, dy: float) -> None:
        # Determine direction
        if abs(dx) + abs(dy) < 0.01:
            # Dash toward aim if not moving
            dx = math.cos(self._aim_angle)
            dy = math.sin(self._aim_angle)

        self._dashing       = True
        self._dash_timer    = DASH_DURATION
        self.iframes        = max(self.iframes, DASH_IFRAMES)
        self._dash_vel      = pygame.Vector2(dx * DASH_SPEED, dy * DASH_SPEED)
        self.vel            = pygame.Vector2(self._dash_vel)

        # Store afterimage
        self._dash_afterimages.append({
            "x": self._fx,
            "y": self._fy,
            "alpha": 180,
            "facing": self._facing,
        })

        # Dash particles
        self._dash_particles.emit(
            self.rect.centerx, self.rect.centery,
            18, (130, 180, 255), speed_range=(2, 7), life_range=(0.15, 0.4)
        )
        self.momentum.signal_active()

    # ========================================================
    # REALITY BREAK
    # ========================================================

    def _activate_reality_break(self) -> None:
        if not self.momentum.spend_reality_break():
            return
        self._rb_active = True
        self._rb_timer  = RB_DURATION
        # Build overlay surface (mirror-dimension geometry)
        self._rb_surface = self._build_rb_surface()

    def _build_rb_surface(self) -> pygame.Surface:
        """Build a sacred-geometry overlay for Reality Break."""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        # Concentric hexagonal rings
        for i in range(6):
            r     = 80 + i * 80
            alpha = max(20, 80 - i * 12)
            col   = (100 + i * 25, 0, 255 - i * 30, alpha)
            points = []
            for k in range(6):
                angle = math.radians(60 * k + 30)
                px    = cx + int(math.cos(angle) * r)
                py    = cy + int(math.sin(angle) * r)
                points.append((px, py))
            pygame.draw.polygon(surf, col, points, 2)
        # Cross beams
        for angle_deg in range(0, 180, 30):
            ang = math.radians(angle_deg)
            x1  = cx + int(math.cos(ang) * 500)
            y1  = cy + int(math.sin(ang) * 500)
            x2  = cx - int(math.cos(ang) * 500)
            y2  = cy - int(math.sin(ang) * 500)
            pygame.draw.line(surf, (180, 0, 255, 40), (x1, y1), (x2, y2), 1)
        return surf

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt: float, walls: list, world_rect: pygame.Rect) -> None:

        # --- iframes ---
        if self.iframes > 0:
            self.iframes -= dt

        # --- damage flash ---
        if self._flash > 0:
            self._flash -= dt

        # --- dash timer ---
        if self._dashing:
            self._dash_timer -= dt
            if self._dash_timer <= 0:
                self._dashing = False
                self.vel.x = 0.0
                self.vel.y = 0.0
                # Landing particle burst
                self._dash_particles.emit(
                    self.rect.centerx, self.rect.centery,
                    10, (160, 200, 255), speed_range=(1, 4), life_range=(0.1, 0.25)
                )

        if self._dash_cooldown > 0:
            self._dash_cooldown -= dt
            if self._dash_cooldown < 0:
                self._dash_cooldown = 0.0

        # Start cooldown the moment dash ends
        if not self._dashing and self._dash_cooldown <= 0:
            pass   # handled by _start_dash setting timer

        # --- Reality Break timer ---
        if self._rb_active:
            self._rb_timer -= dt
            if self._rb_timer <= 0:
                self._rb_active  = False
                self._rb_surface = None
        # --- Deflect timers ---
        if self._deflect_active:
            self._deflect_timer -= dt
            if self._deflect_timer <= 0:
                self._deflect_active = False
        if self._deflect_cooldown > 0:
            self._deflect_cooldown -= dt

        # --- float-position movement ---
        self._fx += self.vel.x * dt
        self._fy += self.vel.y * dt

        # Sync rect (x axis)
        self.rect.x = int(round(self._fx))
        mtv = collide_rects(self.rect, walls)
        if mtv.x != 0:
            self._fx    += mtv.x
            self.rect.x  = int(round(self._fx))
            if self._dashing:
                self.vel.x = 0

        # y axis
        self.rect.y = int(round(self._fy))
        mtv = collide_rects(self.rect, walls)
        if mtv.y != 0:
            self._fy    += mtv.y
            self.rect.y  = int(round(self._fy))
            if self._dashing:
                self.vel.y = 0

        # World boundary
        self.rect.clamp_ip(world_rect)
        self._fx = float(self.rect.x)
        self._fy = float(self.rect.y)

        # --- attack update ---
        self.attack.update(dt, self.rect)

        # --- particles ---
        self._particles.update(dt)
        self._dash_particles.update(dt)

        # --- dash cooldown reset when dash ends ---
        # (We set cooldown only once per dash, at the start)

        # --- afterimages fade ---
        alive_ai = []
        for ai in self._dash_afterimages:
            ai["alpha"] -= 220 * dt
            if ai["alpha"] > 0:
                alive_ai.append(ai)
        self._dash_afterimages = alive_ai

        # --- momentum ---
        self.momentum.update(dt)

        # --- animation frame ---
        if self._state in self._anims:
            frames = self._anims[self._state]
            if frames:
                self._frame = (self._frame + self._frame_spd * dt) % len(frames)

    # ========================================================
    # DAMAGE
    # ========================================================

    def take_damage(self, amount: int) -> bool:
        if self.iframes > 0 or not self.alive:
            return False

        self.hp      = max(0, self.hp - amount)
        self.iframes = IFRAMES
        self._flash  = 0.28

        self._particles.emit(
            self.rect.centerx, self.rect.centery,
            14, (255, 80, 80), speed_range=(2, 6), life_range=(0.2, 0.5)
        )
        self.momentum.on_damage()

        if self.hp <= 0:
            self.alive = False

        return True

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self, surface: pygame.Surface, camera) -> None:

        # --- Afterimages (behind player) ---
        if self.custom_player is not None:
            for ai in self._dash_afterimages:
                ghost = self.custom_player.copy()
                ghost.set_alpha(int(ai["alpha"]))
                if ai["facing"] == "left":
                    ghost = pygame.transform.flip(ghost, True, False)
                gx = int(ai["x"]) - int(camera.offset_x) - ghost.get_width()  // 2
                gy = int(ai["y"]) - int(camera.offset_y) - ghost.get_height() // 2
                surface.blit(ghost, (gx, gy))

        # --- Dash particles (behind player) ---
        self._dash_particles.draw(surface, camera)

        # --- Blink during iframes (not during dash) ---
        if self.iframes > 0 and not self._dashing:
            if int(self.iframes * 12) % 2 == 0:
                return   # skip frame → blink

        # --- Main sprite ---
        if self.custom_player is not None:
            sprite = self.custom_player

            if self._facing == "left":
                sprite = pygame.transform.flip(sprite, True, False)

            # Damage flash overlay
            if self._flash > 0:
                sprite = sprite.copy()
                fl     = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                fl.fill((255, 60, 60, 90))
                sprite.blit(fl, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            r     = camera.apply(self.rect)
            draw_x = r.centerx - sprite.get_width()  // 2
            draw_y = r.centery - sprite.get_height() // 2
            surface.blit(sprite, (draw_x, draw_y))

        else:
            # Procedural fallback
            frames = self._anims.get(self._state, [])
            if frames:
                idx    = int(self._frame) % len(frames)
                sprite = frames[idx]
                r      = camera.apply(self.rect)
                surface.blit(sprite, r.topleft)

        # --- Attack effect ---
        if hasattr(self.attack, "draw"):
            self.attack.draw(surface, camera)

        # --- Particles ---
        self._particles.draw(surface, camera)

        # --- Reality Break overlay ---
        if self._rb_active and self._rb_surface:
            frac   = self._rb_timer / RB_DURATION
            alpha  = int(220 * frac)
            overlay = self._rb_surface.copy()
            overlay.set_alpha(alpha)
            surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def draw_ui(self, surface: pygame.Surface) -> None:
        """Draw aim reticle and dash cooldown ring near player (screen-space)."""
        pass   # Extended in HUD

    # ========================================================
    # DASH COOLDOWN FRACTION (for HUD)
    # ========================================================

    @property
    def dash_cooldown_pct(self) -> float:
        if DASH_COOLDOWN <= 0:
            return 0.0
        return max(0.0, min(1.0, self._dash_cooldown / DASH_COOLDOWN))

    # ========================================================
    # NOTIFY DASH COOLDOWN START
    # ========================================================

    def start_dash_cooldown(self) -> None:
        self._dash_cooldown = DASH_COOLDOWN