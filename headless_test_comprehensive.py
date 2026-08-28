import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
import core.game_state

def test_all():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game()
    
    # 1. Test all stages explicitly
    for stage_idx in range(1, 6):
        print(f"Testing Stage {stage_idx} init")
        game.lm.current_stage = stage_idx
        game.lm.difficulty = "MEDIUM"
        game._start_stage(stage_idx)
        
        # Spawn some enemies explicitly to test enemy rendering
        if game.enemy_mgr:
            print("Spawning wave...")
            game.enemy_mgr.spawn_wave(10)
        
        # Test update and drawing
        keys = game.clock.tick()
        mock_keys = {pygame.K_w: 1}  # some random input
        
        class MockKeys:
            def __getitem__(self, k):
                return 1 if k == pygame.K_w else 0
        def mock_get_pressed():
            return MockKeys()
        pygame.key.get_pressed = mock_get_pressed
        
        for k in range(10):
            game._update_playing(0.016, pygame.key.get_pressed())
            game._draw_gameplay()
    
    print("All stages updated and drawn without errors!")
    return True

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
