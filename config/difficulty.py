# config/difficulty.py

# Main difficulty settings.
#
# Both uppercase and lowercase keys are provided because the current
# game and older EnemyManager versions may use different casing.

_DIFFICULTY_VALUES = {
    "easy": {
        "enemy_count_mult": 0.6,
        "enemy_speed_mult": 0.7,
        "spawn_rate_mult": 0.6,
        "damage_mult": 0.7,
    },
    "medium": {
        "enemy_count_mult": 1.0,
        "enemy_speed_mult": 1.0,
        "spawn_rate_mult": 1.0,
        "damage_mult": 1.0,
    },
    "hard": {
        "enemy_count_mult": 1.5,
        "enemy_speed_mult": 1.3,
        "spawn_rate_mult": 1.4,
        "damage_mult": 1.3,
    },
}

DIFFICULTIES = {
    "EASY": _DIFFICULTY_VALUES["easy"],
    "MEDIUM": _DIFFICULTY_VALUES["medium"],
    "HARD": _DIFFICULTY_VALUES["hard"],

    # Compatibility with older code.
    "easy": _DIFFICULTY_VALUES["easy"],
    "medium": _DIFFICULTY_VALUES["medium"],
    "hard": _DIFFICULTY_VALUES["hard"],

    # Compatibility with an older "normal" value that appeared
    # in the existing project.
    "NORMAL": _DIFFICULTY_VALUES["medium"],
    "normal": _DIFFICULTY_VALUES["medium"],
}

STAGE_SCALE = {
    1: 1.0,
    2: 1.2,
    3: 1.45,
    4: 1.75,
    5: 2.1,
}

DEFAULT_DIFFICULTY = "medium"
