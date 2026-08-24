# core/game.py
"""Main game loop and state machine."""
import pygame
import sys
import math
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from config.controls import PAUSE, FULLSCREEN, CONFIRM, INTERACT, ATTACK
from config.stages import STAGE_CONFIG
from config.scoring import SCORING
from core.game_state import GameState
from core.level_manager import LevelManager
from core.asset_manager import assets
from effects.screen_shake import ScreenShake
from effects.transitions import FadeTransition
from audio.audio_manager import audio

# --- UI screens ---
from ui.main_menu import MainMenu
from ui.difficulty_menu import DifficultyMenu
from ui.how_to_play import HowToPlay
from ui.stage_intro import StageIntro
from ui.hud import HUD
from ui.pause_menu import PauseMenu
from ui.portal_result import PortalResult
from ui.result_screen import FinalEscapeScreen, FinalResultScreen, FailureScreen

# --- Player ---
from player.player import Player

# --- Enemy manager ---
from enemies.enemy_manager import EnemyManager

# --- Stage factory ---
def _build_stage(stage: int, difficulty: str):
    if stage == 1:
        from levels.stage1_new_york import Stage1NewYork
        return Stage1NewYork(difficulty)
    elif stage == 2:
        from levels.stage2_space import Stage2Space
        return Stage2Space(difficulty)
    elif stage == 3:
        from levels.stage3_titan import Stage3Titan
        return Stage3Titan(difficulty)
    elif stage == 4:
        from levels.stage4_snow import Stage4Snow
        return Stage4Snow(difficulty)
    elif stage == 5:
        from levels.stage5_netherworld import Stage5Netherworld
        return Stage5Netherworld(difficulty)
    return None


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.screen   = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock    = pygame.time.Clock()
        self.running  = True
        self.fullscreen = False

        # Fonts
        self.font_large = pygame.font.SysFont("arial", 42, bold=True)
        self.font_med   = pygame.font.SysFont("arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("arial", 20)
        self.font_tiny  = pygame.font.SysFont("arial", 16)

        # State
        self.state     = GameState.MAIN_MENU
        self.lm        = LevelManager()
        self.shake     = ScreenShake()
        self.fade      = FadeTransition()

        # Game objects (set up in _start_stage)
        self.player    = None
        self.level     = None
        self.enemy_mgr = None
        self.hud       = None
        self.time_left = 0.0
        self.objective = "FIND THE CORRECT PORTAL"

        # Portal result state
        self._portal_result_result = 'correct'
        self._portal_result_pending = False

        # UI objects
        self.main_menu   = MainMenu(self.font_large, self.font_med, self.font_small)
        self.diff_menu   = DifficultyMenu(self.font_large, self.font_med, self.font_small)
        self.how_to_play = HowToPlay(self.font_large, self.font_med, self.font_small)
        self.pause_menu  = PauseMenu(self.font_large, self.font_med, self.font_small)
        self.portal_result_ui = PortalResult(self.font_large, self.font_med, self.font_small)
        self.final_escape_ui  = FinalEscapeScreen(self.font_large, self.font_med)
        self.final_result_ui  = FinalResultScreen(self.font_large, self.font_med, self.font_small)
        self.failure_ui       = FailureScreen(self.font_large, self.font_med, self.font_small)
        self.stage_intro_ui   = None  # built per stage

    # ============================================================ PUBLIC
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # cap dt to prevent spiral-of-death

            events = pygame.event.get()
            keys   = pygame.key.get_pressed()
            mouse  = pygame.mouse.get_pos()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                # Global controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self._toggle_fullscreen()

                self._handle_state_event(event, keys, mouse)

            self._update(dt, keys)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # ============================================================ PRIVATE: TOGGLE
    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # ============================================================ PRIVATE: BUILD STAGE
    def _start_stage(self, stage: int = None):
        if stage is not None:
            self.lm.current_stage = stage
        s = self.lm.current_stage
        cfg = STAGE_CONFIG[s]

        self.level     = _build_stage(s, self.lm.difficulty)
        player_start   = cfg["player_start"]
        self.player    = Player(*player_start)
        self.enemy_mgr = EnemyManager(s, self.lm.difficulty,
                                       cfg["enemy_spawn_zones"],
                                       player_start,
                                       self.level.world_rect)
        self.enemy_mgr.spawn_wave(cfg["base_enemy_count"])
        self.hud       = HUD(self.font_med, self.font_small, s)
        self.time_left = float(cfg["timer"])

        # Objective
        labels = cfg.get("portal_labels", [])
        correct = cfg.get("correct_label", "")
        if correct:
            self.objective = f"REACH {correct} EXIT"
        else:
            self.objective = "FIND THE CORRECT PORTAL"

        # Stage intro
        self.stage_intro_ui = StageIntro(self.font_large, self.font_med, self.font_small,
                                          s, cfg["timer"])
        self.state = GameState.STAGE_INTRO
        self.fade.start_fade_in(speed=200)

    def _restart_game(self):
        self.lm.reset()
        self.lm.difficulty = self.diff_menu.options[self.diff_menu.selected]
        self._start_stage(1)

    def _retry_stage(self):
        self._start_stage(self.lm.current_stage)

    # ============================================================ PRIVATE: EVENTS
    def _handle_state_event(self, event, keys, mouse):
        s = self.state

        if s == GameState.MAIN_MENU:
            result = self.main_menu.handle_event(event, mouse)
            if result == "PLAY":
                self.state = GameState.DIFFICULTY_SELECT
                self.fade.start_fade_in(speed=300)
            elif result == "HOW TO PLAY":
                self.state = GameState.HOW_TO_PLAY
            elif result == "EXIT":
                self.running = False

        elif s == GameState.DIFFICULTY_SELECT:
            result = self.diff_menu.handle_event(event, mouse)
            if result:
                self.lm.difficulty = result
                self.lm.reset()
                self._start_stage(1)

        elif s == GameState.HOW_TO_PLAY:
            result = self.how_to_play.handle_event(event)
            if result == 'back':
                self.state = GameState.MAIN_MENU

        elif s == GameState.STAGE_INTRO:
            result = self.stage_intro_ui.handle_event(event)
            if result == 'start':
                self.state = GameState.PLAYING
                self.fade.start_fade_in(speed=200)

        elif s == GameState.PAUSED:
            result = self.pause_menu.handle_event(event, mouse)
            if result == 'RESUME':
                self.state = GameState.PLAYING
            elif result == 'RESTART':
                self._restart_game()
            elif result == 'MAIN MENU':
                self.state = GameState.MAIN_MENU

        elif s == GameState.PORTAL_RESULT:
            pass  # auto-dismiss handled in update

        elif s == GameState.FINAL_ESCAPE:
            pass  # auto-advance in update

        elif s == GameState.FINAL_RESULT:
            result = self.final_result_ui.handle_event(event, mouse)
            if result == 'PLAY AGAIN':
                self.state = GameState.DIFFICULTY_SELECT
            elif result == 'MAIN MENU':
                self.state = GameState.MAIN_MENU

        elif s == GameState.PLAYER_DEFEATED or s == GameState.STAGE_FAILED:
            result = self.failure_ui.handle_event(event, mouse)
            if result == 'RETRY STAGE':
                self._retry_stage()
            elif result == 'RESTART GAME':
                self._restart_game()
            elif result == 'MAIN MENU':
                self.state = GameState.MAIN_MENU

        # Pause toggle
        if s == GameState.PLAYING:
            if event.type == pygame.KEYDOWN and event.key in PAUSE:
                self.state = GameState.PAUSED
                self.pause_menu.selected = 0

    # ============================================================ PRIVATE: UPDATE
    def _update(self, dt: float, keys):
        self.fade.update(dt)
        s = self.state

        if s == GameState.MAIN_MENU:
            self.main_menu.update(dt)

        elif s == GameState.DIFFICULTY_SELECT:
            self.diff_menu.update(dt)

        elif s == GameState.STAGE_INTRO:
            if self.stage_intro_ui:
                self.stage_intro_ui.update(dt)

        elif s == GameState.PLAYING:
            self._update_playing(dt, keys)

        elif s == GameState.PORTAL_RESULT:
            self.portal_result_ui.update(dt)
            if self.portal_result_ui.continue_flag:
                if self._portal_result_result == 'correct':
                    self._advance_or_final()
                else:
                    self.state = GameState.PLAYING

        elif s == GameState.FINAL_ESCAPE:
            self.final_escape_ui.update(dt)
            if self.final_escape_ui.done:
                self.state = GameState.FINAL_RESULT

    def _update_playing(self, dt: float, keys):
        if not self.player or not self.level:
            return

        # Input
        self.player.handle_input(keys, dt)

        # Portal interaction
        e_pressed = any(keys[k] for k in INTERACT)

        # Level update (portals, fragments, env fx, camera)
        result = self.level.update(dt, self.player,
                                    e_pressed,
                                    lambda pts: self.lm.add_score(pts))

        # Player movement vs walls
        self.player.update(dt, self.level.walls, self.level.world_rect)

        # Camera shake
        self.shake.update(dt)
        ox, oy = self.shake.get_offset()
        self.level.camera.set_shake(ox, oy)

        # Enemies
        score_delta = self.enemy_mgr.update(dt, self.player, self.level.walls)
        self.lm.add_score(score_delta)
        if score_delta > 0:
            self.lm.stage_kills += 1

        # HUD update
        self.hud.update(dt)

        # Timer
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self._fail_stage(defeated=False)
            return

        # Stage 5 instability
        if self.lm.current_stage == 5:
            from levels.stage5_netherworld import Stage5Netherworld
            if isinstance(self.level, Stage5Netherworld):
                cfg_t = STAGE_CONFIG[5]["timer"]
                self.level.update_instability(self.time_left, cfg_t,
                                               self.level.camera, self.shake)

        # Player death
        if not self.player.alive:
            pygame.time.wait(400)
            self._fail_stage(defeated=True)
            return

        # Portal result
        if result == 'correct':
            # Score for correct portal
            time_bonus = int(self.time_left * SCORING["time_bonus_per_sec"])
            self.lm.add_score(SCORING["correct_portal_base"] + time_bonus)
            self.lm.add_elapsed(STAGE_CONFIG[self.lm.current_stage]["timer"] - self.time_left)
            self.portal_result_ui.show('correct', 0, duration=2.2)
            self._portal_result_result = 'correct'
            self.state = GameState.PORTAL_RESULT
        elif result == 'wrong':
            self.lm.add_score(SCORING["wrong_portal_penalty"])
            self.portal_result_ui.show('wrong', SCORING["wrong_portal_penalty"], duration=2.0)
            self._portal_result_result = 'wrong'
            self.state = GameState.PORTAL_RESULT

    def _fail_stage(self, defeated: bool):
        self.failure_ui.set_reason(defeated)
        self.state = GameState.PLAYER_DEFEATED if defeated else GameState.STAGE_FAILED

    def _advance_or_final(self):
        """Advance to next stage, or trigger final escape if we just beat stage 5."""
        if self.lm.is_final_stage():
            # Just completed stage 5
            self.lm.add_score(SCORING["final_escape_bonus"])
            self.final_escape_ui._t = 0
            self.final_escape_ui.done = False
            self.state = GameState.FINAL_ESCAPE
        else:
            self.lm.add_score(SCORING["stage_complete_bonus"])
            self.lm.advance_stage()
            self._start_stage()

    # ============================================================ PRIVATE: DRAW
    def _draw(self):
        s = self.state

        if s == GameState.MAIN_MENU:
            self.main_menu.draw(self.screen)

        elif s == GameState.DIFFICULTY_SELECT:
            self.diff_menu.draw(self.screen)

        elif s == GameState.HOW_TO_PLAY:
            self.how_to_play.draw(self.screen)

        elif s == GameState.STAGE_INTRO and self.stage_intro_ui:
            self.stage_intro_ui.draw(self.screen)

        elif s in (GameState.PLAYING, GameState.PAUSED, GameState.PORTAL_RESULT):
            self._draw_gameplay()
            if s == GameState.PAUSED:
                self.pause_menu.draw(self.screen)
            elif s == GameState.PORTAL_RESULT:
                self.portal_result_ui.draw(self.screen)

        elif s == GameState.FINAL_ESCAPE:
            self._draw_gameplay()
            self.final_escape_ui.draw(self.screen)

        elif s == GameState.FINAL_RESULT:
            self.final_result_ui.draw(self.screen, self.lm.total_score,
                                       self.lm.total_time_elapsed,
                                       self.lm.current_stage - 1)

        elif s in (GameState.PLAYER_DEFEATED, GameState.STAGE_FAILED):
            self._draw_gameplay()
            self.failure_ui.draw(self.screen, self.lm.total_score, self.lm.current_stage)

        # Fade overlay always on top
        self.fade.draw(self.screen)

    def _draw_gameplay(self):
        if not self.level or not self.player:
            return

        # Level (background + walls + portals + env fx)
        self.level.draw(self.screen, self.font_small)
        self.level.draw_interact_prompts(self.screen, self.player.rect, self.font_small)

        # Enemies
        self.enemy_mgr.draw(self.screen, self.level.camera)

        # Player
        self.player.draw(self.screen, self.level.camera)

        # HUD
        self.hud.draw(
            surface             = self.screen,
            hp                  = self.player.hp,
            max_hp              = self.player.max_hp,
            score               = self.lm.total_score,
            time_left           = self.time_left,
            max_time            = STAGE_CONFIG[self.lm.current_stage]["timer"],
            stage               = self.lm.current_stage,
            objective           = self.objective,
            attack_cooldown_pct = self.player.attack.cooldown_pct,
            fragment_count      = self.player.fragments_collected,
        )
