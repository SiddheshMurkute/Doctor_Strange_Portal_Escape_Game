# core/momentum.py
"""
Momentum system — Doctor Strange: Portal Escape

Three tiers based on current momentum value (0–100):
    FOCUSED          ≥ 33  — slight cast improvement
    ASCENDANT        ≥ 66  — better cast speed, slight movement improvement
    SORCERER_SUPREME = 100 — maximum power, Reality Break available

Momentum decays when idle or on taking damage.
Momentum is gained from attacks, kills, dodges, fragments.
"""


# ------------------------------------------------------------------
# CONSTANTS — all tweak-able here
# ------------------------------------------------------------------

MAX_MOMENTUM       = 100.0
DECAY_RATE         = 8.0          # per second when idle (not attacking recently)
DECAY_IDLE_WINDOW  = 1.5          # seconds of no action before decay begins
DAMAGE_PENALTY     = 15.0         # subtracted on taking damage

GAIN_ATTACK_HIT    = 6.0
GAIN_KILL          = 18.0
GAIN_DODGE         = 10.0         # successful dodge (iframes active during hit)
GAIN_FRAGMENT      = 8.0

TIER_FOCUSED          = 33.0
TIER_ASCENDANT        = 66.0
TIER_SORCERER_SUPREME = 100.0      # exact max

# Multipliers granted by tier
TIER_BONUSES = {
    "NONE": {
        "speed_mult": 1.00,
        "cast_rate":  1.00,
        "vfx_scale":  1.00,
    },
    "FOCUSED": {
        "speed_mult": 1.05,
        "cast_rate":  1.15,
        "vfx_scale":  1.10,
    },
    "ASCENDANT": {
        "speed_mult": 1.12,
        "cast_rate":  1.30,
        "vfx_scale":  1.30,
    },
    "SORCERER_SUPREME": {
        "speed_mult": 1.20,
        "cast_rate":  1.50,
        "vfx_scale":  1.60,
    },
}


class Momentum:
    """Per-player Momentum tracker."""

    def __init__(self):
        self._value: float = 0.0
        self._idle_timer: float = 0.0
        self._reality_break_ready: bool = False
        self._reality_break_used: bool = False   # used once per max charge

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------

    @property
    def value(self) -> float:
        return self._value

    @property
    def fraction(self) -> float:
        """0.0 – 1.0"""
        return self._value / MAX_MOMENTUM

    @property
    def tier(self) -> str:
        if self._value >= TIER_SORCERER_SUPREME:
            return "SORCERER_SUPREME"
        if self._value >= TIER_ASCENDANT:
            return "ASCENDANT"
        if self._value >= TIER_FOCUSED:
            return "FOCUSED"
        return "NONE"

    @property
    def bonuses(self) -> dict:
        return TIER_BONUSES[self.tier]

    @property
    def reality_break_ready(self) -> bool:
        return self._reality_break_ready

    # ------------------------------------------------------------------
    # GAINS
    # ------------------------------------------------------------------

    def on_attack_hit(self):
        self._add(GAIN_ATTACK_HIT)

    def on_kill(self):
        self._add(GAIN_KILL)

    def on_dodge(self):
        """Call when player successfully dodges (was in iframes during hit)."""
        self._add(GAIN_DODGE)

    def on_fragment(self):
        self._add(GAIN_FRAGMENT)

    def on_damage(self):
        self._value = max(0.0, self._value - DAMAGE_PENALTY)
        self._reality_break_ready = False
        self._reality_break_used = False
        self._idle_timer = 0.0

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def signal_active(self):
        """Call each frame the player is actively attacking/moving."""
        self._idle_timer = 0.0

    def update(self, dt: float):
        self._idle_timer += dt

        # Decay begins after idle window
        if self._idle_timer > DECAY_IDLE_WINDOW:
            self._value = max(0.0, self._value - DECAY_RATE * dt)

        # Reality Break charge logic
        if (self._value >= TIER_SORCERER_SUPREME
                and not self._reality_break_used
                and not self._reality_break_ready):
            self._reality_break_ready = True

    def spend_reality_break(self) -> bool:
        """Consume the Reality Break charge. Returns True if successful."""
        if not self._reality_break_ready:
            return False
        self._reality_break_ready = False
        self._reality_break_used = True
        # Drop from max so player must re-earn it
        self._value = TIER_ASCENDANT
        return True

    def reset(self):
        self._value = 0.0
        self._idle_timer = 0.0
        self._reality_break_ready = False
        self._reality_break_used = False

    # ------------------------------------------------------------------
    # PRIVATE
    # ------------------------------------------------------------------

    def _add(self, amount: float):
        self._value = min(MAX_MOMENTUM, self._value + amount)
        self._idle_timer = 0.0
        # Re-enable Reality Break if they hit max again after spending
        if self._value >= TIER_SORCERER_SUPREME and self._reality_break_used:
            self._reality_break_used = False
