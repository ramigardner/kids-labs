#!/usr/bin/env python3
"""
Beat Lab - Educational Tecno Sequencer for Kids
Part of ASPR Gardener · Kids Lab
MIT License · Ramiro
"""

import pygame
import numpy as np
import time
import threading
import json
import os
from datetime import datetime

# ----------------------------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 1000, 680           # Ampliado para 12 columnas
GRID_COLS = 12                      # 8 + 4 casilleros
GRID_ROWS = 7                       # 5 + 2 sonidos nuevos
CELL_SIZE = 64
GRID_LEFT = (WIDTH - (GRID_COLS * CELL_SIZE)) // 2
GRID_TOP = 160

SOUND_NAMES = ["KICK", "SNARE", "HI-HAT", "CLAP", "BASS", "TOM", "RIM"]
DEFAULT_BPM = 120

# ── Paleta Kids Lab ──────────────────────────────────────────────────
BG_COLOR       = (8, 6, 18)
BG2_COLOR      = (14, 11, 30)
BORDER_COLOR   = (40, 30, 70)
ACCENT         = (0, 229, 180)
ACCENT2        = (180, 100, 255)
TEXT_COLOR     = (210, 200, 240)
TEXT_DIM       = (100, 85, 140)

# Colores por instrumento (Kids Lab vivid)
TRACK_COLORS = [
    (255,  80,  80),   # KICK
    (255, 180,  30),   # SNARE
    ( 50, 220, 255),   # HI-HAT
    (180, 100, 255),   # CLAP
    ( 60, 230, 130),   # BASS
    (255, 140,   0),   # TOM   → naranja fuerte
    (220,  50, 220),   # RIM   → magenta
]

TRACK_COLORS_DIM = [
    ( 50,  15,  15),
    ( 50,  35,   5),
    (  5,  40,  55),
    ( 30,  10,  55),
    (  5,  45,  20),
    ( 40,  20,   0),
    ( 40,   0,  40),
]

HIGHLIGHT_COLOR = (255, 255, 255)

# Teclas del teclado que se muestran
KEY_MAP = [
    ("SPACE", "Play/Stop"),
    ("R",     "Record"),
    ("M",     "Mix"),
    ("S",     "Save"),
    ("L",     "Load"),
    ("+",     "BPM +5"),
    ("-",     "BPM -5"),
    ("ESC",   "Salir"),
]

# ----------------------------------------------------------------------
# SÍNTESIS DE SONIDOS
# ----------------------------------------------------------------------
SAMPLE_RATE = 44100

def _ensure_sound(wave):
    wave = np.ascontiguousarray(wave.astype(np.int16))
    try:
        return pygame.sndarray.make_sound(wave)
    except ValueError:
        stereo = np.column_stack((wave, wave))
        stereo = np.ascontiguousarray(stereo)
        return pygame.sndarray.make_sound(stereo)

def generate_kick():
    duration = 0.2
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = np.linspace(150, 40, len(t))
    wave = np.sin(2 * np.pi * freq * t)
    envelope = np.exp(-5 * t)
    wave = wave * envelope * 32767
    return _ensure_sound(wave)

def generate_snare():
    duration = 0.15
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.normal(0, 1, len(t))
    envelope = np.exp(-20 * t)
    tone = np.sin(2 * np.pi * 180 * t) * envelope * 0.5
    wave = noise * envelope + tone
    wave = wave / np.max(np.abs(wave)) * 32767
    return _ensure_sound(wave)

def generate_hihat():
    duration = 0.05
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.normal(0, 1, len(t))
    filtered = noise[1:] - 0.8 * noise[:-1]
    filtered = np.append(filtered, 0)
    envelope = np.exp(-80 * t)
    wave = filtered * envelope
    wave = wave / np.max(np.abs(wave)) * 20000
    return _ensure_sound(wave)

def generate_clap():
    duration = 0.1
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.normal(0, 1, len(t))
    envelope = np.exp(-15 * t)
    wave = noise * envelope
    wave = wave / np.max(np.abs(wave)) * 32767
    return _ensure_sound(wave)

def generate_bass():
    duration = 0.3
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = 70
    wave = np.sin(2 * np.pi * freq * t) * 0.5
    saw = 2 * (t * freq - np.floor(0.5 + t * freq))
    wave = wave + saw * 0.3
    envelope = np.exp(-3 * t)
    wave = wave * envelope
    wave = wave / np.max(np.abs(wave)) * 32767
    return _ensure_sound(wave)

def generate_tom():
    """Tom de sintetizador estilo 808"""
    duration = 0.15
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = np.linspace(200, 80, len(t))
    wave = np.sin(2 * np.pi * freq * t)
    envelope = np.exp(-10 * t)
    wave = wave * envelope * 25000
    return _ensure_sound(wave)

def generate_rim():
    """Rimshot / clic percusivo"""
    duration = 0.03
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    noise = np.random.normal(0, 1, len(t))
    tone = np.sin(2 * np.pi * 1200 * t) * 0.3
    wave = noise * 0.7 + tone
    envelope = np.exp(-120 * t)
    wave = wave * envelope * 20000
    return _ensure_sound(wave)

# ----------------------------------------------------------------------
# HELPERS DE DIBUJO
# ----------------------------------------------------------------------
def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
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
# CLASE PRINCIPAL
# ----------------------------------------------------------------------
class BeatLab:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("🎵 Beat Lab · ASPR Kids Lab")
        self.clock = pygame.time.Clock()

        # Fuentes
        self.font_big   = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_med   = pygame.font.SysFont("Courier New", 16, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 13)
        self.font_tiny  = pygame.font.SysFont("Courier New", 11)

        # Sonidos
        self.sounds = [
            generate_kick(),
            generate_snare(),
            generate_hihat(),
            generate_clap(),
            generate_bass(),
            generate_tom(),
            generate_rim()
        ]

        # Estado de la grilla
        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]

        # Secuenciador
        self.bpm = DEFAULT_BPM
        self.playing = False
        self.recording = False          # Modo grabación (no usado por ahora)
        self.current_step = 0
        self.last_step_time = 0
        self.step_interval = 60.0 / self.bpm / 4

        # Animaciones
        self.row_flash = [0.0] * GRID_ROWS

        # Armario: directorio para proyectos
        self.projects_dir = "beatlab_projects"
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

        self.running = True
        self.seq_thread = None

        # Mensaje temporal en pantalla
        self.status_message = ""
        self.status_timer = 0

    # ------------------------------------------------------------------
    # Secuenciador
    # ------------------------------------------------------------------
    def sequencer_loop(self):
        while self.playing and self.running:
            now = time.time()
            if now - self.last_step_time >= self.step_interval:
                for row in range(GRID_ROWS):
                    if self.grid[row][self.current_step]:
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
    # Armario: guardar / cargar proyectos
    # ------------------------------------------------------------------
    def save_project(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proyecto_{timestamp}.json"
        path = os.path.join(self.projects_dir, filename)
        data = {
            "grid": self.grid,
            "bpm": self.bpm,
            "name": filename
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        self.set_status(f"Guardado: {filename}")

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

    def list_projects(self):
        """Devuelve lista de archivos .json en el armario"""
        files = [f for f in os.listdir(self.projects_dir) if f.endswith('.json')]
        files.sort(reverse=True)
        return files

    def set_status(self, msg):
        self.status_message = msg
        self.status_timer = 120  # frames ≈ 2 segundos a 60 fps

    # ------------------------------------------------------------------
    # Mix: genera un patrón aleatorio sencillo (tecno)
    # ------------------------------------------------------------------
    def mix_pattern(self):
        """Crea un patrón rítmico básico de techno en la grilla actual"""
        import random
        # Limpiar grilla
        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]

        # Kick en tiempos 1,5,9 (cuatro en el suelo simplificado)
        kick_row = 0
        for step in [0, 4, 8]:
            if step < GRID_COLS:
                self.grid[kick_row][step] = True

        # Snare/clap en 4 y 10
        snare_row = 1
        clap_row = 3
        for step in [3, 9]:
            if step < GRID_COLS:
                self.grid[snare_row][step] = True
                if step+1 < GRID_COLS:
                    self.grid[clap_row][step+1] = True

        # Hi-hat en octavas
        hh_row = 2
        for step in range(0, GRID_COLS, 2):
            self.grid[hh_row][step] = True

        # Tom y rim para variación
        tom_row = 5
        rim_row = 6
        for step in [2, 6, 10]:
            if step < GRID_COLS:
                self.grid[tom_row][step] = True
        for step in [5, 11]:
            if step < GRID_COLS:
                self.grid[rim_row][step] = True

        # Bass simple
        bass_row = 4
        for step in [0, 2, 4, 6, 8, 10]:
            if step < GRID_COLS:
                self.grid[bass_row][step] = random.choice([True, False])

        self.set_status("Mix generado")

    # ------------------------------------------------------------------
    # Dibujo: header
    # ------------------------------------------------------------------
    def draw_header(self):
        title = self.font_big.render("BEAT LAB", True, ACCENT)
        self.screen.blit(title, (GRID_LEFT, 18))

        sub = self.font_tiny.render("ASPR GARDENER · KIDS LAB", True, TEXT_DIM)
        self.screen.blit(sub, (GRID_LEFT, 44))

        # Estado play/stop/record
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

        # Mensaje de estado
        if self.status_timer > 0:
            status_surf = self.font_tiny.render(self.status_message, True, ACCENT)
            self.screen.blit(status_surf, (GRID_LEFT + 280, 76))
            self.status_timer -= 1

        pygame.draw.line(self.screen, BORDER_COLOR,
                         (GRID_LEFT - 80, 110), (GRID_LEFT + GRID_COLS * CELL_SIZE + 10, 110), 1)

    # ------------------------------------------------------------------
    # Dibujo: grilla
    # ------------------------------------------------------------------
    def draw_grid(self):
        for col in range(GRID_COLS):
            x = GRID_LEFT + col * CELL_SIZE + CELL_SIZE // 2 - 8
            num = self.font_tiny.render(str(col + 1), True,
                                        ACCENT if (self.playing and col == self.current_step) else TEXT_DIM)
            self.screen.blit(num, (x, GRID_TOP - 22))

        for row in range(GRID_ROWS):
            color_on  = TRACK_COLORS[row]
            color_off = TRACK_COLORS_DIM[row]
            flash_t   = self.row_flash[row]

            lx = GRID_LEFT - 78
            ly = GRID_TOP + row * CELL_SIZE + CELL_SIZE // 2 - 8
            track_label = self.font_small.render(SOUND_NAMES[row], True, color_on)
            self.screen.blit(track_label, (lx, ly))

            if flash_t > 0:
                bright = self.font_small.render(SOUND_NAMES[row], True,
                                                lerp_color(color_on, (255, 255, 255), flash_t * 0.6))
                self.screen.blit(bright, (lx, ly))

            for col in range(GRID_COLS):
                x = GRID_LEFT + col * CELL_SIZE
                y = GRID_TOP + row * CELL_SIZE
                rect = (x + 3, y + 3, CELL_SIZE - 8, CELL_SIZE - 8)

                if self.grid[row][col]:
                    c = lerp_color(color_on, (255, 255, 255),
                                   0.4 if (self.playing and col == self.current_step) else 0.0)
                    draw_rounded_rect(self.screen, c, rect, radius=8)
                    cx = x + CELL_SIZE // 2
                    cy = y + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, (255, 255, 255, 80), (cx, cy), 4)
                else:
                    draw_rounded_rect(self.screen, color_off, rect, radius=8)
                    draw_rounded_rect(self.screen, color_off, rect, radius=8,
                                      border=1, border_color=lerp_color(color_off, color_on, 0.3))

                if self.playing and col == self.current_step:
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR,
                                     (x + 2, y + 2, CELL_SIZE - 6, CELL_SIZE - 6), 2)

    # ------------------------------------------------------------------
    # Dibujo: botones de control (Play, Stop, Record, Mix, Armario)
    # ------------------------------------------------------------------
    def draw_control_buttons(self):
        btn_y = GRID_TOP + GRID_ROWS * CELL_SIZE + 40
        btn_x_start = GRID_LEFT - 20
        btn_w, btn_h = 100, 40
        gap = 15

        buttons = [
            ("▶ PLAY", self.playing, (0, 200, 100) if self.playing else (40, 40, 70)),
            ("⏹ STOP", not self.playing, (200, 60, 60) if not self.playing else (40, 40, 70)),
            ("● REC", self.recording, (220, 30, 30) if self.recording else (40, 40, 70)),
            ("🔄 MIX", False, (70, 50, 140)),
            ("💾 SAVE", False, (50, 100, 150)),
            ("📂 LOAD", False, (100, 70, 170)),
        ]

        for i, (text, active, base_color) in enumerate(buttons):
            bx = btn_x_start + i * (btn_w + gap)
            by = btn_y

            # Color según estado activo o hover (hover simplificado no implementado)
            color = base_color if not active else lerp_color(base_color, (255, 255, 255), 0.3)
            draw_rounded_rect(self.screen, color, (bx, by, btn_w, btn_h), radius=8)
            # Borde
            draw_rounded_rect(self.screen, color, (bx, by, btn_w, btn_h), radius=8,
                              border=1, border_color=lerp_color(color, (255, 255, 255), 0.5))

            label = self.font_small.render(text, True, (220, 220, 250))
            lw = label.get_width()
            self.screen.blit(label, (bx + (btn_w - lw)//2, by + 12))

        # Almacenar rects para detección de clicks
        self.button_rects = []
        for i, _ in enumerate(buttons):
            bx = btn_x_start + i * (btn_w + gap)
            self.button_rects.append(pygame.Rect(bx, btn_y, btn_w, btn_h))

    # ------------------------------------------------------------------
    # Dibujo: teclado retro
    # ------------------------------------------------------------------
    def draw_keyboard(self):
        kb_y = GRID_TOP + GRID_ROWS * CELL_SIZE + 100
        kb_x = GRID_LEFT - 80
        pygame.draw.line(self.screen, BORDER_COLOR, (kb_x, kb_y - 10), (kb_x + 700, kb_y - 10), 1)

        label = self.font_tiny.render("KEYBOARD SHORTCUTS", True, TEXT_DIM)
        self.screen.blit(label, (kb_x, kb_y - 7))
        kb_y += 14

        key_w, key_h = 70, 40
        gap = 8

        for i, (key, action) in enumerate(KEY_MAP):
            kx = kb_x + i * (key_w + gap)
            ky = kb_y

            body_color = (28, 20, 50)
            shadow_color = (10, 6, 22)
            draw_rounded_rect(self.screen, shadow_color, (kx + 2, ky + 4, key_w, key_h), radius=6)
            draw_rounded_rect(self.screen, body_color, (kx, ky, key_w, key_h), radius=6)
            pygame.draw.line(self.screen, (60, 45, 100), (kx + 5, ky), (kx + key_w - 5, ky), 1)
            pygame.draw.line(self.screen, (60, 45, 100), (kx, ky + 5), (kx, ky + key_h - 5), 1)

            k_surf = self.font_med.render(key, True, ACCENT)
            kw = k_surf.get_width()
            self.screen.blit(k_surf, (kx + (key_w - kw) // 2, ky + 5))

            a_surf = self.font_tiny.render(action, True, TEXT_DIM)
            aw = a_surf.get_width()
            self.screen.blit(a_surf, (kx + (key_w - aw) // 2, ky + 25))

    # ------------------------------------------------------------------
    # Dibujo: footer
    # ------------------------------------------------------------------
    def draw_footer(self):
        fy = HEIGHT - 22
        cr = self.font_tiny.render("ASPR GARDENER · Kids Lab · MIT License · Ramiro", True, TEXT_DIM)
        self.screen.blit(cr, (GRID_LEFT - 80, fy))

    # ------------------------------------------------------------------
    # Actualizar animaciones de flash
    # ------------------------------------------------------------------
    def update_animations(self, dt):
        for i in range(GRID_ROWS):
            if self.row_flash[i] > 0:
                self.row_flash[i] = max(0.0, self.row_flash[i] - dt * 6.0)

    # ------------------------------------------------------------------
    # Manejo de clicks
    # ------------------------------------------------------------------
    def handle_click(self, pos):
        x, y = pos

        # Clicks en grilla
        if (GRID_LEFT <= x < GRID_LEFT + GRID_COLS * CELL_SIZE and
                GRID_TOP <= y < GRID_TOP + GRID_ROWS * CELL_SIZE):
            col = (x - GRID_LEFT) // CELL_SIZE
            row = (y - GRID_TOP) // CELL_SIZE
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                self.grid[row][col] = not self.grid[row][col]
                return

        # Clicks en botones de control
        if hasattr(self, 'button_rects'):
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(x, y):
                    if i == 0:   # Play
                        self.start_sequencer()
                    elif i == 1: # Stop
                        self.stop_sequencer()
                    elif i == 2: # Record (toggle)
                        self.recording = not self.recording
                        self.set_status("Modo grabación ON" if self.recording else "Modo grabación OFF")
                    elif i == 3: # Mix
                        self.mix_pattern()
                    elif i == 4: # Save
                        self.save_project()
                    elif i == 5: # Load (carga el proyecto más reciente automáticamente)
                        projects = self.list_projects()
                        if projects:
                            self.load_project(projects[0])
                        else:
                            self.set_status("No hay proyectos guardados")
                    return

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
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
                        projects = self.list_projects()
                        if projects:
                            self.load_project(projects[0])
                        else:
                            self.set_status("Armario vacío")
                    elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        self.bpm = min(200, self.bpm + 5)
                        self.step_interval = 60.0 / self.bpm / 4
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.bpm = max(60, self.bpm - 5)
                        self.step_interval = 60.0 / self.bpm / 4
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            self.update_animations(dt)

            # Fondo
            self.screen.fill(BG_COLOR)
            for gx in range(0, WIDTH, 40):
                for gy in range(0, HEIGHT, 40):
                    pygame.draw.circle(self.screen, BORDER_COLOR, (gx, gy), 1)

            self.draw_header()
            self.draw_grid()
            self.draw_control_buttons()
            self.draw_keyboard()
            self.draw_footer()

            pygame.display.flip()
            self.clock.tick(60)

        self.stop_sequencer()
        pygame.quit()

# ----------------------------------------------------------------------
if __name__ == "__main__":
    lab = BeatLab()
    lab.run()
