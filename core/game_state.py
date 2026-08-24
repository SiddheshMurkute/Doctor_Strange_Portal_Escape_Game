# core/game_state.py
from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU        = auto()
    DIFFICULTY_SELECT= auto()
    HOW_TO_PLAY      = auto()
    STAGE_INTRO      = auto()
    PLAYING          = auto()
    PORTAL_RESULT    = auto()
    STAGE_COMPLETE   = auto()
    PLAYER_DEFEATED  = auto()
    STAGE_FAILED     = auto()
    PAUSED           = auto()
    FINAL_ESCAPE     = auto()
    FINAL_RESULT     = auto()
