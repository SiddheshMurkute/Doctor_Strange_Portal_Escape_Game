# config/difficulty.py

DIFFICULTIES = {
    "EASY": {
        "enemy_count_mult":  0.6,
        "enemy_speed_mult":  0.7,
        "spawn_rate_mult":   0.6,
        "damage_mult":       0.7,
    },
    "MEDIUM": {
        "enemy_count_mult":  1.0,
        "enemy_speed_mult":  1.0,
        "spawn_rate_mult":   1.0,
        "damage_mult":       1.0,
    },
    "HARD": {
        "enemy_count_mult":  1.5,
        "enemy_speed_mult":  1.3,
        "spawn_rate_mult":   1.4,
        "damage_mult":       1.3,
    },
}

# Stage-based difficulty scaling (multiplier applied on top of difficulty mode)
STAGE_SCALE = {
    1: 1.0,
    2: 1.2,
    3: 1.45,
    4: 1.75,
    5: 2.1,
}

DEFAULT_DIFFICULTY = "MEDIUM"
