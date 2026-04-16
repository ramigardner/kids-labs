#!/usr/bin/env python3
"""
Beat Lab - Educational Tecno Sequencer for Kids
ASPR Gardener · Kids Lab
MIT License · Ramiro
Versión mejorada con Reset, Export All, mejor mezcla y atajos visuales.
"""

import pygame
import numpy as np
import time
import threading
import json
import os
import wave
from datetime import datetime

# ----------------------------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 1280, 680
GRID_COLS = 15
GRID_ROWS = 7
CELL_WIDTH = 48
CELL_HEIGHT = 56
GRID_LEFT = 60
GRID_TOP = 140

SOUND_NAMES = ["KICK", "SNARE", "HI-HAT", "CLAP", "BASS", "TOM", "RIM"]
DEFAULT_BPM = 120

# Paleta Kids Lab
BG_COLOR       = (8, 6, 18)
BG2_COLOR      = (14, 11, 30)
BORDER_COLOR   = (40, 30, 70)
ACCENT         = (0, 229, 180)
ACCENT2        = (180, 100, 255)
TEXT_COLOR     = (210, 200, 240)
TEXT_DIM       = (100, 85, 140)
PANEL_BG       = (12, 9, 22)

TRACK_COLORS = [
    (255,  80,  80), (255, 180,  30), ( 50, 220, 255),
    (180, 100, 255), ( 60, 230, 130), (255, 140,   0), (220,  50, 220)
]
TRACK_COLORS_DIM = [
    ( 50,  15,  15), ( 50,  35,   5), (  5,  40,  55),
    ( 30,  10,  55), (  5,  45,  20), ( 40,  20,   0), ( 40,   0,  40)
]
HIGHLIGHT_COLOR = (255, 255, 255)

# Atajos de teclado (se dibujan en pantalla)
KEY_MAP = [
    ("SPACE", "Play/Stop"), ("R", "Record"), ("M", "Mix"), ("S", "Save"),
    ("L", "Load list"), ("E", "Effects"), ("+", "BPM +5"), ("-", "BPM -5"),
    ("ESC", "Salir"), ("DEL", "Reset Grid")
]

# ----------------------------------------------------------------------
# SÍNTESIS DE SONIDOS (igual que original, pero con ligeras mejoras)
# ----------------------------------------------------------------------
SAMPLE_RATE = 44100

def _make_sound_from_array(wave_int16):
    wave_int16 = np.ascontiguousarray(wave_int16)
    try:
        return pygame.sndarray.make_sound(wave_int16)
    except ValueError:
        stereo = np.column_stack((wave_int16, wave_int16))
        stereo = np.ascontiguousarray(stereo)
        return pygame.sndarray.make_sound(stereo)

def synth_kick():
    duration = 0.2
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = np.linspace(150, 40, len(t))
    wave = np.sin(2 * np.pi * freq * t)
    envelope = np.exp(-5 * t)
    return wave * envelope

def synth_snare():
    duration = 0.15
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.normal(0, 1, len(t))
    envelope = np.exp(-20 * t)
    tone = np.sin(2 * np.pi * 180 * t) * envelope * 0.5
    wave = noise * envelope + tone
    if np.max(np.abs(wave)) > 0:
        wave = wave / np.max(np.abs(wave))
    return wave

def synth_hihat():
    duration = 0.05
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.normal(0, 1, len(t))
    filtered = noise[1:] - 0.8 * noise[:-1]
    filtered = np.append(filtered, 0)
    envelope = np.exp(-80 * t)
    wave = filtered * envelope
    if np.max(np.abs(wave)) > 0:
        wave = wave / np.max(np.abs(wave)) * 0.6
    return wave

def synth_clap():
    duration = 0.1
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.normal(0, 1, len(t))
    envelope = np.exp(-15 * t)
    wave = noise * envelope
    if np.max(np.abs(wave)) > 0:
        wave = wave / np.max(np.abs(wave))
    return wave

def synth_bass():
    duration = 0.3
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = 70
    wave = np.sin(2 * np.pi * freq * t) * 0.5
    saw = 2 * (t * freq - np.floor(0.5 + t * freq))
    wave = wave + saw * 0.3
    envelope = np.exp(-3 * t)
    wave = wave * envelope
    if np.max(np.abs(wave)) > 0:
        wave = wave / np.max(np.abs(wave))
    return wave

def synth_tom():
    duration = 0.15
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = np.linspace(200, 80, len(t))
    wave = np.sin(2 * np.pi * freq * t)
    envelope = np.exp(-10 * t)
    wave = wave * envelope
    if np.max(np.abs(wave)) > 0:
        wave = wave / np.max(np.abs(wave))
    return wave

def synth_rim():
    duration = 0.03
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.normal(0, 1, len(t))
    tone = np.sin(2 * np.pi * 1200 * t) * 0.3
    wave = noise * 0.7 + tone
    envelope = np.exp(-120 * t)
    wave = wave * envelope
    if np.max(np.abs(wave)) > 0:
        wave = wave / np.max(np.abs(wave)) * 0.8
    return wave

def generate_kick():   arr = synth_kick();   arr_int16 = (arr * 32767).astype(np.int16); return _make_sound_from_array(arr_int16)
def generate_snare():  arr = synth_snare();  arr_int16 = (arr * 32767).astype(np.int16); return _make_sound_from_array(arr_int16)
def generate_hihat():  arr = synth_hihat();  arr_int16 = (arr * 32767).astype(np.int16); return _make_sound_from_array(arr_int16)
def generate_clap():   arr = synth_clap();   arr_int16 = (arr * 32767).astype(np.int16); return _make_sound_from_array(arr_int16)
def generate_bass():   arr = synth_bass();   arr_int16 = (arr * 32767).astype(np.int16); return _make_sound_from_array(arr_int16)
def generate_tom():    arr = synth_tom();    arr_int16 = (arr * 32767).astype(np.int16); return _make_sound_from_array(arr_int16)
def generate_rim():    arr = synth_rim();    arr_int16 = (arr * 32767).astype(np.int16); return _make_sound_from_array(arr_int16)

# ----------------------------------------------------------------------
# HELPERS DE DIBUJO
# ----------------------------------------------------------------------
def draw_rounded_rect(surface, color, rect, radius=8, border=0, border_color=None):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
    for cx, cy in [(x+radius, y+radius), (x+w-radius-1, y+radius),
                   (x+radius, y+h-radius-1), (x+w-radius-1, y+h-radius-1)]:
        pygame.draw.circle(surface, color, (cx, cy), radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, (x + radius, y, w - 2*radius, h), border)
        pygame.draw.rect(surface, border_color, (x, y + radius, w, h - 2*radius), border)
        for cx, cy in [(x+radius, y+radius), (x+w-radius-1, y+radius),
                       (x+radius, y+h-radius-1), (x+w-radius-1, y+h-radius-1)]:
            pygame.draw.circle(surface, border_color, (cx, cy), radius, border)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ----------------------------------------------------------------------
# CLASE PRINCIPAL MEJORADA
# ----------------------------------------------------------------------
class BeatLab:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("🎵 Beat Lab · ASPR Kids Lab · Enhanced")
        self.clock = pygame.time.Clock()

        self.font_big   = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_med   = pygame.font.SysFont("Courier New", 16, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 13)
        self.font_tiny  = pygame.font.SysFont("Courier New", 11)

        self.sounds = [
            generate_kick(), generate_snare(), generate_hihat(),
            generate_clap(), generate_bass(), generate_tom(), generate_rim()
        ]

        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]
        self.bpm = DEFAULT_BPM
        self.playing = False
        self.recording = False   # solo efecto visual
        self.current_step = 0
        self.last_step_time = 0
        self.step_interval = 60.0 / self.bpm / 4

        self.track_mute = [False] * GRID_ROWS
        self.track_solo = [False] * GRID_ROWS
        self.row_flash = [0.0] * GRID_ROWS

        self.projects_dir = "beatlab_projects"
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

        self.samples_dir = "beatlab_samples"
        if not os.path.exists(self.samples_dir):
            os.makedirs(self.samples_dir)
        self.sample_files = []
        self.loaded_samples = {}
        self.refresh_sample_list()

        self.running = True
        self.seq_thread = None
        self.status_message = ""
        self.status_timer = 0
        self.project_list = []
        self.selected_project_index = -1
        self.effects_mode = False

        # Botones adicionales (coordenadas se actualizan en cada draw)
        self.reset_btn_rect = None
        self.export_all_btn_rect = None

        self.refresh_project_list()

    # ------------------------------------------------------------------
    # Secuenciador
    # ------------------------------------------------------------------
    def _should_play_track(self, row):
        any_solo = any(self.track_solo)
        if any_solo:
            return self.track_solo[row]
        return not self.track_mute[row]

    def sequencer_loop(self):
        while self.playing and self.running:
            now = time.time()
            if now - self.last_step_time >= self.step_interval:
                for row in range(GRID_ROWS):
                    if self.grid[row][self.current_step] and self._should_play_track(row):
                        self.sounds[row].play()
                        self.row_flash[row] = 1.0
                self.current_step = (self.current_step + 1) % GRID_COLS
                self.last_step_time = now
            time.sleep(0.001)

    def start_sequencer(self):
        if not self.playing:
            self.playing = True
            self.last_step_time = time.time()
            self.current_step = 0
            self.seq_thread = threading.Thread(target=self.sequencer_loop, daemon=True)
            self.seq_thread.start()

    def stop_sequencer(self):
        self.playing = False
        if self.seq_thread and self.seq_thread.is_alive():
            self.seq_thread.join(timeout=0.2)

    # ------------------------------------------------------------------
    # Proyectos (guardado/carga/exportación)
    # ------------------------------------------------------------------
    def save_project(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proyecto_{timestamp}.json"
        path = os.path.join(self.projects_dir, filename)
        data = {"grid": self.grid, "bpm": self.bpm, "name": filename}
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        self.set_status(f"Guardado: {filename}")
        self.refresh_project_list()

    def load_project(self, filename):
        path = os.path.join(self.projects_dir, filename)
        if not os.path.exists(path):
            self.set_status(f"No existe: {filename}")
            return
        with open(path, 'r') as f:
            data = json.load(f)
        self.grid = data.get("grid", self.grid)
        self.bpm = data.get("bpm", self.bpm)
        self.step_interval = 60.0 / self.bpm / 4
        self.set_status(f"Cargado: {filename}")

    def load_project_data(self, filename):
        path = os.path.join(self.projects_dir, filename)
        if not os.path.exists(path):
            return None, None
        with open(path, 'r') as f:
            data = json.load(f)
        return data.get("grid", [[False]*GRID_COLS for _ in range(GRID_ROWS)]), data.get("bpm", DEFAULT_BPM)

    def list_projects(self):
        files = [f for f in os.listdir(self.projects_dir) if f.endswith('.json')]
        files.sort(reverse=True)
        return files

    def refresh_project_list(self):
        self.project_list = self.list_projects()
        self.selected_project_index = -1

    def set_status(self, msg):
        self.status_message = msg
        self.status_timer = 120

    # ------------------------------------------------------------------
    # Samples (efectos)
    # ------------------------------------------------------------------
    def refresh_sample_list(self):
        self.sample_files = [f for f in os.listdir(self.samples_dir) if f.endswith('.wav')]
        self.sample_files.sort()
        for f in self.sample_files:
            if f not in self.loaded_samples:
                try:
                    path = os.path.join(self.samples_dir, f)
                    self.loaded_samples[f] = pygame.mixer.Sound(path)
                except:
                    pass

    def play_sample(self, filename):
        if filename in self.loaded_samples:
            self.loaded_samples[filename].play()
            self.set_status(f"Efecto: {filename}")

    # ------------------------------------------------------------------
    # Mix y Reset (mejorados)
    # ------------------------------------------------------------------
    def mix_pattern(self):
        """Genera un patrón rítmico moderno (como en la versión web)"""
        new_grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]
        # Kick en 0,4,8,12
        for step in [0,4,8,12]:
            if step < GRID_COLS:
                new_grid[0][step] = True
        # Snare + Clap
        for step in [3,7,11]:
            if step < GRID_COLS:
                new_grid[1][step] = True
                if step+1 < GRID_COLS:
                    new_grid[3][step+1] = True
        # Hi-Hat cada 2 pasos
        for step in range(0, GRID_COLS, 2):
            new_grid[2][step] = True
        # Tom en 2,6,10,14
        for step in [2,6,10,14]:
            if step < GRID_COLS:
                new_grid[5][step] = True
        # Rim en 5,9,13
        for step in [5,9,13]:
            if step < GRID_COLS:
                new_grid[6][step] = True
        # Bass aleatorio en los pares
        for step in range(0, GRID_COLS, 2):
            new_grid[4][step] = np.random.choice([True, False])
        self.grid = new_grid
        self.set_status("🎛 Mix generado (15 pasos)")

    def reset_grid(self):
        """Limpia toda la grilla (todas las celdas a False)."""
        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]
        self.set_status("🧹 Grilla completamente limpiada")

    # ------------------------------------------------------------------
    # EXPORTACIÓN A WAV (mejorada y con exportación masiva)
    # ------------------------------------------------------------------
    def export_pattern_to_wav(self, grid, bpm, filename, num_loops=4):
        step_duration = 60.0 / bpm / 4
        total_steps = GRID_COLS * num_loops
        total_samples = int(total_steps * step_duration * SAMPLE_RATE)
        mix_buffer = np.zeros(total_samples, dtype=np.float32)

        synth_funcs = [synth_kick, synth_snare, synth_hihat, synth_clap,
                       synth_bass, synth_tom, synth_rim]
        row_audio = [func() for func in synth_funcs]

        for loop in range(num_loops):
            for step in range(GRID_COLS):
                step_global = loop * GRID_COLS + step
                start_sample = int(step_global * step_duration * SAMPLE_RATE)
                end_sample = start_sample + int(step_duration * SAMPLE_RATE)
                if end_sample > total_samples:
                    end_sample = total_samples
                for row in range(GRID_ROWS):
                    if grid[row][step]:
                        audio = row_audio[row]
                        audio_len = min(len(audio), end_sample - start_sample)
                        mix_buffer[start_sample:start_sample+audio_len] += audio[:audio_len]

        max_val = np.max(np.abs(mix_buffer))
        if max_val > 0:
            mix_buffer = mix_buffer / max_val * 0.95

        audio_int16 = (mix_buffer * 32767).astype(np.int16)

        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        self.set_status(f"Exportado: {os.path.basename(filename)}")

    def export_current_pattern(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.projects_dir, f"export_{timestamp}.wav")
        self.export_pattern_to_wav(self.grid, self.bpm, filename, num_loops=4)

    def export_all_projects(self):
        if not self.project_list:
            self.set_status("No hay proyectos para exportar")
            return
        count = 0
        for proj in self.project_list:
            grid, bpm = self.load_project_data(proj)
            if grid is None:
                continue
            out_name = proj.replace('.json', '.wav')
            out_path = os.path.join(self.projects_dir, out_name)
            self.export_pattern_to_wav(grid, bpm, out_path, num_loops=4)
            count += 1
        self.set_status(f"Exportados {count} proyectos a WAV")

    # ------------------------------------------------------------------
    # Dibujo (mejorado con más botones y atajos visuales)
    # ------------------------------------------------------------------
    def draw_header(self):
        title = self.font_big.render("BEAT LAB", True, ACCENT)
        self.screen.blit(title, (GRID_LEFT, 18))
        sub = self.font_tiny.render("ASPR GARDENER · KIDS LAB · ENHANCED", True, TEXT_DIM)
        self.screen.blit(sub, (GRID_LEFT, 44))
        if self.recording:
            badge_color = (200, 60, 60)
            label = "● REC"
            label_color = (255, 150, 150)
        elif self.playing:
            badge_color = (0, 180, 90)
            label = "▶  PLAYING"
            label_color = (0, 255, 140)
        else:
            badge_color = (50, 30, 70)
            label = "⏸  STOPPED"
            label_color = TEXT_DIM
        draw_rounded_rect(self.screen, badge_color, (GRID_LEFT, 68, 130, 26), radius=6)
        surf = self.font_small.render(label, True, label_color)
        self.screen.blit(surf, (GRID_LEFT + 8, 75))
        bpm_label = self.font_small.render(f"BPM: {self.bpm}", True, ACCENT2)
        self.screen.blit(bpm_label, (GRID_LEFT + 150, 74))
        if self.status_timer > 0:
            status_surf = self.font_tiny.render(self.status_message, True, ACCENT)
            self.screen.blit(status_surf, (GRID_LEFT + 280, 76))
            self.status_timer -= 1
        pygame.draw.line(self.screen, BORDER_COLOR,
                         (GRID_LEFT - 10, 110), (GRID_LEFT + GRID_COLS * CELL_WIDTH + 10, 110), 1)

    def draw_grid(self):
        for col in range(GRID_COLS):
            x = GRID_LEFT + col * CELL_WIDTH + CELL_WIDTH // 2 - 6
            num = self.font_tiny.render(str(col + 1), True,
                                        ACCENT if (self.playing and col == self.current_step) else TEXT_DIM)
            self.screen.blit(num, (x, GRID_TOP - 22))
        for row in range(GRID_ROWS):
            color_on  = TRACK_COLORS[row]
            color_off = TRACK_COLORS_DIM[row]
            flash_t   = self.row_flash[row]
            lx = GRID_LEFT - 50
            ly = GRID_TOP + row * CELL_HEIGHT + CELL_HEIGHT // 2 - 8
            track_label = self.font_small.render(SOUND_NAMES[row], True, color_on)
            self.screen.blit(track_label, (lx, ly))
            if flash_t > 0:
                bright = self.font_small.render(SOUND_NAMES[row], True,
                                                lerp_color(color_on, (255, 255, 255), flash_t * 0.6))
                self.screen.blit(bright, (lx, ly))
            for col in range(GRID_COLS):
                x = GRID_LEFT + col * CELL_WIDTH
                y = GRID_TOP + row * CELL_HEIGHT
                rect = (x + 2, y + 2, CELL_WIDTH - 6, CELL_HEIGHT - 6)
                if self.grid[row][col]:
                    c = lerp_color(color_on, (255, 255, 255),
                                   0.4 if (self.playing and col == self.current_step) else 0.0)
                    draw_rounded_rect(self.screen, c, rect, radius=6)
                    cx = x + CELL_WIDTH // 2
                    cy = y + CELL_HEIGHT // 2
                    pygame.draw.circle(self.screen, (255, 255, 255, 80), (cx, cy), 3)
                else:
                    draw_rounded_rect(self.screen, color_off, rect, radius=6)
                    draw_rounded_rect(self.screen, color_off, rect, radius=6,
                                      border=1, border_color=lerp_color(color_off, color_on, 0.3))
                if self.playing and col == self.current_step:
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR,
                                     (x + 1, y + 1, CELL_WIDTH - 4, CELL_HEIGHT - 4), 2)

    def draw_right_panel(self):
        panel_x = GRID_LEFT + GRID_COLS * CELL_WIDTH + 20
        panel_w = WIDTH - panel_x - 20
        panel_rect = pygame.Rect(panel_x, GRID_TOP - 20, panel_w, HEIGHT - GRID_TOP - 40)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, panel_rect, 2)
        title = self.font_med.render("MONITOR", True, ACCENT2)
        self.screen.blit(title, (panel_x + 10, GRID_TOP - 10))

        y = GRID_TOP + 10
        header_y = y
        self.screen.blit(self.font_tiny.render("TRACK", True, TEXT_DIM), (panel_x + 10, header_y))
        self.screen.blit(self.font_tiny.render("M", True, TEXT_DIM), (panel_x + 90, header_y))
        self.screen.blit(self.font_tiny.render("S", True, TEXT_DIM), (panel_x + 110, header_y))
        self.screen.blit(self.font_tiny.render("▶", True, TEXT_DIM), (panel_x + 135, header_y))
        y += 16
        self.track_control_rects = []
        for row in range(GRID_ROWS):
            color = TRACK_COLORS[row]
            name = SOUND_NAMES[row][:4]
            name_surf = self.font_tiny.render(name, True, color)
            self.screen.blit(name_surf, (panel_x + 10, y + 4))
            mute_rect = pygame.Rect(panel_x + 85, y, 18, 18)
            mute_color = (200, 60, 60) if self.track_mute[row] else (60, 60, 100)
            draw_rounded_rect(self.screen, mute_color, mute_rect, radius=3)
            self.screen.blit(self.font_tiny.render("M", True, (255,255,255)), (panel_x + 90, y+2))
            solo_rect = pygame.Rect(panel_x + 107, y, 18, 18)
            solo_color = (200, 200, 60) if self.track_solo[row] else (60, 60, 100)
            draw_rounded_rect(self.screen, solo_color, solo_rect, radius=3)
            self.screen.blit(self.font_tiny.render("S", True, (0,0,0) if self.track_solo[row] else (255,255,255)), (panel_x + 112, y+2))
            trig_rect = pygame.Rect(panel_x + 130, y, 22, 18)
            draw_rounded_rect(self.screen, (80, 80, 120), trig_rect, radius=3)
            self.screen.blit(self.font_tiny.render("▶", True, ACCENT), (panel_x + 136, y+2))
            self.track_control_rects.append((row, mute_rect, solo_rect, trig_rect))
            y += 22

        y += 5
        pygame.draw.line(self.screen, BORDER_COLOR, (panel_x + 5, y), (panel_x + panel_w - 5, y), 1)
        y += 10

        self.screen.blit(self.font_med.render("PROYECTOS", True, ACCENT), (panel_x + 10, y))
        y += 22
        if not self.project_list:
            self.refresh_project_list()
        self.project_item_rects = []
        list_h = 120
        list_rect = pygame.Rect(panel_x + 5, y, panel_w - 10, list_h)
        pygame.draw.rect(self.screen, (20, 15, 30), list_rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, list_rect, 1)
        item_h = 20
        for i, proj in enumerate(self.project_list[:6]):
            item_y = y + 2 + i * item_h
            if i == self.selected_project_index:
                pygame.draw.rect(self.screen, (60, 50, 90), (panel_x + 7, item_y, panel_w - 14, item_h))
            proj_surf = self.font_tiny.render(proj.replace(".json", ""), True, TEXT_COLOR)
            self.screen.blit(proj_surf, (panel_x + 10, item_y + 3))
            rect = pygame.Rect(panel_x + 7, item_y, panel_w - 14, item_h)
            self.project_item_rects.append((i, proj, rect))
        y += list_h + 5

        btn_w = 65
        btn_h = 24
        self.load_proj_btn = pygame.Rect(panel_x + 10, y, btn_w, btn_h)
        draw_rounded_rect(self.screen, (40, 80, 120), self.load_proj_btn, radius=5)
        self.screen.blit(self.font_tiny.render("Cargar", True, (220,220,250)), (panel_x + 16, y+5))
        self.refresh_btn = pygame.Rect(panel_x + 85, y, btn_w, btn_h)
        draw_rounded_rect(self.screen, (60, 60, 90), self.refresh_btn, radius=5)
        self.screen.blit(self.font_tiny.render("↻", True, TEXT_DIM), (panel_x + 105, y+5))
        self.del_proj_btn = pygame.Rect(panel_x + 160, y, btn_w, btn_h)
        draw_rounded_rect(self.screen, (120, 50, 50), self.del_proj_btn, radius=5)
        self.screen.blit(self.font_tiny.render("Borrar", True, (220,220,250)), (panel_x + 168, y+5))
        self.export_all_btn = pygame.Rect(panel_x + 235, y, btn_w+10, btn_h)
        draw_rounded_rect(self.screen, (70, 130, 70), self.export_all_btn, radius=5)
        self.screen.blit(self.font_tiny.render("📁 EXP ALL", True, (255,255,200)), (panel_x + 240, y+5))
        self.export_all_btn_rect = self.export_all_btn

        y += btn_h + 15
        pygame.draw.line(self.screen, BORDER_COLOR, (panel_x + 5, y), (panel_x + panel_w - 5, y), 1)
        y += 8
        self.screen.blit(self.font_med.render("EFECTOS", True, ACCENT if self.effects_mode else ACCENT2), (panel_x + 10, y))
        y += 22
        self.sample_rects = []
        sample_h = 24
        samples_visible = min(len(self.sample_files), 4)
        for i in range(samples_visible):
            fname = self.sample_files[i]
            item_y = y + i * sample_h
            rect = pygame.Rect(panel_x + 5, item_y, panel_w - 10, sample_h-2)
            color = (60, 50, 90) if self.effects_mode else (30, 25, 50)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, rect, 1)
            name = fname.replace(".wav", "")[:15]
            self.screen.blit(self.font_tiny.render(name, True, TEXT_COLOR), (panel_x + 10, item_y+4))
            self.sample_rects.append((fname, rect))
        if not self.sample_files:
            self.screen.blit(self.font_tiny.render("(pon .wav en samples/)", True, TEXT_DIM), (panel_x + 10, y+10))

    def draw_control_buttons(self):
        btn_y = GRID_TOP + GRID_ROWS * CELL_HEIGHT + 30
        btn_x_start = GRID_LEFT
        btn_w, btn_h = 85, 36
        gap = 10
        buttons = [
            ("▶ PLAY", self.playing, (0, 200, 100) if self.playing else (40, 40, 70)),
            ("⏹ STOP", not self.playing, (200, 60, 60) if not self.playing else (40, 40, 70)),
            ("● REC", self.recording, (220, 30, 30) if self.recording else (40, 40, 70)),
            ("🔄 MIX", False, (70, 50, 140)),
            ("💾 SAVE", False, (50, 100, 150)),
            ("✨ EFX", self.effects_mode, (120, 60, 180) if self.effects_mode else (40, 40, 70)),
            ("📀 WAV", False, (30, 100, 130)),
            ("🗑 RESET", False, (120, 40, 40))
        ]
        self.button_rects = []
        for i, (text, active, base_color) in enumerate(buttons):
            bx = btn_x_start + i * (btn_w + gap)
            by = btn_y
            color = base_color if not active else lerp_color(base_color, (255, 255, 255), 0.3)
            draw_rounded_rect(self.screen, color, (bx, by, btn_w, btn_h), radius=6)
            draw_rounded_rect(self.screen, color, (bx, by, btn_w, btn_h), radius=6,
                              border=1, border_color=lerp_color(color, (255, 255, 255), 0.5))
            label = self.font_small.render(text, True, (220, 220, 250))
            lw = label.get_width()
            self.screen.blit(label, (bx + (btn_w - lw)//2, by + 10))
            self.button_rects.append(pygame.Rect(bx, by, btn_w, btn_h))

    def draw_keyboard(self):
        kb_y = GRID_TOP + GRID_ROWS * CELL_HEIGHT + 90
        kb_x = GRID_LEFT
        pygame.draw.line(self.screen, BORDER_COLOR, (kb_x - 10, kb_y - 10), (kb_x + 950, kb_y - 10), 1)
        label = self.font_tiny.render("KEYBOARD SHORTCUTS", True, TEXT_DIM)
        self.screen.blit(label, (kb_x, kb_y - 7))
        kb_y += 14
        key_w, key_h = 65, 38
        gap = 8
        for i, (key, action) in enumerate(KEY_MAP):
            kx = kb_x + i * (key_w + gap)
            ky = kb_y
            body_color = (28, 20, 50)
            shadow_color = (10, 6, 22)
            draw_rounded_rect(self.screen, shadow_color, (kx + 2, ky + 4, key_w, key_h), radius=5)
            draw_rounded_rect(self.screen, body_color, (kx, ky, key_w, key_h), radius=5)
            pygame.draw.line(self.screen, (60, 45, 100), (kx + 5, ky), (kx + key_w - 5, ky), 1)
            pygame.draw.line(self.screen, (60, 45, 100), (kx, ky + 5), (kx, ky + key_h - 5), 1)
            k_surf = self.font_med.render(key, True, ACCENT)
            kw = k_surf.get_width()
            self.screen.blit(k_surf, (kx + (key_w - kw) // 2, ky + 4))
            a_surf = self.font_tiny.render(action, True, TEXT_DIM)
            aw = a_surf.get_width()
            self.screen.blit(a_surf, (kx + (key_w - aw) // 2, ky + 24))

    def draw_footer(self):
        fy = HEIGHT - 22
        cr = self.font_tiny.render("ASPR GARDENER · Kids Lab · MIT License · Enhanced Version", True, TEXT_DIM)
        self.screen.blit(cr, (GRID_LEFT, fy))

    # ------------------------------------------------------------------
    # Actualización y eventos
    # ------------------------------------------------------------------
    def update_animations(self, dt):
        for i in range(GRID_ROWS):
            if self.row_flash[i] > 0:
                self.row_flash[i] = max(0.0, self.row_flash[i] - dt * 6.0)

    def handle_click(self, pos):
        x, y = pos
        grid_right = GRID_LEFT + GRID_COLS * CELL_WIDTH
        grid_bottom = GRID_TOP + GRID_ROWS * CELL_HEIGHT
        if GRID_LEFT <= x < grid_right and GRID_TOP <= y < grid_bottom:
            col = (x - GRID_LEFT) // CELL_WIDTH
            row = (y - GRID_TOP) // CELL_HEIGHT
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                self.grid[row][col] = not self.grid[row][col]
                return

        if hasattr(self, 'button_rects'):
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(x, y):
                    if i == 0:   # Play
                        self.start_sequencer()
                    elif i == 1: # Stop
                        self.stop_sequencer()
                    elif i == 2: # Record
                        self.recording = not self.recording
                        self.set_status("REC " + ("ON" if self.recording else "OFF"))
                    elif i == 3: # Mix
                        self.mix_pattern()
                    elif i == 4: # Save
                        self.save_project()
                    elif i == 5: # Effects
                        self.effects_mode = not self.effects_mode
                        self.set_status("Modo Efectos " + ("ACTIVADO" if self.effects_mode else "DESACTIVADO"))
                    elif i == 6: # Export WAV
                        self.export_current_pattern()
                    elif i == 7: # Reset
                        self.reset_grid()
                    return

        if hasattr(self, 'track_control_rects'):
            for row, mute_rect, solo_rect, trig_rect in self.track_control_rects:
                if mute_rect.collidepoint(x, y):
                    self.track_mute[row] = not self.track_mute[row]
                    if self.track_mute[row]:
                        self.track_solo[row] = False
                    return
                elif solo_rect.collidepoint(x, y):
                    self.track_solo[row] = not self.track_solo[row]
                    if self.track_solo[row]:
                        self.track_mute[row] = False
                    return
                elif trig_rect.collidepoint(x, y):
                    self.sounds[row].play()
                    self.row_flash[row] = 1.0
                    return

        if hasattr(self, 'project_item_rects'):
            for idx, proj_name, rect in self.project_item_rects:
                if rect.collidepoint(x, y):
                    self.selected_project_index = idx
                    return

        if hasattr(self, 'load_proj_btn') and self.load_proj_btn.collidepoint(x, y):
            if self.selected_project_index >= 0 and self.selected_project_index < len(self.project_list):
                self.load_project(self.project_list[self.selected_project_index])
            return
        if hasattr(self, 'refresh_btn') and self.refresh_btn.collidepoint(x, y):
            self.refresh_project_list()
            self.selected_project_index = -1
            return
        if hasattr(self, 'del_proj_btn') and self.del_proj_btn.collidepoint(x, y):
            if self.selected_project_index >= 0 and self.selected_project_index < len(self.project_list):
                filename = self.project_list[self.selected_project_index]
                path = os.path.join(self.projects_dir, filename)
                if os.path.exists(path):
                    os.remove(path)
                    self.set_status(f"Borrado: {filename}")
                    self.refresh_project_list()
                    self.selected_project_index = -1
            return
        if hasattr(self, 'export_all_btn_rect') and self.export_all_btn_rect and self.export_all_btn_rect.collidepoint(x, y):
            self.export_all_projects()
            return

        if hasattr(self, 'sample_rects'):
            for fname, rect in self.sample_rects:
                if rect.collidepoint(x, y):
                    self.play_sample(fname)
                    return

    def run(self):
        prev_time = time.time()
        while self.running:
            now = time.time()
            dt = now - prev_time
            prev_time = now
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        if self.playing:
                            self.stop_sequencer()
                        else:
                            self.start_sequencer()
                    elif event.key == pygame.K_r:
                        self.recording = not self.recording
                        self.set_status("REC " + ("ON" if self.recording else "OFF"))
                    elif event.key == pygame.K_m:
                        self.mix_pattern()
                    elif event.key == pygame.K_s:
                        self.save_project()
                    elif event.key == pygame.K_l:
                        self.refresh_project_list()
                    elif event.key == pygame.K_e:
                        self.effects_mode = not self.effects_mode
                        self.set_status("Modo Efectos " + ("ON" if self.effects_mode else "OFF"))
                    elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        self.bpm = min(200, self.bpm + 5)
                        self.step_interval = 60.0 / self.bpm / 4
                        self.set_status(f"BPM: {self.bpm}")
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.bpm = max(60, self.bpm - 5)
                        self.step_interval = 60.0 / self.bpm / 4
                        self.set_status(f"BPM: {self.bpm}")
                    elif event.key == pygame.K_DELETE:
                        self.reset_grid()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            self.update_animations(dt)
            self.screen.fill(BG_COLOR)
            for gx in range(0, WIDTH, 40):
                for gy in range(0, HEIGHT, 40):
                    pygame.draw.circle(self.screen, BORDER_COLOR, (gx, gy), 1)

            self.draw_header()
            self.draw_grid()
            self.draw_control_buttons()
            self.draw_right_panel()
            self.draw_keyboard()
            self.draw_footer()
            pygame.display.flip()
            self.clock.tick(60)

        self.stop_sequencer()
        pygame.quit()

if __name__ == "__main__":
    lab = BeatLab()
    lab.run()
