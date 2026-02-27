#!/usr/bin/env python3
"""KIZIL ELMA - Turkish Mythology Snake Game with 2 Player VS Mode"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

import pygame


# Settings
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
CELL_SIZE = 20
GRID_COLS = 60
GRID_ROWS = 45
PLAY_WIDTH = GRID_COLS * CELL_SIZE
PLAY_HEIGHT = GRID_ROWS * CELL_SIZE
FPS = 144


# Snake Characters
SNAKE_CHARACTERS = {
    "Aktif": {
        "name": "Aktif Yılan",
        "description": "Hızlı hareket eder",
        "primary": (50, 200, 100),
        "secondary": (100, 255, 150),
        "glow": (100, 255, 150),
        "speed_bonus": 0.85,
        "magnet_range": 0,
        "start_lives": 3,
    },
    "Sakin": {
        "name": "Sakin Yılan",
        "description": "Daha yavaş ama daha dikkatli",
        "primary": (100, 150, 200),
        "secondary": (150, 200, 255),
        "glow": (150, 200, 255),
        "speed_bonus": 1.15,
        "magnet_range": 0,
        "start_lives": 4,
    },
    "Çekici": {
        "name": "Çekici Yılan",
        "description": "Yakınındaki yemekleri çeker",
        "primary": (200, 100, 200),
        "secondary": (255, 150, 255),
        "glow": (255, 150, 255),
        "speed_bonus": 1.0,
        "magnet_range": 2,
        "start_lives": 3,
    },
    "Uzun": {
        "name": "Uzun Yılan",
        "description": "Daha uzun başlar, daha fazla can",
        "primary": (200, 150, 50),
        "secondary": (255, 200, 100),
        "glow": (255, 200, 100),
        "speed_bonus": 1.0,
        "magnet_range": 0,
        "start_length": 7,
        "start_lives": 3,
    },
    "Sihirli": {
        "name": "Sihirli Yılan",
        "description": "Bonus yemeklerden güç alır",
        "primary": (150, 50, 200),
        "secondary": (200, 100, 255),
        "glow": (200, 100, 255),
        "speed_bonus": 1.0,
        "magnet_range": 0,
        "bonus_mult": 1.5,
        "start_lives": 3,
    },
}

# Food Config
FOOD_CONFIG = {
    "elma": {"color": (220, 50, 60), "points": 100, "growth": 1, "weight": 80, "ttl": None},
    "altin": {"color": (255, 215, 0), "points": 250, "growth": 2, "weight": 20, "ttl": None},
    # Bonus foods - appear rarely with special abilities
    "peri": {"color": (180, 100, 255), "points": 180, "growth": 1, "weight": 0, "ttl": 9.0, "ability": "ghost", "duration": 6.0},
    "nazar": {"color": (50, 150, 255), "points": 160, "growth": 1, "weight": 0, "ttl": 9.0, "ability": "magnet", "duration": 8.0},
    "tas": {"color": (255, 100, 200), "points": 200, "growth": 1, "weight": 0, "ttl": 9.0, "ability": "turbo", "duration": 7.0},
    "zümrüt": {"color": (50, 200, 100), "points": 230, "growth": 2, "weight": 0, "ttl": 9.0, "ability": "clear_obstacles", "duration": 0},
    "can": {"color": (255, 80, 80), "points": 130, "growth": 1, "weight": 0, "ttl": 8.0, "ability": "extra_life", "duration": 0},
    "zehir": {"color": (100, 255, 100), "points": 145, "growth": 1, "weight": 0, "ttl": 8.0, "ability": "poison", "duration": 0},
    "kalkan": {"color": (100, 180, 255), "points": 150, "growth": 1, "weight": 0, "ttl": 8.0, "ability": "shield", "duration": 5.0},
    "hayat": {"color": (255, 200, 100), "points": 120, "growth": 0, "weight": 0, "ttl": 8.0, "ability": "heal", "duration": 0},
    # Rare special ability foods - very rare but powerful
    "yıldırım": {"color": (255, 255, 100), "points": 500, "growth": 3, "weight": 0, "ttl": 7.0, "ability": "lightning", "duration": 4.0, "rare": True},
    "gölge": {"color": (50, 50, 80), "points": 400, "growth": 2, "weight": 0, "ttl": 7.0, "ability": "shadow", "duration": 10.0, "rare": True},
    "kutuk": {"color": (180, 100, 50), "points": 600, "growth": 1, "weight": 0, "ttl": 6.0, "ability": "stump", "duration": 0, "rare": True},
}

# Game modes
MODES = ["Klasik", "Arena", "Süre", "Zen", "VS Modu"]
DIRECTIONS_P1 = {
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0),
}
DIRECTIONS_P2 = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}


@dataclass
class Food:
    pos: tuple
    kind: str
    spawned_at: float
    ttl: float | None = None

    def is_expired(self, now: float) -> bool:
        return self.ttl is not None and now - self.spawned_at >= self.ttl


@dataclass
class Particle:
    pos: pygame.Vector2
    vel: pygame.Vector2
    color: tuple
    life: float
    max_life: float
    radius: float

    def update(self, dt: float) -> bool:
        self.pos += self.vel * dt
        self.vel *= 0.95
        self.radius *= 0.992
        self.life -= dt
        return self.life > 0.0


@dataclass
class FloatingText:
    text: str
    pos: pygame.Vector2
    color: tuple
    life: float = 1.0
    max_life: float = 1.0

    def update(self, dt: float) -> bool:
        self.pos.y -= 40.0 * dt
        self.life -= dt
        return self.life > 0.0


@dataclass
class TrailPoint:
    pos: pygame.Vector2
    life: float
    max_life: float
    color: tuple

    def update(self, dt: float) -> bool:
        self.life -= dt
        return self.life > 0.0


class KizilElmaGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("KIZIL ELMA - Efsane Başlıyor")
        
        self.fullscreen = False
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        
        self.clock = pygame.time.Clock()
        self.rng = random.Random()

        self.play_rect = pygame.Rect(
            (WINDOW_WIDTH - PLAY_WIDTH) // 2,
            (WINDOW_HEIGHT - PLAY_HEIGHT) // 2 + 30,
            PLAY_WIDTH,
            PLAY_HEIGHT,
        )

        self.background_grid = self._build_grid_surface()
        self.overlay_vignette = self._build_vignette_surface()
        
        self.font_title = pygame.font.Font(None, 100)
        self.font_h1 = pygame.font.Font(None, 60)
        self.font_h2 = pygame.font.Font(None, 42)
        self.font_body = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)

        self.state = "character_select"
        self.mode_index = 0
        self.character_index = 0
        self.character_index_p2 = 1  # Player 2 character
        self.running = True
        self.screen_shake = 0.0
        self.flash_strength = 0.0
        
        self.damage_flash_until = 0.0
        self.trail: list[TrailPoint] = []
        self.trail_p2: list[TrailPoint] = []
        self.total_coins = 0
        
        self.character_keys = list(SNAKE_CHARACTERS.keys())
        
        self.clouds = []
        for _ in range(15):
            self.clouds.append({
                'x': random.random() * WINDOW_WIDTH,
                'y': random.random() * WINDOW_HEIGHT * 0.6,
                'speed': random.uniform(5, 20),
                'size': random.uniform(80, 200),
                'opacity': random.uniform(30, 80)
            })

        self.scores_file = Path(__file__).with_name("high_scores.json")
        self.skins_file = Path(__file__).with_name("skins_save.json")
        self._load_data()
        self.high_scores = self._load_scores()
        self.particles = []
        self.floaters = []

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

    def _load_data(self) -> None:
        try:
            if self.skins_file.exists():
                data = json.loads(self.skins_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    self.total_coins = data.get("total_coins", 0)
        except:
            pass

    def _get_current_character(self, p1: bool = True) -> dict:
        idx = self.character_index if p1 else self.character_index_p2
        return SNAKE_CHARACTERS[self.character_keys[idx]]

    def _build_grid_surface(self) -> pygame.Surface:
        surface = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT), pygame.SRCALPHA)
        for x in range(0, PLAY_WIDTH, CELL_SIZE):
            pygame.draw.line(surface, (200, 150, 100, 25), (x, 0), (x, PLAY_HEIGHT), 1)
        for y in range(0, PLAY_HEIGHT, CELL_SIZE):
            pygame.draw.line(surface, (200, 150, 100, 20), (0, y), (PLAY_WIDTH, y), 1)
        return surface

    def _build_vignette_surface(self) -> pygame.Surface:
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        center = pygame.Vector2(WINDOW_WIDTH / 2.0, WINDOW_HEIGHT / 2.0)
        max_dist = center.length()
        for y in range(WINDOW_HEIGHT):
            for x in range(WINDOW_WIDTH):
                dist = pygame.Vector2(x, y).distance_to(center)
                alpha = int(max(0, min(145, (dist / max_dist) * 180 - 30)))
                if alpha > 0:
                    surface.set_at((x, y), (0, 0, 0, alpha))
        return surface

    def _load_scores(self) -> list:
        if not self.scores_file.exists():
            return []
        try:
            data = json.loads(self.scores_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [int(v) for v in data][:10]
        except:
            return []
        return []

    def _save_scores(self) -> None:
        self.scores_file.write_text(json.dumps(self.high_scores[:10], indent=2), encoding="utf-8")

    def reset_run(self, vs_mode: bool = False) -> None:
        now = time.monotonic()
        
        # Player 1 setup
        char1 = self._get_current_character(True)
        start_length1 = char1.get("start_length", 5)
        start_lives1 = char1.get("start_lives", 3)
        
        center_x = GRID_COLS // 2
        center_y = GRID_ROWS // 2
        self.snake = [(center_x - i, center_y) for i in range(start_length1)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.last_turn_at = 0.0
        
        # Player 2 setup (for VS mode)
        if vs_mode:
            char2 = self._get_current_character(False)
            start_length2 = char2.get("start_length", 5)
            self.snake_p2 = [(center_x + i, center_y + 5) for i in range(start_length2)]
            self.direction_p2 = (-1, 0)
            self.next_direction_p2 = (-1, 0)
            self.last_turn_p2 = 0.0
        else:
            self.snake_p2 = []
            self.direction_p2 = (-1, 0)
            self.next_direction_p2 = (-1, 0)

        self.score = 0
        self.score_p2 = 0
        self.level = 1
        self.foods_eaten = 0
        self.lives = start_lives1
        self.lives_p2 = char2.get("start_lives", 3) if vs_mode else 3
        self.combo = 1
        self.combo_clock = 0.0
        self.last_eat_at = 0.0

        self.pending_growth = 0
        self.move_clock = 0.0
        self.invulnerable_until = now + 1.1
        self.invulnerable_p2 = 0.0

        self.ghost_until = 0.0
        self.magnet_until = 0.0
        self.turbo_until = 0.0
        self.reverse_until = 0.0

        self.shield_charges = 0
        self.tail_whip_cooldown_until = 0.0

        self.companion_active = False
        self.companion_snake = []

        self.obstacles: set = set()
        self.portal_a = None
        self.portal_b = None
        self.portal_refresh_at = now + 13.0
        self.obstacle_growth_at = now + 8.0
        self.obstacle_shift_at = now + 5.0
        self.food = None
        self.bonus_food = None
        self.next_bonus_spawn_at = now + self.rng.uniform(3.0, 5.0)

        self.particles = []
        self.floaters = []
        
        self.trail = []
        self.trail_p2 = []
        self.damage_flash_until = 0.0

        self.game_started_at = now
        self.game_over_reason = ""
        self.vs_mode = vs_mode
        
        self._rebuild_obstacles()
        self._spawn_portals()
        self._spawn_main_food(force_kind="elma")

    def _rebuild_obstacles(self) -> None:
        self.obstacles.clear()
        if MODES[self.mode_index] == "Klasik":
            count = max(0, (self.level - 2) * 2)
        elif MODES[self.mode_index] == "Arena":
            count = 6 + self.level * 2
        elif MODES[self.mode_index] == "Zen":
            count = 0
        elif MODES[self.mode_index] == "VS Modu":
            count = 0  # No obstacles in VS mode
        else:
            count = 4 + self.level * 2
        self._add_obstacles(count)

    def _portal_cells(self) -> set:
        cells = set()
        if self.portal_a is not None:
            cells.add(self.portal_a)
        if self.portal_b is not None:
            cells.add(self.portal_b)
        return cells

    def _occupied_cells(self, include_food: bool = True, include_p2: bool = True) -> set:
        occupied = set(self.snake) | set(self.obstacles) | self._portal_cells()
        if include_p2 and self.vs_mode:
            occupied.update(self.snake_p2)
        if self.companion_active:
            occupied.update(self.companion_snake)
        if include_food:
            if self.food:
                occupied.add(self.food.pos)
            if self.bonus_food:
                occupied.add(self.bonus_food.pos)
        return occupied

    def _is_cell_free(self, pos: tuple, include_food: bool = True, include_p2: bool = True) -> bool:
        return 0 <= pos[0] < GRID_COLS and 0 <= pos[1] < GRID_ROWS and pos not in self._occupied_cells(include_food=include_food, include_p2=include_p2)

    def _random_free_cell(self, attempts: int = 2000, include_food: bool = True, include_p2: bool = True) -> tuple | None:
        for _ in range(attempts):
            pos = (self.rng.randrange(GRID_COLS), self.rng.randrange(GRID_ROWS))
            if self._is_cell_free(pos, include_food=include_food, include_p2=include_p2):
                return pos
        return None

    def _add_obstacles(self, amount: int) -> None:
        blocked = set(self.snake)
        if self.vs_mode:
            blocked.update(self.snake_p2)
        if self.companion_active:
            blocked.update(self.companion_snake)
        blocked.update(self._portal_cells())
        for _ in range(6000):
            if amount <= 0:
                break
            pos = (self.rng.randrange(GRID_COLS), self.rng.randrange(GRID_ROWS))
            if pos in blocked or pos in self.obstacles:
                continue
            if self.food and pos == self.food.pos:
                continue
            if self.bonus_food and pos == self.bonus_food.pos:
                continue
            if abs(pos[0] - GRID_COLS // 2) <= 2 and abs(pos[1] - GRID_ROWS // 2) <= 2:
                continue
            self.obstacles.add(pos)
            amount -= 1

    def _spawn_portals(self) -> None:
        first = self._random_free_cell(include_food=False, include_p2=False)
        second = self._random_free_cell(include_food=False, include_p2=False)
        if first is None or second is None:
            self.portal_a = None
            self.portal_b = None
            return
        for _ in range(200):
            if first != second and abs(first[0] - second[0]) + abs(first[1] - second[1]) >= 10:
                break
            second = self._random_free_cell(include_food=False, include_p2=False)
            if second is None:
                break
        if second is None or first == second:
            self.portal_a = None
            self.portal_b = None
            return
        self.portal_a = first
        self.portal_b = second

    def _spawn_main_food(self, force_kind: str | None = None) -> None:
        occupied = self._occupied_cells(include_food=False, include_p2=False)
        for _ in range(900):
            pos = (self.rng.randrange(GRID_COLS), self.rng.randrange(GRID_ROWS))
            if pos in occupied:
                continue
            if force_kind:
                kind = force_kind
            else:
                weighted = []
                for key in ("elma", "altin"):
                    weighted.extend([key] * FOOD_CONFIG[key]["weight"])
                if self.level >= 4:
                    weighted.extend(["altin"] * 8)
                kind = self.rng.choice(weighted)
            self.food = Food(pos=pos, kind=kind, spawned_at=time.monotonic(), ttl=None)
            return

    def _spawn_bonus_food(self, now: float) -> None:
        occupied = self._occupied_cells(include_food=False, include_p2=False)
        bonus_kinds = ["peri", "nazar", "tas", "zümrüt", "can", "zehir", "kalkan", "hayat", "yıldırım", "gölge", "kutuk"]
        for _ in range(1200):
            pos = (self.rng.randrange(GRID_COLS), self.rng.randrange(GRID_ROWS))
            if pos in occupied:
                continue
            kind = self.rng.choice(bonus_kinds)
            ttl = FOOD_CONFIG[kind]["ttl"]
            self.bonus_food = Food(pos=pos, kind=kind, spawned_at=now, ttl=ttl)
            self.next_bonus_spawn_at = now + self.rng.uniform(4.0, 7.0)
            return

    def _grid_to_screen(self, cell: tuple) -> tuple:
        return (
            self.play_rect.left + cell[0] * CELL_SIZE,
            self.play_rect.top + cell[1] * CELL_SIZE,
        )

    def _active_interval(self) -> float:
        character = self._get_current_character(True)
        speed_bonus = character.get("speed_bonus", 1.0)
        
        base = max(0.058, 0.14 - (self.level - 1) * 0.0075) * speed_bonus
        
        if MODES[self.mode_index] == "Süre":
            base *= 0.9
        elif MODES[self.mode_index] == "Zen":
            base *= 1.2
        if time.monotonic() <= self.turbo_until:
            base *= 0.72
        return base

    def _remaining_blitz_seconds(self) -> int:
        if MODES[self.mode_index] != "Süre":
            return 0
        elapsed = time.monotonic() - self.game_started_at
        return max(0, 180 - int(elapsed))

    def _queue_floating_text(self, text: str, grid_pos: tuple, color: tuple, life: float = 1.0) -> None:
        x, y = self._grid_to_screen(grid_pos)
        center = pygame.Vector2(x + CELL_SIZE * 0.5, y + CELL_SIZE * 0.35)
        self.floaters.append(FloatingText(text=text, pos=center, color=color, life=life, max_life=life))

    def _emit_particles(self, grid_pos: tuple, color: tuple, amount: int = 16, speed: float = 240.0) -> None:
        x, y = self._grid_to_screen(grid_pos)
        origin = pygame.Vector2(x + CELL_SIZE * 0.5, y + CELL_SIZE * 0.5)
        for _ in range(amount):
            angle = self.rng.uniform(0.0, math.tau)
            magnitude = self.rng.uniform(speed * 0.25, speed)
            vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * magnitude
            life = self.rng.uniform(0.28, 0.7)
            radius = self.rng.uniform(2.0, 4.8)
            self.particles.append(Particle(pos=origin.copy(), vel=vel, color=color, life=life, max_life=life, radius=radius))

    def _add_trail_point(self, cell: tuple, is_p2: bool = False) -> None:
        character = self._get_current_character(not is_p2)
        x, y = self._grid_to_screen(cell)
        center = pygame.Vector2(x + CELL_SIZE * 0.5, y + CELL_SIZE * 0.5)
        
        trail_color = character["primary"]
        
        trail = self.trail_p2 if is_p2 else self.trail
        trail.append(TrailPoint(pos=center, life=1.5, max_life=1.5, color=trail_color))
        
        if len(trail) > 50:
            trail.pop(0)
        
        if is_p2:
            self.trail_p2 = trail
        else:
            self.trail = trail

    def _update_trail(self, dt: float) -> None:
        self.trail = [t for t in self.trail if t.update(dt)]
        self.trail_p2 = [t for t in self.trail_p2 if t.update(dt)]

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                key = event.key
                
                # Character selection
                if self.state == "character_select":
                    if key in (pygame.K_LEFT, pygame.K_a):
                        self.character_index = (self.character_index - 1) % len(self.character_keys)
                    elif key in (pygame.K_RIGHT, pygame.K_d):
                        self.character_index = (self.character_index + 1) % len(self.character_keys)
                    elif key in (pygame.K_UP, pygame.K_w):
                        self.mode_index = (self.mode_index - 1) % len(MODES)
                    elif key in (pygame.K_DOWN, pygame.K_s):
                        self.mode_index = (self.mode_index + 1) % len(MODES)
                    # Player 2 character selection in VS mode
                    elif key == pygame.K_q:
                        self.character_index_p2 = (self.character_index_p2 - 1) % len(self.character_keys)
                    elif key == pygame.K_e:
                        self.character_index_p2 = (self.character_index_p2 + 1) % len(self.character_keys)
                    elif key in (pygame.K_RETURN, pygame.K_SPACE):
                        vs_mode = MODES[self.mode_index] == "VS Modu"
                        self.reset_run(vs_mode=vs_mode)
                        self.state = "playing"
                    elif key == pygame.K_ESCAPE:
                        self.running = False
                    elif key == pygame.K_F11:
                        self.toggle_fullscreen()
                    return

                if self.state == "menu":
                    if key in (pygame.K_UP, pygame.K_w):
                        self.mode_index = (self.mode_index - 1) % len(MODES)
                    elif key in (pygame.K_DOWN, pygame.K_s):
                        self.mode_index = (self.mode_index + 1) % len(MODES)
                    elif key in (pygame.K_RETURN, pygame.K_SPACE):
                        vs_mode = MODES[self.mode_index] == "VS Modu"
                        self.reset_run(vs_mode=vs_mode)
                        self.state = "playing"
                    elif key == pygame.K_ESCAPE:
                        self.running = False
                    elif key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif key == pygame.K_c:
                        self.state = "character_select"
                    return

                if self.state == "playing":
                    # Player 1 (WASD)
                    if key in DIRECTIONS_P1:
                        desired = DIRECTIONS_P1[key]
                        
                        # Allow any turn
                        if time.monotonic() <= self.reverse_until:
                            desired = (-desired[0], -desired[1])
                        self.next_direction = desired
                    
                    # Player 2 (Arrows)
                    if self.vs_mode:
                        if key == pygame.K_UP:
                            self.next_direction_p2 = (0, -1)
                        elif key == pygame.K_DOWN:
                            self.next_direction_p2 = (0, 1)
                        elif key == pygame.K_LEFT:
                            self.next_direction_p2 = (-1, 0)
                        elif key == pygame.K_RIGHT:
                            self.next_direction_p2 = (1, 0)
                    
                    if key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        pass  # Optional: bullet time
                    elif key in (pygame.K_p, pygame.K_ESCAPE):
                        self.state = "paused"
                    elif key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif key == pygame.K_m:
                        self.state = "character_select"
                    return

                if self.state == "paused":
                    if key in (pygame.K_p, pygame.K_ESCAPE):
                        self.state = "playing"
                    elif key == pygame.K_r:
                        vs_mode = MODES[self.mode_index] == "VS Modu"
                        self.reset_run(vs_mode=vs_mode)
                        self.state = "playing"
                    elif key == pygame.K_m:
                        self.state = "character_select"
                    elif key == pygame.K_F11:
                        self.toggle_fullscreen()
                    return

                if self.state == "gameover":
                    if key in (pygame.K_RETURN, pygame.K_SPACE):
                        vs_mode = MODES[self.mode_index] == "VS Modu"
                        self.reset_run(vs_mode=vs_mode)
                        self.state = "playing"
                    elif key == pygame.K_m:
                        self.state = "character_select"

            elif event.type == pygame.KEYUP:
                self._on_key_up(event.key)
            if event.type == pygame.VIDEORESIZE:
                if not self.fullscreen:
                    global WINDOW_WIDTH, WINDOW_HEIGHT
                    WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h

    def _on_key_up(self, key: int) -> None:
        pass

    def _update(self, dt: float) -> None:
        now = time.monotonic()

        self.screen_shake = max(0.0, self.screen_shake - dt * 24.0)
        self.flash_strength = max(0.0, self.flash_strength - dt * 2.0)
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floaters = [t for t in self.floaters if t.update(dt)]
        
        self._update_trail(dt)
        
        for cloud in self.clouds:
            cloud['x'] += cloud['speed'] * dt
            if cloud['x'] > WINDOW_WIDTH + cloud['size']:
                cloud['x'] = -cloud['size']
                cloud['y'] = random.random() * WINDOW_HEIGHT * 0.5

        if self.state != "playing":
            return

        if MODES[self.mode_index] == "Süre" and self._remaining_blitz_seconds() <= 0:
            self._trigger_game_over("Süre Doldu")
            return

        world_dt = dt

        if self.combo_clock > 0.0:
            self.combo_clock -= world_dt
            if self.combo_clock <= 0.0:
                self.combo = 1
                self.combo_clock = 0.0

        if self.bonus_food is None and now >= self.next_bonus_spawn_at:
            self._spawn_bonus_food(now)
        elif self.bonus_food and self.bonus_food.is_expired(now):
            self.bonus_food = None

        if now >= self.portal_refresh_at:
            self._spawn_portals()
            self.portal_refresh_at = now + self.rng.uniform(13.0, 18.0)
        if now >= self.obstacle_growth_at and MODES[self.mode_index] not in ("Zen", "VS Modu"):
            self._add_obstacles(1 + (1 if self.level >= 6 else 0))
            self.obstacle_growth_at = now + self.rng.uniform(7.5, 11.0)
        if now >= self.obstacle_shift_at and MODES[self.mode_index] not in ("Zen", "VS Modu"):
            self._shift_obstacles()
            self.obstacle_shift_at = now + self.rng.uniform(5.2, 8.0)

        self.move_clock += world_dt
        step_interval = self._active_interval()
        while self.state == "playing" and self.move_clock >= step_interval:
            self.move_clock -= step_interval
            tick_now = time.monotonic()
            
            if len(self.snake) > 1:
                self._add_trail_point(self.snake[-1], False)
            if self.vs_mode and len(self.snake_p2) > 1:
                self._add_trail_point(self.snake_p2[-1], True)
            
            self._advance_snake(tick_now)
            if self.state != "playing":
                break
            if self.vs_mode:
                self._advance_p2_snake(tick_now)

    def _shift_obstacles(self) -> None:
        if not self.obstacles:
            return
        originals = list(self.obstacles)
        self.rng.shuffle(originals)
        max_moves = max(1, len(originals) // 7)
        moved = 0
        kept = set()
        blockers = set(self.snake) | self._portal_cells()
        if self.vs_mode:
            blockers.update(self.snake_p2)
        if self.food:
            blockers.add(self.food.pos)
        if self.bonus_food:
            blockers.add(self.bonus_food.pos)

        for pos in originals:
            if moved >= max_moves or self.rng.random() < 0.35:
                kept.add(pos)
                continue
            options = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cand = (pos[0] + dx, pos[1] + dy)
                if not (0 <= cand[0] < GRID_COLS and 0 <= cand[1] < GRID_ROWS):
                    continue
                if cand in blockers or cand in kept or cand in self.obstacles:
                    continue
                options.append(cand)
            if options:
                kept.add(self.rng.choice(options))
                moved += 1
            else:
                kept.add(pos)
        self.obstacles = kept

    def _try_use_shield(self, now: float, pos: tuple) -> bool:
        if self.shield_charges <= 0:
            return False
        self.shield_charges -= 1
        self.invulnerable_until = max(self.invulnerable_until, now + 1.0)
        return True

    def _apply_portal(self, pos: tuple) -> tuple:
        if self.portal_a is None or self.portal_b is None:
            return pos, False
        if pos == self.portal_a:
            return self.portal_b, True
        if pos == self.portal_b:
            return self.portal_a, True
        return pos, False

    def _advance_snake(self, now: float) -> None:
        direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        invulnerable = now <= self.invulnerable_until
        ghosted = now <= self.ghost_until

        # Wall collision
        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
            if invulnerable:
                new_head = (new_head[0] % GRID_COLS, new_head[1] % GRID_ROWS)
            else:
                if self.vs_mode:
                    self._trigger_vs_game_over("Oyuncu 1 duvara çarptı!")
                else:
                    self._on_crash("Duvar")
                return

        new_head, used_portal = self._apply_portal(new_head)
        if used_portal:
            self._emit_particles(new_head, (150, 100, 50), amount=18, speed=210)
            self._queue_floating_text("KAPI", new_head, (200, 150, 100), life=0.85)

        # Self collision
        body_to_check = self.snake[:-1] if self.pending_growth <= 0 else self.snake
        if new_head in body_to_check and not ghosted:
            if self.vs_mode:
                self._trigger_vs_game_over("Oyuncu 1 kendine çarptı!")
            else:
                self._on_crash("Kendine çarptı")
            return

        # VS Mode: collision with P2 body - but allow head-to-head (tie goes to first processed)
        if self.vs_mode and new_head in self.snake_p2 and new_head != self.snake_p2[0]:
            self._trigger_vs_game_over("Oyuncu 1 Oyuncu 2'ye çarptı!")
            return

        # Obstacle collision
        if new_head in self.obstacles and not invulnerable:
            if self.vs_mode:
                self._trigger_vs_game_over("Oyuncu 1 kayaya çarptı!")
            else:
                self._on_crash("Kaya")
            return

        self.snake.insert(0, new_head)
        ate = False
        if self.food and new_head == self.food.pos:
            self._consume_food(self.food, now, False)
            self.pending_growth += FOOD_CONFIG[self.food.kind]["growth"]
            self.food = None
            self._spawn_main_food()
            ate = True
        if self.bonus_food and new_head == self.bonus_food.pos:
            self._consume_food(self.bonus_food, now, True)
            self.pending_growth += FOOD_CONFIG[self.bonus_food.kind]["growth"]
            self.bonus_food = None
            self.next_bonus_spawn_at = now + self.rng.uniform(5.0, 8.0)
            ate = True

        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.snake.pop()

        if not ate and self.rng.random() < 0.25:
            self._emit_particles(self.snake[-1], (150, 100, 50), amount=2, speed=65)

    def _advance_p2_snake(self, now: float) -> None:
        """Player 2 snake movement for VS mode"""
        direction = self.next_direction_p2
        head_x, head_y = self.snake_p2[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        invulnerable = now <= self.invulnerable_p2
        ghosted = now <= self.ghost_until

        # Wall collision
        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
            if invulnerable:
                new_head = (new_head[0] % GRID_COLS, new_head[1] % GRID_ROWS)
            else:
                self._trigger_vs_game_over("Oyuncu 2 duvara çarptı!")
                return

        new_head, used_portal = self._apply_portal(new_head)
        if used_portal:
            self._emit_particles(new_head, (150, 100, 50), amount=18, speed=210)

        # Self collision
        body_to_check = self.snake_p2[:-1]
        if new_head in body_to_check and not ghosted:
            self._trigger_vs_game_over("Oyuncu 2 kendine çarptı!")
            return

        # Collision with P1 body - but allow head-to-head (tie goes to first processed)
        if new_head in self.snake and new_head != self.snake[0]:
            self._trigger_vs_game_over("Oyuncu 2 Oyuncu 1'e çarptı!")
            return

        # Obstacle collision
        if new_head in self.obstacles and not invulnerable:
            self._trigger_vs_game_over("Oyuncu 2 kayaya çarptı!")
            return

        self.snake_p2.insert(0, new_head)
        ate = False
        if self.food and new_head == self.food.pos:
            self.score_p2 += FOOD_CONFIG[self.food.kind]["points"]
            self.pending_growth_p2 = getattr(self, 'pending_growth_p2', 0) + FOOD_CONFIG[self.food.kind]["growth"]
            self.food = None
            self._spawn_main_food()
            ate = True

        if getattr(self, 'pending_growth_p2', 0) > 0:
            self.pending_growth_p2 -= 1
            if self.pending_growth_p2 <= 0:
                self.snake_p2.pop()
        else:
            self.snake_p2.pop()

    def _consume_food(self, food: Food, now: float, is_bonus: bool) -> None:
        cfg = FOOD_CONFIG[food.kind]
        character = self._get_current_character(True)
        bonus_mult = character.get("bonus_mult", 1.0)

        if now - self.last_eat_at <= 2.7:
            self.combo = min(9, self.combo + 1)
        else:
            self.combo = 1
        self.last_eat_at = now
        self.combo_clock = 3.0

        gain = cfg["points"] * self.combo
        if is_bonus:
            gain = int(gain * bonus_mult)
        if MODES[self.mode_index] == "Süre":
            gain = int(gain * 1.25)
        self.score += gain
        self.pending_growth += cfg["growth"]
        self.foods_eaten += 1

        label = f"+{gain}"
        if self.combo > 1:
            label += f" x{self.combo}"
        self._queue_floating_text(label, food.pos, cfg["color"], life=1.0)
        self._emit_particles(food.pos, cfg["color"], amount=18 if is_bonus else 14, speed=280)

        if food.kind == "peri":
            self.ghost_until = max(self.ghost_until, now + 6.0)
        elif food.kind == "nazar":
            self.magnet_until = max(self.magnet_until, now + 8.0)
        elif food.kind == "tas":
            self.turbo_until = max(self.turbo_until, now + 7.0)
        elif food.kind == "zümrüt":
            removed = min(6, len(self.obstacles))
            for _ in range(removed):
                if self.obstacles:
                    self.obstacles.pop()
            self.score += removed * 45
            self.flash_strength = 0.6
        elif food.kind == "can":
            self.lives = min(5, self.lives + 1)

        level_from_score = 1 + self.score // 1300
        if level_from_score > self.level:
            self.level = level_from_score
            self.screen_shake = 9.0
            self.flash_strength = 0.55

    def _on_crash(self, reason: str) -> None:
        head = self.snake[0]
        self._emit_particles(head, (255, 80, 80), amount=36, speed=360)
        self.screen_shake = 14.0
        self.flash_strength = 0.75
        self.damage_flash_until = time.monotonic() + 0.3
        
        self.lives -= 1
        if self.lives <= 0:
            self.total_coins += self.score
            self._trigger_game_over(reason)
            return
        self._queue_floating_text("-1 CAN", head, (255, 100, 100), life=1.25)

        center_x = GRID_COLS // 2
        center_y = GRID_ROWS // 2
        start_length = self._get_current_character(True).get("start_length", 5)
        self.snake = [(center_x - i, center_y) for i in range(start_length)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.pending_growth = 0
        self.invulnerable_until = time.monotonic() + 2.0

    def _trigger_vs_game_over(self, reason: str) -> None:
        self.game_over_reason = reason
        self.state = "gameover"

    def _trigger_game_over(self, reason: str) -> None:
        self.game_over_reason = reason
        self.state = "gameover"
        self.high_scores.append(self.score)
        self.high_scores = sorted(self.high_scores, reverse=True)[:10]
        self._save_scores()

    def _draw(self) -> None:
        now = time.monotonic()
        
        self._draw_background(now)

        shake_x = 0.0
        shake_y = 0.0
        if self.screen_shake > 0.0:
            amplitude = self.screen_shake * 0.7
            shake_x = self.rng.uniform(-amplitude, amplitude)
            shake_y = self.rng.uniform(-amplitude, amplitude)

        if self.state in ("playing", "paused", "gameover"):
            self._draw_playfield(shake_x, shake_y, now)
            self._draw_trail(shake_x, shake_y)
            self._draw_trail_p2(shake_x, shake_y)
            self._draw_obstacles(shake_x, shake_y, now)
            self._draw_foods(shake_x, shake_y, now)
            self._draw_snake(shake_x, shake_y, now, False)
            if self.vs_mode:
                self._draw_snake(shake_x, shake_y, now, True)
            self._draw_particles_text(shake_x, shake_y)
            self._draw_hud(now)

            self.screen.blit(self.overlay_vignette, (0, 0))
            
            if now < self.damage_flash_until:
                damage = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                flash = (self.damage_flash_until - now) / 0.3
                damage.fill((255, 0, 0, int(180 * flash)))
                self.screen.blit(damage, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            
            if self.flash_strength > 0.0:
                flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                flash.fill((255, 255, 255, int(180 * self.flash_strength)))
                self.screen.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        self._draw_scanlines()

        if self.state == "character_select":
            self._draw_character_select()
        elif self.state == "menu":
            self._draw_menu()
        elif self.state == "paused":
            self._draw_pause()
        elif self.state == "gameover":
            self._draw_game_over()

    def _draw_background(self, now: float) -> None:
        for y in range(WINDOW_HEIGHT):
            r = int(20 + y * 0.02)
            g = int(10 + y * 0.015)
            b = int(40 + y * 0.01)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        
        moon_x = WINDOW_WIDTH - 200
        moon_y = 150
        pygame.draw.circle(self.screen, (255, 250, 220), (moon_x, moon_y), 60)
        pygame.draw.circle(self.screen, (20, 10, 30), (moon_x, moon_y), 55)
        
        for i in range(80):
            x = (i * 137 + now * 10) % WINDOW_WIDTH
            y = (i * 97 + now * 5) % (WINDOW_HEIGHT * 0.5)
            brightness = 150 + 100 * math.sin(now * 3 + i)
            pygame.draw.circle(self.screen, (brightness, brightness, min(255, brightness + 30)), (int(x), int(y)), 1 + i % 2)
        
        for cloud in self.clouds:
            cloud_surf = pygame.Surface((int(cloud['size'] * 2), int(cloud['size'])), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surf, (200, 180, 150, int(cloud['opacity'])), (0, 0, cloud['size'] * 2, cloud['size']))
            self.screen.blit(cloud_surf, (cloud['x'], cloud['y']))

    def _draw_scanlines(self) -> None:
        lines = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for y in range(0, WINDOW_HEIGHT, 4):
            lines.set_at((0, y), (0, 0, 0, 20))
        self.screen.blit(lines, (0, 0))

    def _draw_playfield(self, shake_x: float, shake_y: float, now: float) -> None:
        base = self.play_rect.move(shake_x, shake_y)
        
        glow = pygame.Surface((PLAY_WIDTH + 50, PLAY_HEIGHT + 50), pygame.SRCALPHA)
        pulse = int(80 + 40 * math.sin(now * 2))
        pygame.draw.rect(glow, (180, 100, 50, pulse // 3), glow.get_rect(), border_radius=25)
        self.screen.blit(glow, (base.x - 25, base.y - 25), special_flags=pygame.BLEND_RGBA_ADD)
        
        pygame.draw.rect(self.screen, (15, 10, 25), base, border_radius=18)
        pygame.draw.rect(self.screen, (180, 120, 60), base, width=4, border_radius=18)

        tint = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT), pygame.SRCALPHA)
        tint.fill((10, 15, 25, 70))
        self.screen.blit(tint, base.topleft)
        self.screen.blit(self.background_grid, base.topleft)

    def _draw_trail(self, shake_x: float, shake_y: float) -> None:
        for trail_point in self.trail:
            alpha = int(255 * (trail_point.life / trail_point.max_life) * 0.7)
            size = int(CELL_SIZE * 0.7 * (trail_point.life / trail_point.max_life))
            
            glow = pygame.Surface((size + 12, size + 12), pygame.SRCALPHA)
            glow_color = (*trail_point.color, min(255, alpha))
            pygame.draw.circle(glow, glow_color, ((size + 12) // 2, (size + 12) // 2), (size + 6) // 2)
            self.screen.blit(glow, (int(trail_point.pos.x - (size + 12) // 2 + shake_x), int(trail_point.pos.y - (size + 12) // 2 + shake_y)), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_trail_p2(self, shake_x: float, shake_y: float) -> None:
        if not self.vs_mode:
            return
        for trail_point in self.trail_p2:
            alpha = int(255 * (trail_point.life / trail_point.max_life) * 0.7)
            size = int(CELL_SIZE * 0.7 * (trail_point.life / trail_point.max_life))
            
            glow = pygame.Surface((size + 12, size + 12), pygame.SRCALPHA)
            glow_color = (*trail_point.color, min(255, alpha))
            pygame.draw.circle(glow, glow_color, ((size + 12) // 2, (size + 12) // 2), (size + 6) // 2)
            self.screen.blit(glow, (int(trail_point.pos.x - (size + 12) // 2 + shake_x), int(trail_point.pos.y - (size + 12) // 2 + shake_y)), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_obstacles(self, shake_x: float, shake_y: float, now: float) -> None:
        pulse = int(50 + 30 * (1 + math.sin(now * 3.0)))
        for ox, oy in self.obstacles:
            x = self.play_rect.left + ox * CELL_SIZE + 2 + shake_x
            y = self.play_rect.top + oy * CELL_SIZE + 2 + shake_y
            rect = pygame.Rect(int(x), int(y), CELL_SIZE - 4, CELL_SIZE - 4)
            
            pygame.draw.rect(self.screen, (80, 60, 50), rect, border_radius=6)
            pygame.draw.rect(self.screen, (140, 100, 70), rect, 2, border_radius=6)
            
            gl = pygame.Surface((CELL_SIZE + 8, CELL_SIZE + 8), pygame.SRCALPHA)
            pygame.draw.circle(gl, (150, 100, 80, pulse), ((CELL_SIZE + 8) // 2, (CELL_SIZE + 8) // 2), (CELL_SIZE + 4) // 2)
            self.screen.blit(gl, (rect.x - 4, rect.y - 4), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_foods(self, shake_x: float, shake_y: float, now: float) -> None:
        for food in (self.food, self.bonus_food):
            if food is None:
                continue
            cfg = FOOD_CONFIG[food.kind]
            fx, fy = self._grid_to_screen(food.pos)
            cx = fx + CELL_SIZE // 2 + shake_x
            cy = fy + CELL_SIZE // 2 + shake_y
            radius = 7 + int(2.5 * math.sin(now * 6.0 + fx * 0.03 + fy * 0.02))
            
            for layer in range(3):
                lr = radius + layer * 8
                la = 100 - layer * 30
                g = pygame.Surface((lr * 2 + 20, lr * 2 + 20), pygame.SRCALPHA)
                pygame.draw.circle(g, (*cfg["color"], la), (lr + 10, lr + 10), lr)
                self.screen.blit(g, (int(cx - lr - 10), int(cy - lr - 10)), special_flags=pygame.BLEND_RGBA_ADD)
            
            pygame.draw.circle(self.screen, cfg["color"], (int(cx), int(cy)), radius)
            pygame.draw.circle(self.screen, (255, 255, 200), (int(cx - radius * 0.3), int(cy - radius * 0.3)), max(1, radius // 3))

    def _draw_snake(self, shake_x: float, shake_y: float, now: float, is_p2: bool = False) -> None:
        snake = self.snake_p2 if is_p2 else self.snake
        character = self._get_current_character(not is_p2)
        direction = self.direction_p2 if is_p2 else self.direction
        
        invulnerable = now <= (self.invulnerable_p2 if is_p2 else self.invulnerable_until)
        if invulnerable and int(now * 12) % 2 == 0:
            return

        ghosted = now <= self.ghost_until
        primary = character["primary"]
        secondary = character["secondary"]
        glow = character["glow"]
        
        for i, segment in enumerate(snake):
            sx, sy = self._grid_to_screen(segment)
            sx += shake_x
            sy += shake_y
            
            shadow = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 80))
            self.screen.blit(shadow, (sx + 4, sy + 4))
            
            rect = pygame.Rect(int(sx + 2), int(sy + 2), CELL_SIZE - 4, CELL_SIZE - 4)
            t = i / max(1, len(snake) - 1)
            
            if ghosted:
                color = (int(200 - 80 * t), int(200 + 50 * t), int(255 - 50 * t))
            else:
                color = (
                    int(secondary[0] + (primary[0] - secondary[0]) * (1 - t)),
                    int(secondary[1] + (primary[1] - secondary[1]) * (1 - t)),
                    int(secondary[2] + (primary[2] - secondary[2]) * (1 - t)),
                )

            gl = pygame.Surface((CELL_SIZE + 10, CELL_SIZE + 10), pygame.SRCALPHA)
            ga = int(100 * (1 - t))
            pygame.draw.circle(gl, (*glow, ga), ((CELL_SIZE + 10) // 2, (CELL_SIZE + 10) // 2), (CELL_SIZE + 6) // 2)
            self.screen.blit(gl, (rect.x - 5, rect.y - 5), special_flags=pygame.BLEND_RGBA_ADD)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=10)
            
            if i == 0:
                self._draw_eyes(rect, now, direction)

    def _draw_eyes(self, head_rect: pygame.Rect, now: float, direction: tuple) -> None:
        dx, dy = direction
        forward = pygame.Vector2(dx, dy)
        side = pygame.Vector2(-dy, dx)
        center = pygame.Vector2(head_rect.centerx, head_rect.centery)
        
        off = side * 5
        fwd = forward * 3
        left_eye = center + off + fwd
        right_eye = center - off + fwd
        
        for eye in [left_eye, right_eye]:
            gl = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.circle(gl, (255, 255, 200, 80), (9, 9), 9)
            self.screen.blit(gl, (int(eye.x - 9), int(eye.y - 9)), special_flags=pygame.BLEND_RGBA_ADD)
        
        pygame.draw.circle(self.screen, (255, 255, 255), left_eye, 5)
        pygame.draw.circle(self.screen, (255, 255, 255), right_eye, 5)
        
        pup = forward * 2
        pygame.draw.circle(self.screen, (20, 20, 30), left_eye + pup, 3)
        pygame.draw.circle(self.screen, (20, 20, 30), right_eye + pup, 3)

    def _draw_particles_text(self, shake_x: float, shake_y: float) -> None:
        for p in self.particles:
            alpha = int(255 * (p.life / p.max_life))
            color = (*p.color, max(0, min(255, alpha)))
            gl = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(gl, color, (10, 10), max(1, int(p.radius * 1.5)))
            self.screen.blit(gl, (int(p.pos.x - 10 + shake_x), int(p.pos.y - 10 + shake_y)), special_flags=pygame.BLEND_RGBA_ADD)

        for txt in self.floaters:
            alpha = max(0, min(255, int(255 * (txt.life / txt.max_life))))
            scale = 1.0 + (1.0 - txt.life / txt.max_life) * 0.3
            font = pygame.font.Font(None, int(30 * scale))
            surf = font.render(txt.text, True, txt.color)
            surf.set_alpha(alpha)
            rect = surf.get_rect(center=(int(txt.pos.x + shake_x), int(txt.pos.y + shake_y)))
            self.screen.blit(surf, rect)

    def _draw_hud(self, now: float) -> None:
        char1 = self._get_current_character(True)
        mode_name = MODES[self.mode_index]
        top = pygame.Rect(30, 15, WINDOW_WIDTH - 60, 48)
        pygame.draw.rect(self.screen, (5, 10, 20, 220), top, border_radius=10)
        pygame.draw.rect(self.screen, (180, 130, 60), top, 2, border_radius=10)

        hearts1 = "♥" * self.lives
        
        if self.vs_mode:
            hearts2 = "♥" * self.lives_p2
            char1_name = char1["name"]
            char2 = self._get_current_character(False)
            char2_name = char2["name"]
            left_text = f"P1: {char1_name} | SKOR: {self.score} | P2: {char2_name} | SKOR: {self.score_p2}"
        else:
            left_text = f"{char1['name']} | {mode_name} | SKOR: {self.score:08d} | SEVİYE: {self.level} | CAN: {hearts1}"
        
        ls = self.font_small.render(left_text, True, (240, 220, 180))
        self.screen.blit(ls, (top.x + 15, top.y + 12))

        if MODES[self.mode_index] == "Süre":
            ss = self.font_small.render(f" SÜRE {self._remaining_blitz_seconds()}s", True, (255, 230, 150))
            self.screen.blit(ss, (top.right - ss.get_width() - 15, top.y + 12))

        ctrl = self.font_small.render("WASD: P1 | OKLAR: P2 | P: Dur | M: Menü | F11: Tam Ekran", True, (140, 120, 80))
        self.screen.blit(ctrl, (30, WINDOW_HEIGHT - 20))

    def _draw_character_select(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 15, 220))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("KIZIL ELMA", True, (255, 200, 50))
        ts = self.font_title.render("KIZIL ELMA", True, (100, 50, 0))
        self.screen.blit(ts, (WINDOW_WIDTH // 2 - title.get_width() // 2 + 4, 54))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        
        subtitle = self.font_h2.render("KARAKTERİNİ SEÇ", True, (200, 150, 50))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 120))

        # VS Mode info
        is_vs = MODES[self.mode_index] == "VS Modu"
        
        # Player 1 card
        p1_y = 200
        if is_vs:
            p1_label = self.font_h2.render("OYUNCU 1 (WASD)", True, (100, 200, 100))
            self.screen.blit(p1_label, (WINDOW_WIDTH // 4 - p1_label.get_width() // 2, p1_y))
        
        # Player 1 character selection
        char1 = SNAKE_CHARACTERS[self.character_keys[self.character_index]]
        card1 = pygame.Rect(WINDOW_WIDTH // 4 - 100, p1_y + 40, 200, 200)
        pygame.draw.rect(self.screen, (10, 15, 30), card1, border_radius=12)
        pygame.draw.rect(self.screen, char1["primary"], card1, 3, border_radius=12)
        
        # Snake preview
        for i in range(5):
            seg_x = card1.x + 40 + i * 25
            t = i / 4
            color = (
                int(char1["secondary"][0] + (char1["primary"][0] - char1["secondary"][0]) * (1 - t)),
                int(char1["secondary"][1] + (char1["primary"][1] - char1["secondary"][1]) * (1 - t)),
                int(char1["secondary"][2] + (char1["primary"][2] - char1["secondary"][2]) * (1 - t)),
            )
            pygame.draw.circle(self.screen, color, (seg_x, card1.y + 100), 18 - i)
        
        name1 = self.font_body.render(char1["name"], True, char1["primary"])
        self.screen.blit(name1, (card1.centerx - name1.get_width() // 2, card1.y + 140))
        
        desc1 = self.font_small.render(char1["description"], True, (180, 180, 180))
        self.screen.blit(desc1, (card1.centerx - desc1.get_width() // 2, card1.y + 170))

        # Player 2 card (for VS mode)
        if is_vs:
            p2_label = self.font_h2.render("OYUNCU 2 (OKLAR)", True, (200, 100, 100))
            self.screen.blit(p2_label, (WINDOW_WIDTH * 3 // 4 - p2_label.get_width() // 2, p1_y))
            
            char2 = SNAKE_CHARACTERS[self.character_keys[self.character_index_p2]]
            card2 = pygame.Rect(WINDOW_WIDTH * 3 // 4 - 100, p1_y + 40, 200, 200)
            pygame.draw.rect(self.screen, (10, 15, 30), card2, border_radius=12)
            pygame.draw.rect(self.screen, char2["primary"], card2, 3, border_radius=12)
            
            for i in range(5):
                seg_x = card2.x + 40 + i * 25
                t = i / 4
                color = (
                    int(char2["secondary"][0] + (char2["primary"][0] - char2["secondary"][0]) * (1 - t)),
                    int(char2["secondary"][1] + (char2["primary"][1] - char2["secondary"][1]) * (1 - t)),
                    int(char2["secondary"][2] + (char2["primary"][2] - char2["secondary"][2]) * (1 - t)),
                )
                pygame.draw.circle(self.screen, color, (seg_x, card2.y + 100), 18 - i)
            
            name2 = self.font_body.render(char2["name"], True, char2["primary"])
            self.screen.blit(name2, (card2.centerx - name2.get_width() // 2, card2.y + 140))
            
            desc2 = self.font_small.render(char2["description"], True, (180, 180, 180))
            self.screen.blit(desc2, (card2.centerx - desc2.get_width() // 2, card2.y + 170))

        # Mode selection
        mode_y = 480
        mode_label = self.font_h2.render("OYUN MODU:", True, (200, 180, 100))
        self.screen.blit(mode_label, (WINDOW_WIDTH // 2 - mode_label.get_width() // 2, mode_y))
        
        for idx, name in enumerate(MODES):
            x = WINDOW_WIDTH // 2 - 200 + idx * 100
            sel = idx == self.mode_index
            if sel:
                ms = self.font_body.render(f"► {name}", True, (255, 220, 150))
            else:
                ms = self.font_body.render(name, True, (140, 140, 140))
            self.screen.blit(ms, (x, mode_y + 35))

        # Instructions
        if is_vs:
            info = ["← → : P1 Karakter | Q E : P2 Karakter | ENTER : Başla"]
        else:
            info = ["← → : Karakter | ↑ ↓ : Mod | ENTER : Başla"]
        
        for i, line in enumerate(info):
            txt = self.font_small.render(line, True, (160, 140, 100))
            self.screen.blit(txt, (WINDOW_WIDTH // 2 - txt.get_width() // 2, mode_y + 80 + i * 25))

    def _draw_menu(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 15, 190))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("KIZIL ELMA", True, (255, 200, 50))
        ts = self.font_title.render("KIZIL ELMA", True, (100, 50, 0))
        self.screen.blit(ts, (WINDOW_WIDTH // 2 - title.get_width() // 2 + 4, 104))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        subtitle = self.font_h2.render("EFSANE BAŞLIYOR", True, (200, 150, 50))
        self.screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 160))

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 280, 210, 560, 320)
        pygame.draw.rect(self.screen, (10, 15, 35), panel, border_radius=18)
        pygame.draw.rect(self.screen, (180, 130, 60), panel, 3, border_radius=18)

        for idx, name in enumerate(MODES):
            y = panel.y + 25 + idx * 65
            sel = idx == self.mode_index
            if sel:
                gl = pygame.Surface((panel.w - 20, 50), pygame.SRCALPHA)
                gl.fill((150, 100, 50, 80))
                self.screen.blit(gl, (panel.x + 10, y - 6))
                pygame.draw.rect(self.screen, (255, 200, 100), (panel.x + 10, y - 6, panel.w - 20, 50), 2, border_radius=10)
            label = self.font_h2.render(f"{idx + 1}. {name}", True, (250, 230, 200) if sel else (140, 120, 80))
            self.screen.blit(label, (panel.x + 25, y))

        info = ["ENTER / SPACE: Başla | C: Karakter | F11: Tam Ekran", "ESC: Çıkış"]
        for i, line in enumerate(info):
            txt = self.font_small.render(line, True, (160, 140, 100))
            self.screen.blit(txt, (WINDOW_WIDTH // 2 - txt.get_width() // 2, 550 + i * 22))

    def _draw_pause(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self.font_h1.render("DURAKLADI", True, (200, 180, 100))
        h1 = self.font_body.render("P veya ESC ile devam et", True, (160, 140, 80))
        h2 = self.font_body.render("R: Yeniden başla, M: Menü", True, (160, 140, 80))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 280))
        self.screen.blit(h1, (WINDOW_WIDTH // 2 - h1.get_width() // 2, 350))
        self.screen.blit(h2, (WINDOW_WIDTH // 2 - h2.get_width() // 2, 390))

    def _draw_game_over(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        if self.vs_mode:
            title = self.font_h1.render("KAZANAN!", True, (255, 215, 0))
            # Determine winner
            if "Oyuncu 1" in self.game_over_reason:
                winner = "OYUNCU 2 KAZANDI!"
                color = (100, 200, 100)
            else:
                winner = "OYUNCU 1 KAZANDI!"
                color = (255, 215, 0)
            winner_text = self.font_h1.render(winner, True, color)
            reason = self.font_body.render(self.game_over_reason, True, (200, 150, 150))
            
            self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 160))
            self.screen.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, 220))
            self.screen.blit(reason, (WINDOW_WIDTH // 2 - reason.get_width() // 2, 280))
        else:
            title = self.font_h1.render("OYUN BİTTİ", True, (200, 80, 80))
            reason = self.font_body.render(f"Sebep: {self.game_over_reason}", True, (200, 150, 150))
            score = self.font_h1.render(f"Skor: {self.score:,}", True, (255, 230, 150))
            
            self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 160))
            self.screen.blit(reason, (WINDOW_WIDTH // 2 - reason.get_width() // 2, 220))
            self.screen.blit(score, (WINDOW_WIDTH // 2 - score.get_width() // 2, 270))

        prompt = self.font_body.render("Enter/Space: Tekrar | M: Menü", True, (160, 180, 200))
        self.screen.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 550))

    def self_test(self) -> bool:
        for _ in range(3):
            self._handle_events()
            self._update(1 / 60.0)
            self._draw()
            pygame.display.flip()
        pygame.quit()
        return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="KIZIL ELMA")
    parser.add_argument("--self-test", action="store_true", help="Run test")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    game = KizilElmaGame()
    if args.self_test:
        ok = game.self_test()
        raise SystemExit(0 if ok else 1)
    game.run()


if __name__ == "__main__":
    main()

