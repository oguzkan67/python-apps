# Neon Snake Ultimate

Desktop Snake game in Python with advanced visuals and layered gameplay systems.

## Features

- Animated neon background, glow effects, particles, screen shake, and floating score text
- Multiple modes: `Neo Classic`, `Arena`, `Blitz` (timed mode)
- Power-up foods: `PHASE`, `MAGNET`, `TURBO`, `CRYSTAL CLEAR`, `EXTRA LIFE`
- Combo scoring, level scaling, increasing speed, and dynamic obstacles
- Pause, game-over screen, and persistent local high scores

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 snake_game.py
```

## Quick self-test

```bash
SDL_VIDEODRIVER=dummy python3 snake_game.py --self-test
```
