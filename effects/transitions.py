# effects/transitions.py
import pygame

class FadeTransition:
    """Simple black fade-in / fade-out."""
    def __init__(self):
        self.alpha  = 0
        self.fading = False  # True = fade out (darken), False = fade in (brighten)
        self.speed  = 300    # alpha units/second
        self.done   = True
        self._surf  = None

    def start_fade_out(self, speed=300):
        self.alpha  = 0
        self.fading = True
        self.speed  = speed
        self.done   = False

    def start_fade_in(self, speed=300):
        self.alpha  = 255
        self.fading = False
        self.speed  = speed
        self.done   = False

    def update(self, dt):
        if self.done:
            return
        if self.fading:
            self.alpha = min(255, self.alpha + self.speed * dt)
            if self.alpha >= 255:
                self.done = True
        else:
            self.alpha = max(0, self.alpha - self.speed * dt)
            if self.alpha <= 0:
                self.done = True

    def draw(self, surface):
        if self._surf is None or self._surf.get_size() != surface.get_size():
            self._surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        self._surf.fill((0, 0, 0, int(self.alpha)))
        surface.blit(self._surf, (0, 0))
