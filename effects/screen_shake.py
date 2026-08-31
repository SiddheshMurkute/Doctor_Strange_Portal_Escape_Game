# effects/screen_shake.py
"""
Trauma-based screen shake.

Uses the classic power-of-two trauma model:
    offset = max_offset * trauma^2 * random(-1, 1)

This produces organic shake that falls off quickly at low trauma
but responds strongly at high trauma (hits, Reality Break, etc.)

Trauma values (add these on events):
    Light hit   +0.15
    Heavy hit   +0.35
    Player hit  +0.25
    Dash        +0.10
    Kill        +0.12
    Boss slam   +0.60
    Reality Break +1.00

Backward compat: old trigger(intensity, duration) still works.
"""

import math
import random


class ScreenShake:

    MAX_OFFSET   = 14     # maximum pixel displacement
    MAX_ROTATION = 2.5    # degrees (available for future use)
    DECAY_RATE   = 1.8    # trauma lost per second

    def __init__(self):
        self._trauma: float = 0.0
        # Legacy fields kept for compatibility
        self.intensity = 0
        self.duration  = 0.0

    # ------------------------------------------------------------------
    # PRIMARY API — trauma-based
    # ------------------------------------------------------------------

    def add_trauma(self, amount: float) -> None:
        """Add to trauma (0–1, clamped)."""
        self._trauma = min(1.0, self._trauma + amount)
        # Keep legacy intensity in sync for any code still reading it
        self.intensity = int(self._trauma * self.MAX_OFFSET)

    def update(self, dt: float) -> None:
        if self._trauma > 0:
            self._trauma = max(0.0, self._trauma - self.DECAY_RATE * dt)
            self.intensity = int(self._trauma * self.MAX_OFFSET)
            if self._trauma <= 0:
                self.duration = 0.0

    def get_offset(self) -> tuple[int, int]:
        if self._trauma <= 0:
            return (0, 0)
        shake = self._trauma * self._trauma   # power-of-two falloff
        ox = int(self.MAX_OFFSET * shake * random.uniform(-1.0, 1.0))
        oy = int(self.MAX_OFFSET * shake * random.uniform(-1.0, 1.0))
        return (ox, oy)

    # ------------------------------------------------------------------
    # LEGACY COMPAT — old trigger(intensity, duration) interface
    # ------------------------------------------------------------------

    def trigger(self, intensity: int, duration: float) -> None:
        """Legacy API shim — converts to trauma."""
        trauma_equiv = intensity / self.MAX_OFFSET
        self.add_trauma(trauma_equiv)
        # keep duration so old code reading it doesn't break
        if duration > self.duration:
            self.duration = duration

    @property
    def active(self) -> bool:
        return self._trauma > 0.0
