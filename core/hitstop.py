# core/hitstop.py
"""
Centralized hitstop service.

When hitstop is active the simulation receives dt=0 so all physics
and AI pause, while rendering continues at full speed.

Usage:
    from core.hitstop import hitstop
    hitstop.trigger(HitstopDuration.KILL)   # activate
    effective_dt = hitstop.update(dt)        # in game loop
    if hitstop.active: ...                   # query
"""

import math


class HitstopDuration:
    """Preset durations in seconds."""
    LIGHT  = 0.040   # light enemy hit
    HEAVY  = 0.090   # heavy hit / player hit
    KILL   = 0.120   # enemy killed
    DASH   = 0.030   # dash impact
    REALITY_BREAK = 0.250   # Reality Break activation


class _HitstopService:
    """Singleton hitstop service."""

    def __init__(self):
        self._remaining: float = 0.0

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def trigger(self, duration: float) -> None:
        """
        Start (or extend) a hitstop freeze.
        Only extends if the new duration is longer than what's left.
        """
        if duration > self._remaining:
            self._remaining = duration

    def update(self, dt: float) -> float:
        """
        Call once per game frame.
        Returns the effective dt that simulation systems should use:
            0.0  while frozen
            dt   when not frozen
        """
        if self._remaining > 0:
            self._remaining -= dt
            if self._remaining < 0:
                self._remaining = 0.0
            return 0.0
        return dt

    @property
    def active(self) -> bool:
        return self._remaining > 0

    def reset(self) -> None:
        self._remaining = 0.0


# Module-level singleton
hitstop = _HitstopService()
