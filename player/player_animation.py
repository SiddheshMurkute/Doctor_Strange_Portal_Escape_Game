# player/player_animation.py
"""
Procedural Doctor Strange sprites drawn with Pygame primitives.
Returns a dict of animation frames per state.
"""
import pygame
import math

def _draw_strange_frame(state: str, frame: int, size=(64, 80)) -> pygame.Surface:
    """Draw a single Doctor Strange animation frame with more detail/shading."""
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)

    t = (math.sin(frame * 0.5) + 1) / 2  # 0..1 idle breathing

    cx = w // 2
    walk_bob = int(math.sin(frame * 1.2) * 2) if state == 'walk' else 0
    body_top = h // 2 - 8 + walk_bob

    # CLOAK OF LEVITATION (drawn first, behind body)
    cloak_sway = math.sin(frame * 0.4) * 6 if state in ('idle', 'walk') else 0
    cloak_flare = 10 if state in ('attack', 'portal') else 0
    cloak_dark = (120, 18, 14)
    cloak_mid  = (180, 30, 20)
    cloak_light = (225, 70, 45)

    cloak_pts = [
        (cx - 19, body_top - 2),
        (cx + 19, body_top - 2),
        (cx + 27 + cloak_flare, body_top + 34 + cloak_sway),
        (cx + 10, body_top + 30 + cloak_sway * 0.6),
        (cx,      body_top + 34 + cloak_sway * 0.3),
        (cx - 10, body_top + 30 + cloak_sway * 0.6),
        (cx - 27 - cloak_flare, body_top + 34 + cloak_sway),
    ]
    pygame.draw.polygon(surf, cloak_dark, cloak_pts)
    inner_cloak_pts = [(x, y - 4) for x, y in cloak_pts[1:-1]]
    pygame.draw.polygon(surf, cloak_mid, [cloak_pts[0]] + inner_cloak_pts + [cloak_pts[-1]])
    pygame.draw.lines(surf, cloak_light, False, cloak_pts, 2)

    pygame.draw.polygon(surf, cloak_mid, [
        (cx - 15, body_top - 2), (cx - 19, body_top - 14), (cx - 9, body_top - 4)
    ])
    pygame.draw.polygon(surf, cloak_mid, [
        (cx + 15, body_top - 2), (cx + 19, body_top - 14), (cx + 9, body_top - 4)
    ])

    # BODY (tunic)
    body_rect = pygame.Rect(cx - 10, body_top, 20, 26)
    pygame.draw.rect(surf, (24, 20, 46), body_rect, border_radius=5)
    pygame.draw.rect(surf, (40, 34, 68), (body_rect.x + 2, body_rect.y + 2, 8, body_rect.height - 4), border_radius=3)

    pygame.draw.rect(surf, (200, 160, 60), (cx - 10, body_top + 16, 20, 3))
    pygame.draw.line(surf, (200, 160, 60), (cx, body_top + 2), (cx, body_top + 24), 2)

    amulet_glow = (120, 220, 255) if state in ('attack', 'portal') else (90, 170, 200)
    pygame.draw.circle(surf, (60, 45, 20), (cx, body_top + 8), 4)
    pygame.draw.circle(surf, amulet_glow, (cx, body_top + 8), 2)

    # HEAD
    head_y = body_top - 20 + (int(t * 2) if state == 'idle' else 0)
    skin = (215, 172, 135)
    skin_shadow = (185, 142, 108)
    pygame.draw.ellipse(surf, skin, (cx - 9, head_y, 18, 20))
    pygame.draw.ellipse(surf, skin_shadow, (cx - 3, head_y + 9, 10, 10))

    pygame.draw.ellipse(surf, (50, 48, 52), (cx - 9, head_y - 1, 18, 10))
    pygame.draw.arc(surf, (150, 150, 155), (cx - 9, head_y - 1, 18, 10), 3.6, 5.8, 2)

    beard_pts = [(cx - 6, head_y + 11), (cx + 6, head_y + 11), (cx + 3, head_y + 18), (cx - 3, head_y + 18)]
    pygame.draw.polygon(surf, (60, 58, 62), beard_pts)

    pygame.draw.line(surf, (40, 38, 42), (cx - 6, head_y + 7), (cx - 2, head_y + 6), 1)
    pygame.draw.line(surf, (40, 38, 42), (cx + 2, head_y + 6), (cx + 6, head_y + 7), 1)

    eye_col = (150, 230, 255) if state in ('attack', 'portal') else (255, 255, 255)
    pygame.draw.circle(surf, eye_col, (cx - 3, head_y + 9), 2)
    pygame.draw.circle(surf, eye_col, (cx + 3, head_y + 9), 2)

    # LEGS / BOOTS
    leg_y = body_rect.bottom
    offset = int(math.sin(frame * 1.2) * 5) if state == 'walk' else 0
    pygame.draw.rect(surf, (22, 18, 40), (cx - 8, leg_y, 7, 16 + offset), border_radius=3)
    pygame.draw.rect(surf, (22, 18, 40), (cx + 1, leg_y, 7, 16 - offset), border_radius=3)
    pygame.draw.rect(surf, (12, 10, 26), (cx - 9, leg_y + 12 + offset, 9, 6), border_radius=2)
    pygame.draw.rect(surf, (12, 10, 26), (cx + 1, leg_y + 12 - offset, 9, 6), border_radius=2)

    # ARMS + HANDS + spellcasting rings
    arm_col = (30, 25, 55)
    hand_col = (255, 190, 70) if state == 'attack' else skin
    arm_swing = int(math.sin(frame * 1.2) * 6) if state == 'walk' else 0

    lax, lay = cx - 15, body_top + 4
    pygame.draw.line(surf, arm_col, (lax, lay), (lax - 6, lay + 13 + arm_swing), 5)
    pygame.draw.circle(surf, hand_col, (lax - 6, lay + 17 + arm_swing), 4)

    rax, ray = cx + 15, body_top + 4
    pygame.draw.line(surf, arm_col, (rax, ray), (rax + 6, ray + 13 - arm_swing), 5)
    pygame.draw.circle(surf, hand_col, (rax + 6, ray + 17 - arm_swing), 4)

    if state == 'attack':
        ri = int(frame % 6)
        pygame.draw.circle(surf, (140, 220, 255), (lax - 6, lay + 17 + arm_swing), 8 + ri, 2)
        pygame.draw.circle(surf, (255, 170, 60), (rax + 6, ray + 17 - arm_swing), 8 + ri, 2)

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
