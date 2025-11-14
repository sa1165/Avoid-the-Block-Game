"""
Avoid The Block - Survival Game (Pygame)
Single-file game with polished UI/UX and animations.

Controls:
- Left / A : move left
- Right / D: move right
- Space: pause / resume (in-game)
- Enter: confirm in menus
- Esc / Q: quit

Leaderboard is stored in leaderboard.json (created automatically).
"""

import pygame
import random
import math
import json
import os
from collections import deque

# --------------------------
# Config
# --------------------------
WIDTH, HEIGHT = 720, 900
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 70, 18
PLAYER_Y = HEIGHT - 110
OBSTACLE_MIN_W, OBSTACLE_MAX_W = 40, 140
OBSTACLE_MIN_H, OBSTACLE_MAX_H = 30, 70
SPAWN_INTERVAL = 700  # ms initial
SPEED_BASE = 2.6
SPEED_INCREASE_PER_SCORE = 0.05
MAX_OBSTACLES_PER_WAVE = 3
LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERS = 5

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Avoid The Block — Survival (Developed by Sanjeev)")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont("Segoe UI", 44)
font_med = pygame.font.SysFont("Segoe UI", 28)
font_small = pygame.font.SysFont("Segoe UI", 20)
icon = pygame.Surface((1,1))
pygame.display.set_icon(icon)

# --------------------------
# Audio (optional assets)
# --------------------------
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
    AUDIO_OK = False  # Disabled audio
except Exception:
    AUDIO_OK = False

ASSETS_MUSIC_DIR = os.path.join("assets", "music")
ASSETS_SFX_DIR = os.path.join("assets", "sfx")
_SOUNDS = {}


def _ensure_dirs():
    os.makedirs(ASSETS_MUSIC_DIR, exist_ok=True)
    os.makedirs(ASSETS_SFX_DIR, exist_ok=True)


def _generate_tone(path, freq=440.0, duration=0.2, volume=0.3, samplerate=44100):
    """Generate a simple sine-wave WAV file at `path`. Overwrites if exists."""
    import wave, struct, math
    n_samples = int(samplerate * duration)
    amp = int(32767 * volume)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        frames = bytearray()
        for i in range(n_samples):
            t = float(i) / samplerate
            sample = int(amp * math.sin(2.0 * math.pi * freq * t))
            frames.extend(struct.pack('<h', sample))
        wf.writeframes(frames)


def ensure_placeholder_sounds():
    """Create placeholder SFX and menu music if no assets are provided.
    This allows the game to play sounds immediately without shipping binary files.
    """
    _ensure_dirs()
    # SFX
    sfx_files = {
        'hit.wav': (120.0, 0.45, 0.6),
        'click.wav': (800.0, 0.08, 0.5),
        'hover.wav': (600.0, 0.06, 0.35),
        'score.wav': (1200.0, 0.10, 0.45),
        'pickup.wav': (1000.0, 0.09, 0.45),
    }
    for name, (freq, dur, vol) in sfx_files.items():
        path = os.path.join(ASSETS_SFX_DIR, name)
        # only generate if missing to preserve custom assets
        if not os.path.exists(path):
            try:
                _generate_tone(path, freq=freq, duration=dur, volume=vol)
            except Exception:
                pass

    menu_path = os.path.join(ASSETS_MUSIC_DIR, 'menu_music.wav')
    if not os.path.exists(menu_path):
        try:
            import wave, struct, math
            samplerate = 44100
            duration = 8.0
            n_samples = int(samplerate * duration)
            amp = int(32767 * 0.12)
            # gentle chord progression (I - vi - IV - V) in a relaxed tonality
            chords = [ (220.0, 261.63, 329.63),  # A-like chord
                       (196.0, 246.94, 293.66), # G major-ish
                       (165.0, 220.0, 261.63),  # E/C flavor
                       (196.0, 247.0, 294.0) ]  # G variation
            with wave.open(menu_path, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                frames = bytearray()
                for i in range(n_samples):
                    t = float(i) / samplerate
                    # chord index cycles every 2 seconds
                    chord_idx = int((t / 2.0)) % len(chords)
                    freqs = chords[chord_idx]
                    # soft pad with multiple harmonics and slow amplitude envelope
                    s = 0.0
                    s += 0.5 * math.sin(2.0 * math.pi * freqs[0] * t)
                    s += 0.25 * math.sin(2.0 * math.pi * freqs[0] * 2.0 * t)
                    s += 0.35 * math.sin(2.0 * math.pi * freqs[1] * t)
                    s += 0.15 * math.sin(2.0 * math.pi * freqs[2] * t)
                    # gentle arpeggio
                    arp = 0.12 * math.sin(2.0 * math.pi * (freqs[0]*2.0 + (freqs[2]-freqs[1])*0.5) * (t*1.5))
                    s += arp
                    # slow tremolo/envelope per chord
                    env = 0.5 * (1.0 - math.cos(math.pi * ((t % 2.0) / 2.0)))
                    sample = int(amp * s * env * 0.8)
                    frames.extend(struct.pack('<h', max(-32767, min(32767, sample))))
                wf.writeframes(frames)
        except Exception:
            pass
    game_path = os.path.join(ASSETS_MUSIC_DIR, 'game_music.wav')
    if not os.path.exists(game_path):
        try:
            import wave, struct, math
            samplerate = 44100
            duration = 12.0
            n_samples = int(samplerate * duration)
            amp = int(32767 * 0.08)
            # ambient layered pads with slow movement
            with wave.open(game_path, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                frames = bytearray()
                for i in range(n_samples):
                    t = float(i) / samplerate
                    low = 0.25 * math.sin(2.0 * math.pi * 55.0 * t)
                    mid = 0.35 * math.sin(2.0 * math.pi * 110.0 * t + 0.5 * math.sin(0.05 * math.pi * t))
                    high = 0.20 * math.sin(2.0 * math.pi * 220.0 * t + 0.25 * math.sin(0.08 * math.pi * t))
                    # slow evolving texture
                    texture = 0.12 * math.sin(2.0 * math.pi * 0.5 * t) * math.sin(2.0 * math.pi * 440.0 * t)
                    sample = int(amp * (low + mid + high + texture))
                    frames.extend(struct.pack('<h', max(-32767, min(32767, sample))))
                wf.writeframes(frames)
        except Exception:
            pass

def load_sounds():
    """Load optional sound assets. Missing files are allowed (silent fallback)."""
    if not AUDIO_OK:
        return
    def _try_load(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None

    # sfx
    _SOUNDS['hit'] = _try_load(os.path.join(ASSETS_SFX_DIR, 'hit.wav'))
    _SOUNDS['click'] = _try_load(os.path.join(ASSETS_SFX_DIR, 'click.wav'))
    _SOUNDS['hover'] = _try_load(os.path.join(ASSETS_SFX_DIR, 'hover.wav'))
    _SOUNDS['score'] = _try_load(os.path.join(ASSETS_SFX_DIR, 'score.wav'))
    _SOUNDS['pickup'] = _try_load(os.path.join(ASSETS_SFX_DIR, 'pickup.wav'))

    # music: we'll use pygame.mixer.music for background music
    _SOUNDS['menu_music_file'] = None
    # prefer .ogg but accept .wav placeholders
    for ext in ('.ogg', '.wav'):
        menu_path = os.path.join(ASSETS_MUSIC_DIR, 'menu_music' + ext)
        if os.path.exists(menu_path):
            _SOUNDS['menu_music_file'] = menu_path
            break
    for ext in ('.ogg', '.wav'):
        gm = os.path.join(ASSETS_MUSIC_DIR, 'game_music' + ext)
        if os.path.exists(gm):
            _SOUNDS['game_music_file'] = gm
            break


def play_sfx(name):
    if not AUDIO_OK:
        return
    s = _SOUNDS.get(name)
    if s:
        try:
            s.play()
        except Exception:
            pass

def play_menu_music(loop=True):
    if not AUDIO_OK:
        return
    mf = _SOUNDS.get('menu_music_file')
    try:
        if mf:
            pygame.mixer.music.load(mf)
            pygame.mixer.music.play(-1 if loop else 0)
    except Exception:
        pass

def stop_menu_music():
    if not AUDIO_OK:
        return
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

def play_game_music(loop=True):
    if not AUDIO_OK:
        return
    mf = _SOUNDS.get('game_music_file')
    try:
        if mf:
            pygame.mixer.music.load(mf)
            pygame.mixer.music.play(-1 if loop else 0)
    except Exception:
        pass

# generate placeholder sounds if asset folders are empty, then load sounds
ensure_placeholder_sounds()
load_sounds()

# --------------------------
# Colors & palette
# --------------------------
BG_TOP = (18, 24, 37)
BG_BOTTOM = (15, 35, 60)
ACCENT = (94, 230, 182)
ACCENT2 = (118, 199, 255)
WHITE = (245, 245, 245)
DARK = (20, 20, 30)
RED = (239, 83, 80)
YELLOW = (255, 214, 102)
UI_PANEL = (22, 30, 45)

# Theme definitions: name -> palette
THEMES = {
    'DarkBlueGlow': {
        'bg_top': (18, 24, 37),
        'bg_bottom': (15, 35, 60),
        'accent': (94, 230, 182),
        'accent2': (118, 199, 255),
        'ui_panel': (22, 30, 45),
        'player_color': (94, 230, 182),
    },
    'Neon': {
        'bg_top': (10, 10, 20),
        'bg_bottom': (5, 2, 20),
        'accent': (255, 85, 255),
        'accent2': (0, 255, 170),
        'ui_panel': (18, 16, 30),
        'player_color': (255, 85, 255),
    },
    'Cyberpunk': {
        'bg_top': (12, 6, 20),
        'bg_bottom': (28, 6, 40),
        'accent': (255, 120, 60),
        'accent2': (200, 40, 200),
        'ui_panel': (30, 16, 36),
        'player_color': (255, 120, 60),
    },
    'Minimal': {
        'bg_top': (245, 245, 245),
        'bg_bottom': (230, 230, 230),
        'accent': (40, 40, 40),
        'accent2': (80, 80, 80),
        'ui_panel': (250, 250, 250),
        'player_color': (40, 40, 40),
    },
    'Retro': {
        'bg_top': (6, 10, 24),
        'bg_bottom': (2, 6, 20),
        'accent': (120, 200, 100),
        'accent2': (180, 140, 80),
        'ui_panel': (14, 18, 28),
        'player_color': (120, 200, 100),
    }
}

# --------------------------
# Utilities
# --------------------------
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_leaderboard(board):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(board[:MAX_LEADERS], f, indent=2)
    except Exception as e:
        print("Failed saving leaderboard:", e)

SETTINGS_FILE = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_settings(s):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(s, f, indent=2)
    except Exception as e:
        print("Failed saving settings:", e)

def draw_text(surf, text, pos, font, color=WHITE, center=False):
    r = font.render(text, True, color)
    if center:
        rect = r.get_rect(center=pos)
        surf.blit(r, rect)
    else:
        surf.blit(r, pos)

# --------------------------
# Particle system for effects
# --------------------------
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.5, 1.2)
        self.size = random.randint(2, 5)
        self.age = 0
        self.color = random.choice([ACCENT, ACCENT2, YELLOW, RED])

    def update(self, dt):
        self.age += dt
        self.x += self.vx
        self.y += self.vy
        # gravity
        self.vy += 0.12
        # slight drag
        self.vx *= 0.995
        self.vy *= 0.995

    def draw(self, surf):
        a = max(0, 1 - (self.age / self.life))
        if a <= 0:
            return
        s = max(1, int(self.size * a))
        # draw particle on a small temporary surface with per-pixel alpha
        surf_s = pygame.Surface((s * 2 + 2, s * 2 + 2), pygame.SRCALPHA)
        col = (self.color[0], self.color[1], self.color[2], int(255 * a))
        pygame.draw.circle(surf_s, col, (s + 1, s + 1), s)
        surf.blit(surf_s, (int(self.x) - (s + 1), int(self.y) - (s + 1)))

# --------------------------
# Player
# --------------------------
class Player:
    def __init__(self):
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.x = WIDTH // 2 - self.w // 2
        self.y = PLAYER_Y
        self.speed = 8.5
        self.vx = 0.0
        self.friction = 0.85
        self.color = ACCENT
        self.hitbox = pygame.Rect(self.x, self.y, self.w, self.h)
        # dash mechanics
        self.dash_speed = 28.0
        self.dash_time = 0.12
        self.dash_cooldown = 0.8
        self.last_dash_t = -999.0
        self.dash_charges = 0

    def update(self, keys, dt):
        target_vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_vx = self.speed
        # smooth acceleration toward target_vx
        acc = 1.6
        self.vx += (target_vx - self.vx) * min(1, acc * dt)
        # apply friction when no input
        if target_vx == 0:
            self.vx *= self.friction
        self.x += self.vx
        # clamp
        if self.x < 20:
            self.x = 20
            self.vx = 0
        if self.x + self.w > WIDTH - 20:
            self.x = WIDTH - 20 - self.w
            self.vx = 0
        self.hitbox.topleft = (self.x, self.y)

    def dash(self, direction=None):
        now = pygame.time.get_ticks() / 1000.0
        if (now - self.last_dash_t) < self.dash_cooldown and self.dash_charges <= 0:
            return False
        # determine direction: -1 left, 1 right
        if direction is None:
            direction = -1 if self.vx < 0 else 1
        self.vx = direction * self.dash_speed
        self.last_dash_t = now
        if self.dash_charges > 0:
            self.dash_charges -= 1
        return True

    def draw(self, surf):
        # subtle gradient fill simulated with two rects
        pygame.draw.rect(surf, (int(self.color[0]*0.9), int(self.color[1]*0.9), int(self.color[2]*0.9)),
                         (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surf, self.color, (self.x+2, self.y+1, self.w-4, self.h-2))
        # small glow
        glow_rect = pygame.Rect(self.x-10, self.y-8, self.w+20, self.h+16)
        s = pygame.Surface((glow_rect.w, glow_rect.h), pygame.SRCALPHA)
        for i in range(4):
            alpha = 25 - i*6
            pygame.draw.rect(s, (ACCENT[0], ACCENT[1], ACCENT[2], alpha),
                             (i*2, i*2, glow_rect.w - i*4, glow_rect.h - i*4), border_radius=8)
        surf.blit(s, (glow_rect.left, glow_rect.top))

# --------------------------
# Obstacle
# --------------------------
class Obstacle:
    def __init__(self, x, w, h, speed):
        self.x = x
        self.y = -h - random.randint(0, 60)
        self.w = w
        self.h = h
        self.speed = speed
        # color variance
        tint = random.randint(-15, 15)
        self.color = (max(0, min(255, 230 + tint)),
                      max(0, min(255, 80 + tint)),
                      max(0, min(255, 100 + tint)))
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.sway = random.uniform(-0.5, 0.5)  # horizontal drift

    def update(self, dt):
        self.y += self.speed * dt
        # slight horizontal sway
        self.x += self.sway * dt * 30
        self.rect.topleft = (self.x, self.y)

    def draw(self, surf):
        # border
        pygame.draw.rect(surf, (20,20,25), self.rect, border_radius=6)
        pygame.draw.rect(surf, self.color, (self.x+3, self.y+3, self.w-6, self.h-6), border_radius=5)


class PowerUp:
    def __init__(self, x, kind, speed=2.0):
        self.kind = kind  # 'shield','slow','mult','dash'
        self.w = 36
        self.h = 36
        self.x = x
        self.y = -self.h - random.randint(0, 40)
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, dt):
        self.y += self.speed * dt
        self.rect.topleft = (self.x, self.y)

    def draw(self, surf):
        # simple circle icon with different colors per kind
        col = (200, 200, 200)
        if self.kind == 'shield':
            col = (100, 180, 255)
        elif self.kind == 'slow':
            col = (200, 120, 255)
        elif self.kind == 'mult':
            col = (255, 200, 60)
        elif self.kind == 'dash':
            col = (255, 100, 100)
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (self.w//2, self.h//2), min(self.w,self.h)//2)
        draw_text(s, self.kind[0].upper(), (self.w//2, self.h//2 - 2), font_small, color=(10,10,10), center=True)
        surf.blit(s, (self.x, self.y))

# --------------------------
# Game Manager
# --------------------------
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.particles = []
        self.score = 0
        self.best = 0
        self.spawn_timer = 0
        self.spawn_interval = SPAWN_INTERVAL
        self.powerups = []
        self.powerup_timer = 0
        self.powerup_interval = 12000  # ms between powerup spawns
        # active effects
        self.shield = False
        self.slow_remaining = 0.0
        self.mult_remaining = 0.0
        self.score_multiplier = 1
        self.speed_base = SPEED_BASE
        self.running = True
        self.playing = False
        self.paused = False
        self.last_time = pygame.time.get_ticks()
        self.difficulty_tick = 0
        self.leaderboard = load_leaderboard()
        # load settings and apply theme
        self.settings = load_settings()
        self.theme_name = self.settings.get('theme', 'DarkBlueGlow')
        if self.theme_name not in THEMES:
            self.theme_name = 'DarkBlueGlow'
        self.theme = THEMES[self.theme_name]
        # apply player color from theme
        try:
            self.player.color = self.theme.get('player_color', self.player.color)
        except Exception:
            pass

    def start(self):
        self.reset()
        self.playing = True
        self.score = 0
        self.spawn_interval = SPAWN_INTERVAL
        self.spawn_timer = 0

    def spawn_wave(self):
        # spawn 1..MAX obstacles at once with varied widths and positions
        num = random.randint(1, min(MAX_OBSTACLES_PER_WAVE, 1 + self.score // 8))
        attempts = 0
        for _ in range(num):
            w = random.randint(OBSTACLE_MIN_W, OBSTACLE_MAX_W)
            h = random.randint(OBSTACLE_MIN_H, OBSTACLE_MAX_H)
            x = random.randint(20, WIDTH - 20 - w)
            speed = self.speed_base + self.score * SPEED_INCREASE_PER_SCORE + random.random() * 0.6
            obs = Obstacle(x, w, h, speed)
            # simple non-overlap check
            ok = True
            for o in self.obstacles:
                if abs(o.x - obs.x) < (o.w + obs.w) * 0.5 and abs(o.y - obs.y) < 80:
                    ok = False
                    break
            if ok:
                self.obstacles.append(obs)
            attempts += 1
            if attempts > 8:
                break

    def spawn_powerup(self):
        kinds = ['shield', 'slow', 'mult', 'dash']
        # weighted choice: mult and shield rarer
        weights = [0.25, 0.25, 0.2, 0.3]
        kind = random.choices(kinds, weights)[0]
        x = random.randint(40, WIDTH - 40 - 36)
        pu = PowerUp(x, kind, speed=self.speed_base * 0.8)
        self.powerups.append(pu)

    def apply_powerup(self, kind):
        if kind == 'shield':
            self.shield = True
            play_sfx('pickup')
        elif kind == 'slow':
            self.slow_remaining = 2.2  # seconds
            play_sfx('pickup')
        elif kind == 'mult':
            self.mult_remaining = 10.0
            self.score_multiplier = 2
            play_sfx('pickup')
        elif kind == 'dash':
            # grant a short dash charge on pickup (player handles dash cooldown)
            self.player.dash_charges = getattr(self.player, 'dash_charges', 0) + 1
            play_sfx('pickup')

    def update(self, dt, keys):
        if not self.playing or self.paused:
            return
        # player
        self.player.update(keys, dt)

        # spawn logic
        self.spawn_timer += dt * 1000
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_wave()
            self.spawn_timer = 0
            # slowly decrease interval to increase difficulty
            self.spawn_interval = max(260, self.spawn_interval - random.randint(8, 22) - (self.score // 6))

        # powerup spawn logic
        self.powerup_timer += dt * 1000
        if self.powerup_timer >= self.powerup_interval:
            self.spawn_powerup()
            self.powerup_timer = 0

        # determine speed multiplier from slow effect
        speed_mult = 0.5 if self.slow_remaining > 0 else 1.0

        # update obstacles
        for o in list(self.obstacles):
            o.update(dt * 60 * speed_mult)  # scale dt so movement feels consistent
            if o.y > HEIGHT + 100:
                # score when obstacle passes safely
                self.score += int(1 * self.score_multiplier)
                play_sfx('score')
                self.obstacles.remove(o)
            # collision
            if o.rect.colliderect(self.player.hitbox):
                self.handle_collision(o)
                break

        # update powerups
        for p in list(self.powerups):
            p.update(dt * 60)
            if p.y > HEIGHT + 80:
                self.powerups.remove(p)
                continue
            if p.rect.colliderect(self.player.hitbox):
                # pickup
                self.apply_powerup(p.kind)
                if p in self.powerups:
                    self.powerups.remove(p)

        # update particles
        for p in list(self.particles):
            p.update(dt)
            if p.age >= p.life:
                self.particles.remove(p)

    def handle_collision(self, obstacle):
        # if shield active, consume it and produce a small effect
        if self.shield:
            self.shield = False
            for _ in range(12):
                self.particles.append(Particle(self.player.x + self.player.w//2, self.player.y + self.player.h//2))
            play_sfx('hit')
            return

        # create particle explosion centered on player
        for _ in range(36):
            self.particles.append(Particle(self.player.x + self.player.w//2, self.player.y + self.player.h//2))
        # play a small flash by drawing a full-screen overlay for frames (handled by draw)
        self.playing = False
        # update leaderboard best if needed
        play_sfx('hit')
        stop_menu_music()
        self.save_score_prompt()

    def draw_background(self, surf, t):
        # gradient background using theme
        bg_top = self.theme.get('bg_top', BG_TOP)
        bg_bottom = self.theme.get('bg_bottom', BG_BOTTOM)
        top = pygame.Surface((WIDTH, HEIGHT))
        for i in range(HEIGHT):
            r = bg_top[0] + (bg_bottom[0] - bg_top[0]) * (i/HEIGHT)
            g = bg_top[1] + (bg_bottom[1] - bg_top[1]) * (i/HEIGHT)
            b = bg_top[2] + (bg_bottom[2] - bg_top[2]) * (i/HEIGHT)
            pygame.draw.line(top, (int(r), int(g), int(b)), (0, i), (WIDTH, i))
        surf.blit(top, (0,0))
        # animated floating shapes
        for i in range(6):
            cx = (math.sin(t * 0.8 + i) + 1) * WIDTH * 0.5
            cy = (i+1) * 80 + math.cos(t*0.4 + i) * 16
            rad = 44 + (i * 6)
            s = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255,255,255,10 + i*8), (rad, rad), rad)
            surf.blit(s, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)

    def draw_ui_panel(self, surf):
        panel_h = 82
        ui_panel_col = self.theme.get('ui_panel', UI_PANEL)
        pygame.draw.rect(surf, ui_panel_col, (16, 14, WIDTH - 32, panel_h), border_radius=12)
        # score
        draw_text(surf, f"Score: {self.score}", (36, 28), font_med, color=WHITE)
        draw_text(surf, "Avoid the falling blocks!", (36, 52), font_small, color=(190,190,200))
        # right side
        draw_text(surf, f"Best: {self.leaderboard[0]['score'] if self.leaderboard else 0}", (WIDTH - 170, 28), font_med, color=self.theme.get('accent2', ACCENT2))
        draw_text(surf, "Space = Pause", (WIDTH - 170, 52), font_small, color=(180,180,190))
        # developer credit
        draw_text(surf, "Developed by Sanjeev", (WIDTH - 170, 72), font_small, color=(170,170,190))
        # active power-up indicators (left side under score)
        x0 = 36
        y0 = 72
        info = []
        if self.shield:
            info.append("Shield")
        if self.slow_remaining > 0:
            info.append(f"Slow {self.slow_remaining:.1f}s")
        if self.mult_remaining > 0:
            info.append(f"2x {self.mult_remaining:.0f}s")
        if getattr(self.player, 'dash_charges', 0) > 0:
            info.append(f"Dash x{self.player.dash_charges}")
        if info:
            draw_text(surf, " | ".join(info), (x0, y0), font_small, color=(200,200,200))

    def save_score_prompt(self):
        # after game over, prompt player name and store leaderboard
        # we'll show name entry UI in main loop
        pass

    def add_to_leaderboard(self, name, score):
        board = self.leaderboard
        board.append({"name": name, "score": score})
        board.sort(key=lambda x: x["score"], reverse=True)
        board = board[:MAX_LEADERS]
        save_leaderboard(board)
        self.leaderboard = board

    def draw(self, surf, t, flash=False):
        # background
        self.draw_background(surf, t)
        # UI panel
        self.draw_ui_panel(surf)
        # draw obstacles
        for o in self.obstacles:
            o.draw(surf)
        # draw powerups
        for pu in self.powerups:
            pu.draw(surf)
        # draw player
        self.player.draw(surf)
        # draw particles
        for p in self.particles:
            p.draw(surf)
        # subtle bottom ground
        pygame.draw.rect(surf, (10,12,18), (0, PLAYER_Y + PLAYER_HEIGHT + 12, WIDTH, HEIGHT - (PLAYER_Y + PLAYER_HEIGHT + 12)))
        # flash overlay on death
        if flash:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 120, 120, 140))
            surf.blit(overlay, (0,0))

# --------------------------
# Menu UI helpers
# --------------------------
def button(surf, rect, text, font, active=False):
    x,y,w,h = rect
    color = (40, 48, 64) if not active else (60, 80, 110)
    pygame.draw.rect(surf, color, rect, border_radius=10)
    draw_text(surf, text, (x + w//2, y + h//2), font, color=WHITE, center=True)

def show_start_menu(game):
    selecting = 0
    options = ["Play", "Themes", "Instructions", "Leaderboard", "Quit"]
    while True:
        dt = clock.tick(FPS) / 1000.0
        t = pygame.time.get_ticks() / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    play_sfx('click')
                    return options[selecting]
                if e.key in (pygame.K_DOWN, pygame.K_s):
                    play_sfx('hover')
                    selecting = (selecting + 1) % len(options)
                if e.key in (pygame.K_UP, pygame.K_w):
                    play_sfx('hover')
                    selecting = (selecting - 1) % len(options)

        # draw
        game.draw_background(screen, t)
        # title card (themed)
        title_panel_col = game.theme.get('ui_panel', UI_PANEL)
        pygame.draw.rect(screen, title_panel_col, (WIDTH//2 - 280, 80, 560, 140), border_radius=14)
        draw_text(screen, "Avoid The Block", (WIDTH//2, 120), font_large, color=game.theme.get('accent', ACCENT), center=True)
        draw_text(screen, "Survive as long as you can — move, dodge, endure.", (WIDTH//2, 160), font_med, color=(220,220,230), center=True)
        # developer credit on the start/title screen
        draw_text(screen, "Developed by Sanjeev", (WIDTH//2, 200), font_small, color=(190,190,200), center=True)
        # buttons
        bx = WIDTH//2 - 140
        by = 270
        b_w = 280
        b_h = 56
        for i, opt in enumerate(options):
            rect = (bx, by + i*(b_h + 18), b_w, b_h)
            button(screen, rect, opt, font_med, active=(i == selecting))
        # hint
        draw_text(screen, "Arrows or A/D to move. Press Enter to select.", (WIDTH//2, HEIGHT - 80), font_small, color=(200,200,200), center=True)
        # ensure menu music plays
        if AUDIO_OK and not pygame.mixer.music.get_busy():
            play_menu_music(loop=True)

        pygame.display.flip()

def show_instructions(game):
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                play_sfx('click')
                return
        bg = game.theme.get('bg_bottom', BG_BOTTOM)
        screen.fill(bg)
        draw_text(screen, "Instructions", (WIDTH//2, 80), font_large, color=game.theme.get('accent', ACCENT), center=True)
        instr = [
            "Move left and right to dodge falling obstacles.",
            "Each obstacle avoided increases your score.",
            "Difficulty increases over time (faster & more obstacles).",
            "Space to pause. When you collide the game ends.",
            "Try to top the leaderboard!"
        ]
        y = 180
        for line in instr:
            draw_text(screen, line, (WIDTH//2, y), font_med, color=WHITE, center=True)
            y += 54
        draw_text(screen, "Press Esc / Enter / Space to go back.", (WIDTH//2, HEIGHT - 80), font_small, center=True)
        pygame.display.flip()
        clock.tick(20)

def show_leaderboard(game):
    board = game.leaderboard
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                play_sfx('click')
                return
        bg = game.theme.get('bg_bottom', BG_BOTTOM)
        screen.fill(bg)
        draw_text(screen, "Leaderboard", (WIDTH//2, 80), font_large, color=game.theme.get('accent', ACCENT), center=True)
        y = 170
        if not board:
            draw_text(screen, "No scores yet — be the first!", (WIDTH//2, y), font_med, center=True)
        else:
            for i, rec in enumerate(board):
                draw_text(screen, f"{i+1}. {rec['name'][:12]:12s} — {rec['score']:4d}", (WIDTH//2, y), font_med, center=True)
                y += 56
        draw_text(screen, "Press Esc / Enter / Space to go back.", (WIDTH//2, HEIGHT - 80), font_small, center=True)
        pygame.display.flip()
        clock.tick(20)

# --------------------------
# Name input UI for high score
# --------------------------
def name_entry_prompt(game, score):
    name = ""
    active = True
    prompt = "Enter name (max 12 chars):"
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    nm = name.strip()[:12] or "Player"
                    game.add_to_leaderboard(nm, score)
                    return
                if e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif e.key == pygame.K_ESCAPE:
                    return
                else:
                    if len(name) < 12 and e.unicode.isprintable():
                        name += e.unicode
        # render
        bg = game.theme.get('bg_bottom', BG_BOTTOM)
        screen.fill(bg)
        draw_text(screen, "Game Over!", (WIDTH//2, 120), font_large, color=RED, center=True)
        draw_text(screen, f"Your Score: {score}", (WIDTH//2, 190), font_med, center=True)
        draw_text(screen, prompt, (WIDTH//2, 270), font_med, center=True)
        # input box
        box_rect = pygame.Rect(WIDTH//2 - 200, 320, 400, 56)
        pygame.draw.rect(screen, (40,40,50), box_rect, border_radius=8)
        draw_text(screen, name + ("|" if (pygame.time.get_ticks()//500) %2 == 0 else ""), (WIDTH//2, 350), font_med, center=True)
        draw_text(screen, "Press Enter to save, Esc to skip.", (WIDTH//2, HEIGHT - 80), font_small, center=True)
        pygame.display.flip()
        clock.tick(30)

# --------------------------
# Main loop + menus
# --------------------------

def show_themes_menu(game):
    # Theme unlock thresholds based on best leaderboard score
    thresholds = {
        'DarkBlueGlow': 0,
        'Minimal': 0,
        'Neon': 15,
        'Retro': 25,
        'Cyberpunk': 40,
    }
    # determine player's best score from leaderboard
    best = 0
    if game.leaderboard:
        best = max((r.get('score', 0) for r in game.leaderboard), default=0)

    theme_names = list(THEMES.keys())
    idx = theme_names.index(game.theme_name) if game.theme_name in theme_names else 0
    while True:
        dt = clock.tick(FPS) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    name = theme_names[idx]
                    req = thresholds.get(name, 0)
                    if best >= req:
                        game.theme_name = name
                        game.theme = THEMES[name]
                        game.player.color = game.theme.get('player_color', game.player.color)
                        # persist
                        game.settings['theme'] = name
                        save_settings(game.settings)
                        play_sfx('click')
                    else:
                        play_sfx('hit')
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(theme_names)
                    play_sfx('hover')
                elif e.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(theme_names)
                    play_sfx('hover')
                elif e.key in (pygame.K_ESCAPE,):
                    play_sfx('click')
                    return

        # draw themed menu
        t = pygame.time.get_ticks() / 1000.0
        game.draw_background(screen, t)
        panel_col = game.theme.get('ui_panel', UI_PANEL)
        pygame.draw.rect(screen, panel_col, (WIDTH//2 - 300, 80, 600, 140), border_radius=14)
        draw_text(screen, 'Select Theme', (WIDTH//2, 110), font_large, color=game.theme.get('accent', ACCENT), center=True)
        draw_text(screen, f'Best: {best}  — use Enter to select (locked until threshold)', (WIDTH//2, 150), font_small, color=(200,200,200), center=True)

        y = 260
        for i, name in enumerate(theme_names):
            req = thresholds.get(name, 0)
            locked = best < req
            text = f"{name} {'(locked)' if locked else ''}"
            color = (150,150,150) if locked else WHITE
            rect = (WIDTH//2 - 220, y + i*52, 440, 44)
            button(screen, rect, text, font_med, active=(i == idx))
            draw_text(screen, f"Requires {req} pts" if req>0 else 'Unlocked', (WIDTH//2 + 180, y + i*52 + 12), font_small, color=(180,180,180))

        draw_text(screen, 'Esc to go back', (WIDTH//2, HEIGHT - 60), font_small, center=True)
        pygame.display.flip()


def main():
    game = Game()
    # Ensure leaderboard file exists
    save_leaderboard(game.leaderboard)
    # initial menu
    while True:
        choice = show_start_menu(game)
        if choice == "Play":
            game.start()
            run_game_loop(game)
        elif choice == "Themes":
            show_themes_menu(game)
        elif choice == "Instructions":
            show_instructions(game)
        elif choice == "Leaderboard":
            show_leaderboard(game)
        else:  # Quit
            pygame.quit()
            raise SystemExit()


def run_game_loop(game):
    running = True
    flash_frames = 0
    # stop menu music when entering game
    stop_menu_music()
    # start gameplay music if available
    play_game_music(loop=True)
    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds per frame
        t = pygame.time.get_ticks() / 1000.0
        keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit()
                if e.key == pygame.K_SPACE:
                    # toggle pause
                    if game.playing:
                        game.paused = not game.paused
                if e.key == pygame.K_p:
                    game.paused = not game.paused
                if e.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    # dash in current direction
                    game.player.dash()
                if e.key == pygame.K_q:
                    game.player.dash(direction=-1)
                if e.key == pygame.K_e:
                    game.player.dash(direction=1)

        # update
        game.update(dt, keys)

        # draw
        game.draw(screen, t, flash=(flash_frames>0))
        if not game.playing and flash_frames == 0 and not game.paused:
            # we have just died
            flash_frames = 18
            # let particles update for a moment and then show game over UI
        if flash_frames > 0:
            flash_frames -= 1
            if flash_frames <= 0:
                # prompt for name/save score
                name_entry_prompt(game, game.score)
                # show game over summary
                show_game_over_screen(game)
                return

        pygame.display.flip()

def show_game_over_screen(game):
    # game over summary (press enter to return to menu)
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                return
        bg = game.theme.get('bg_bottom', BG_BOTTOM)
        screen.fill(bg)
        draw_text(screen, "Game Over", (WIDTH//2, 120), font_large, color=RED, center=True)
        draw_text(screen, f"Score: {game.score}", (WIDTH//2, 200), font_med, center=True)
        draw_text(screen, "Leaderboard (Top Scores):", (WIDTH//2, 260), font_med, center=True)
        y = 320
        for i, rec in enumerate(game.leaderboard):
            draw_text(screen, f"{i+1}. {rec['name'][:12]:12s} — {rec['score']:4d}", (WIDTH//2, y), font_med, center=True)
            y += 46
        draw_text(screen, "Press Enter / Space / Esc to return to main menu.", (WIDTH//2, HEIGHT - 80), font_small, center=True)
        pygame.display.flip()
        clock.tick(20)

if __name__ == "__main__":
    print("Starting Avoid The Block...")
    try:
        main()
    except Exception as e:
        import traceback, sys
        traceback.print_exc()
        try:
            pygame.quit()
        except Exception:
            pass
        sys.exit(1)
