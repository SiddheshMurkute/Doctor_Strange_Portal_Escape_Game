# effects/glow.py
import pygame

def draw_glow(surface, center, radius, color, intensity=180):
    """Draw a soft radial glow at center."""
    glow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for r in range(radius, 0, -max(1, radius//12)):
        alpha = int(intensity * (1 - r/radius)**1.5)
        pygame.draw.circle(glow, (*color[:3], alpha), (radius, radius), r)
    surface.blit(glow, (center[0]-radius, center[1]-radius), special_flags=pygame.BLEND_RGBA_ADD)
