# main.py
"""Entry point for Doctor Strange: Portal Escape."""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
