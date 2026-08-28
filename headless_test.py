import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import sys
import time

# Ensure project root in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.settings import FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from core.game_state import GameState

def run_headless_tests():
    # Initialize basic dummy window and mock display
    pygame.init()
    pygame.display.set_mode((1, 1))

    try:
        game = Game()
    except Exception as e:
        print(f"FAILED TO INIT GAME: {e}")
        return False

    print("Game Initialized successfully.")

    frames = 0
    max_frames = 60 * 10 # 10 seconds of simulation max

    mock_keys = {k: 0 for k in range(512)}
    def _mock_get_pressed():
        # returns an array-like sequence
        return [mock_keys.get(k, 0) for k in range(512)]
    pygame.key.get_pressed = _mock_get_pressed

    def mock_event(type, key=None):
        ev = pygame.event.Event(type)
        if key is not None:
            ev.key = key
            if type == pygame.KEYDOWN:
                mock_keys[key] = 1
            elif type == pygame.KEYUP:
                mock_keys[key] = 0
        return ev

    try:
        while game.running and frames < max_frames:
            dt = 1.0 / FPS
            events = []
            
            # Send events based on state to progress through the game
            s = game.state
            if frames == 5:
                # Main Menu -> Difficulty Select
                events = [mock_event(pygame.KEYUP, pygame.K_RETURN)]
                # set main_menu selected to 'PLAY' (0)
                game.main_menu.selected = 0
                game.main_menu.handle_event(mock_event(pygame.KEYDOWN, pygame.K_RETURN), (0,0))
                print("Transitioning to PLAY")

            elif frames == 10 and s == GameState.DIFFICULTY_SELECT:
                # Select difficulty and start
                game.diff_menu.handle_event(mock_event(pygame.KEYDOWN, pygame.K_RETURN), (0,0))
                print("Transitioning to STAGE INTRO")
                
            elif frames == 15 and s == GameState.STAGE_INTRO:
                # Start stage
                game.stage_intro_ui.handle_event(mock_event(pygame.KEYDOWN, pygame.K_RETURN))
                print("Transitioning to PLAYING")

            elif frames > 20 and s == GameState.PLAYING:
                import random
                # Mash movement, attack, interact keys randomly
                # possible keys: W, A, S, D, Q (attack), E (interact)
                action_keys = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_q, pygame.K_e]
                if random.random() < 0.2:
                    events.append(mock_event(pygame.KEYDOWN, random.choice(action_keys)))
                if random.random() < 0.2:
                    events.append(mock_event(pygame.KEYUP, random.choice(action_keys)))
                
                # Mock a correct portal interaction randomly later
                if frames == 250:
                    print("Simulating correct portal interaction")
                    # We can directly hack the state to trigger portal result
                    game._portal_result_result = 'correct'
                    game.portal_result_ui.show('correct', 100, 1.0)
                    game.state = GameState.PORTAL_RESULT
            
            elif frames > 30 and s == GameState.PORTAL_RESULT:
                # skip portal result logic
                game.portal_result_ui.continue_flag = True

            keys = pygame.key.get_pressed()
            mouse = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

            for ev in events:
                game._handle_state_event(ev, keys, mouse)

            game._update(dt, keys)
            game._draw()
            frames += 1

        print("Headless tests completed without crashes.")
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CRASH ON FRAME {frames} IN STATE {game.state}")
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = run_headless_tests()
    sys.exit(0 if success else 1)
