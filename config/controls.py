# config/controls.py
import pygame

MOVE_UP    = [pygame.K_w, pygame.K_UP]
MOVE_DOWN  = [pygame.K_s, pygame.K_DOWN]
MOVE_LEFT  = [pygame.K_a, pygame.K_LEFT]
MOVE_RIGHT = [pygame.K_d, pygame.K_RIGHT]
ATTACK     = [pygame.K_SPACE]
INTERACT   = [pygame.K_e]
DEFLECT    = [pygame.K_r]
PAUSE      = [pygame.K_ESCAPE]
FULLSCREEN = [pygame.K_F11]
CONFIRM    = [pygame.K_RETURN, pygame.K_KP_ENTER]
# ============================================================
# GAMEPAD SUPPORT
# ============================================================

pygame.joystick.init()

def get_active_joystick():
    """Returns the first connected joystick, or None if none connected."""
    if pygame.joystick.get_count() > 0:
        joy = pygame.joystick.Joystick(0)
        joy.init()
        return joy
    return None

GAMEPAD_BUTTON = {
    "ATTACK":        0,
    "DASH":          1,
    "REALITY_BREAK": 7,
}

GAMEPAD_AXIS_MOVE_X = 0
GAMEPAD_AXIS_MOVE_Y = 1
GAMEPAD_AXIS_AIM_X  = 2
GAMEPAD_AXIS_AIM_Y  = 3

GAMEPAD_DEADZONE = 0.18