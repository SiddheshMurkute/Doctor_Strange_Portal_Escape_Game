# player/player_animation.py
"""
Procedural Doctor Strange sprites drawn with Pygame primitives.
Returns a dict of animation frames per state.
"""
import pygame
import math

def _draw_strange_frame(state: str, frame: int, size=(64, 80)) -> pygame.Surface:
    """Draw a single Doctor Strange animation frame."""
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)

    # Lerp helper for subtle animations
    t = (math.sin(frame * 0.5) + 1) / 2  # 0..1

    # --- Body (dark blue/black mystical suit) ---
    body_rect = pygame.Rect(w//2 - 11, h//2 - 8, 22, 28)
    pygame.draw.rect(surf, (30, 25, 55), body_rect, border_radius=4)

    # --- Red Cloak ---
    cloak_color = (180, 30, 20)
    cloak_pts = [
        (w//2 - 20, h//2 - 4),
        (w//2 + 20, h//2 - 4),
        (w//2 + 28, h//2 + 30 + (int(t*4) if state=='idle' else 0)),
        (w//2 - 28, h//2 + 30 + (int(t*4) if state=='idle' else 0)),
    ]
    pygame.draw.polygon(surf, cloak_color, cloak_pts)
    pygame.draw.polygon(surf, (220, 60, 40), cloak_pts, 2)

    # Collar
    pygame.draw.rect(surf, (200, 50, 30), (w//2-13, h//2-12, 26, 10), border_radius=3)

    # --- Head ---
    head_y = h//2 - 26 + (int(t*2) if state == 'idle' else 0)
    pygame.draw.ellipse(surf, (220, 180, 140), (w//2-10, head_y, 20, 22))

    # Hair (dark brown)
    pygame.draw.ellipse(surf, (60, 35, 20), (w//2-10, head_y, 20, 12))

    # Beard
    pygame.draw.ellipse(surf, (80, 55, 35), (w//2-7, head_y+12, 14, 9))

    # Eyes (glowing depending on state)
    eye_col = (255, 200, 50) if state in ('attack','portal') else (255, 255, 255)
    pygame.draw.circle(surf, eye_col, (w//2-4, head_y+8), 2)
    pygame.draw.circle(surf, eye_col, (w//2+4, head_y+8), 2)

    # --- Legs ---
    leg_y = body_rect.bottom
    offset = int(math.sin(frame * 1.2) * 5) if state == 'walk' else 0
    pygame.draw.rect(surf, (25, 20, 50), (w//2-9, leg_y, 8, 18+offset), border_radius=3)
    pygame.draw.rect(surf, (25, 20, 50), (w//2+1, leg_y, 8, 18-offset), border_radius=3)
    # Boots
    pygame.draw.rect(surf, (15, 10, 35), (w//2-11, leg_y+14+offset, 10, 6), border_radius=2)
    pygame.draw.rect(surf, (15, 10, 35), (w//2+1,  leg_y+14-offset, 10, 6), border_radius=2)

    # --- Arms + Hands ---
    arm_col = (30, 25, 55)
    hand_col = (255, 180, 50) if state == 'attack' else (220, 180, 140)

    # Walk arm swing
    arm_swing = int(math.sin(frame * 1.2) * 6) if state == 'walk' else 0

    # Left arm
    lax, lay = w//2 - 16, h//2 - 4
    pygame.draw.line(surf, arm_col, (lax, lay), (lax - 6, lay + 14 + arm_swing), 5)
    pygame.draw.circle(surf, hand_col, (lax - 6, lay + 18 + arm_swing), 5)

    # Right arm
    rax, ray = w//2 + 16, h//2 - 4
    pygame.draw.line(surf, arm_col, (rax, ray), (rax + 6, ray + 14 - arm_swing), 5)
    pygame.draw.circle(surf, hand_col, (rax + 6, ray + 18 - arm_swing), 5)

    # Mandala rings on hands when attacking
    if state == 'attack':
        ri = int(frame % 6)
        pygame.draw.circle(surf, (255, 200+ri*5, 50), (lax-6, lay+18+arm_swing), 9+ri, 2)
        pygame.draw.circle(surf, (255, 150, 0), (rax+6, ray+18-arm_swing), 9+ri, 2)

    # Damage flash
    if state == 'damage':
        flash = pygame.Surface(size, pygame.SRCALPHA)
        flash.fill((255, 50, 50, 130))
        surf.blit(flash, (0, 0))

    # Death dim
    if state == 'death':
        t2 = min(1.0, frame / 6)
        dim = pygame.Surface(size, pygame.SRCALPHA)
        dim.fill((0, 0, 0, int(200 * t2)))
        surf.blit(dim, (0, 0))

    return surf


def build_animations(size=(64, 80)) -> dict:
    """Build all animation frame lists."""
    anims = {}
    states = {
        'idle':   8,
        'walk':   8,
        'attack': 6,
        'damage': 4,
        'death':  8,
        'portal': 6,
    }
    for state, n_frames in states.items():
        anims[state] = [_draw_strange_frame(state, f, size) for f in range(n_frames)]
    return anims
