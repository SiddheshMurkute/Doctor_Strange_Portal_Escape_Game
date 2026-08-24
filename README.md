# Doctor Strange: Portal Escape

## Overview
A complete 2D PC arcade/adventure game built in Python/Pygame. Control Doctor Strange through 5 dimensions, fight Thanos-army enemies, and find the correct portal before time runs out.

## Quick Start

```powershell
# 1 - Create venv (already done)
python -m venv .venv

# 2 - Activate
.venv\Scripts\activate

# 3 - Install dependencies
pip install pygame

# 4 - Run
python main.py
```

Or use the interpreter directly:
```powershell
.venv\Scripts\python.exe main.py
```

## Controls

| Key | Action |
|-----|--------|
| W / A / S / D | Move |
| Arrow Keys | Move (alternative) |
| SPACE | Mystic Flame Attack |
| E | Enter nearby portal |
| ESC | Pause |
| F11 | Toggle Fullscreen |
| ENTER | Confirm menus |

## Difficulty Modes

| Mode | Enemy Count | Enemy Speed | Notes |
|------|-------------|-------------|-------|
| EASY | ×0.6 | ×0.7 | Learn the game |
| MEDIUM | ×1.0 | ×1.0 | Intended experience |
| HARD | ×1.5 | ×1.3 | Maximum pressure |

## Stage Information

| Stage | Location | Time Limit | Objective |
|-------|----------|------------|-----------|
| 1 | New York City | 90 sec | Find the correct portal |
| 2 | Spaceship | 75 sec | Navigate corridors |
| 3 | Titan | 60 sec | Reach Earth-616 exit |
| 4 | Snow Mountain | 45 sec | Survive decoys |
| 5 | Netherworld | 30 sec | Maximum pressure escape |

## Scoring

| Action | Points |
|--------|--------|
| Correct portal | +500 |
| Time bonus | +10/sec remaining |
| Dimensional fragment | +150 |
| Wrong portal | -100 |
| Enemy kill (max 20/stage) | +25 |
| Stage complete bonus | +300 |
| Final escape bonus | +2000 |

## Project Structure

```
Doctor_Strange_Portal_Escape/
├── main.py               # Entry point
├── requirements.txt
├── config/               # All game constants & balancing
├── core/                 # Game loop, camera, collision, state machine
├── player/               # Doctor Strange (procedural sprite), attack
├── enemies/              # Enemy types, AI, manager
├── objects/              # Portals, fragments
├── levels/               # All 5 stage environments
├── ui/                   # All screens (menu, HUD, results)
├── effects/              # Particles, glow, shake, transitions
├── audio/                # Centralized audio manager
└── assets/               # images, sounds, fonts (optional)
```

## Configuration

To tune game balance without code changes, edit these files:
- `config/scoring.py` — all point values and penalties
- `config/stages.py` — timer per stage, enemy counts, portal zones
- `config/difficulty.py` — Easy/Medium/Hard multipliers

## Packaging (Optional)

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## Technical Notes
- Target: 1280×720 @ 60 FPS
- All graphics: procedural Pygame primitives (no external art required)
- Audio: graceful no-op if sound files are missing
- Portal positions: randomly validated per run within configured zones
