# config/scoring.py

SCORING = {
    "correct_portal_base":  500,
    "time_bonus_per_sec":   10,      # multiplied by remaining seconds
    "fragment_bonus":       150,
    "wrong_portal_penalty": -100,
    "hazard_hit_penalty":   -20,
    "enemy_kill_bonus":     25,
    "enemy_kill_cap":       20,      # max kills that count toward score per stage
    "final_escape_bonus":   2000,
    "stage_complete_bonus": 300,
}
