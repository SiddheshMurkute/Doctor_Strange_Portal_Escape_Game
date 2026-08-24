# effects/screen_shake.py
import random

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration  = 0.0

    def trigger(self, intensity: int, duration: float):
        if intensity > self.intensity:
            self.intensity = intensity
            self.duration  = duration

    def update(self, dt: float):
        if self.duration > 0:
            self.duration -= dt
        else:
            self.intensity = 0

    def get_offset(self):
        if self.intensity > 0:
            return (random.randint(-self.intensity, self.intensity),
                    random.randint(-self.intensity, self.intensity))
        return (0, 0)
