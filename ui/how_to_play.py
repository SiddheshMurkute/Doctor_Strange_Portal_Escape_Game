# ui/how_to_play.py
import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class HowToPlay:
    GOLD  = (255, 180, 0)
    WHITE = (255, 255, 255)

    CONTENT = [
        ("OBJECTIVE",  "Find the correct portal before time runs out."),
        ("MOVEMENT",   "WASD or Arrow Keys to move Doctor Strange."),
        ("ATTACK",     "SPACE — Mystic Flame Attack (damages enemies)."),
        ("INTERACT",   "E — Enter a portal when nearby."),
        ("SURVIVE",    "Enemies attack you. Each hit: -5 HP. Dodge wisely."),
        ("ESCAPE",     "Enter the correct portal to advance to the next stage."),
        ("WRONG PORTAL","Wrong portal = score penalty. You stay in the stage."),
        ("FRAGMENTS",  "Golden diamonds = bonus points (optional)."),
        ("TIMER",      "Time decreases each stage. Zero = stage failed."),
        ("PAUSE",      "ESC to pause. F11 toggles fullscreen."),
    ]

    def __init__(self, font_large, font_med, font_small):
        self.fl = font_large
        self.fm = font_med
        self.fs = font_small

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE,
                             pygame.K_SPACE, pygame.K_BACKSPACE):
                return 'back'
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return 'back'
        return None

    def draw(self, surface):
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT
        surface.fill((8, 4, 18))
        for y in range(sh):
            frac = y/sh
            pygame.draw.line(surface, (int(8+frac*22), int(4+frac*8), int(18+frac*45)), (0,y),(sw,y))

        title = self.fl.render("HOW TO PLAY", True, self.GOLD)
        surface.blit(title, (sw//2 - title.get_width()//2, 30))

        col1_x = 60
        col2_x = 380
        y0 = 100
        for i, (heading, body) in enumerate(self.CONTENT):
            row = i % ((len(self.CONTENT)+1)//2)
            col_x = col1_x if i < (len(self.CONTENT)+1)//2 else col2_x + 200
            y = y0 + row * 76

            pygame.draw.rect(surface, (30, 20, 55, 0), (col_x-10, y-5, 550, 65))
            head = self.fm.render(heading, True, self.GOLD)
            body_txt = self.fs.render(body, True, (200, 190, 220))
            surface.blit(head, (col_x, y))
            surface.blit(body_txt, (col_x, y + head.get_height() + 2))

        hint = self.fs.render("Press ENTER / SPACE / click to return", True, (120, 100, 160))
        surface.blit(hint, (sw//2 - hint.get_width()//2, sh - 50))
