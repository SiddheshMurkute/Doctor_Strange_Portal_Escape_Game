# core/level_manager.py
from config.stages import STAGE_CONFIG

class LevelManager:
    """Tracks current stage, accumulated score, and total time across all stages."""

    TOTAL_STAGES = 5

    def __init__(self):
        self.current_stage = 1
        self.total_score   = 0
        self.total_time_elapsed = 0.0   # seconds used across all stages
        self.difficulty    = "MEDIUM"
        self.stage_kills   = 0          # kills this stage for cap enforcement

    def reset(self):
        self.current_stage      = 1
        self.total_score        = 0
        self.total_time_elapsed = 0.0
        self.stage_kills        = 0

    def add_score(self, pts: int):
        self.total_score = max(0, self.total_score + pts)

    def add_elapsed(self, secs: float):
        self.total_time_elapsed += secs

    def advance_stage(self):
        self.current_stage += 1
        self.stage_kills = 0

    def is_final_stage(self) -> bool:
        return self.current_stage == self.TOTAL_STAGES

    def is_complete(self) -> bool:
        return self.current_stage > self.TOTAL_STAGES

    def stage_timer(self) -> int:
        return STAGE_CONFIG[self.current_stage]["timer"]
