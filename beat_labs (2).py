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

# ----------------------------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 860, 620
GRID_COLS = 8
GRID_ROWS = 5
CELL_SIZE = 64
GRID_LEFT = (WIDTH - (GRID_COLS * CELL_SIZE)) // 2
GRID_TOP = 160

SOUND_NAMES = ["KICK", "SNARE", "HI-HAT", "CLAP", "BASS"]
DEFAULT_BPM = 120

# ── Paleta Kids Lab ──────────────────────────────────────────────────
BG_COLOR       = (8, 6, 18)           # fondo muy oscuro violeta
BG2_COLOR      = (14, 11, 30)
BORDER_COLOR   = (40, 30, 70)
ACCENT         = (0, 229, 180)        # teal brillante
ACCENT2        = (180, 100, 255)      # violeta
TEXT_COLOR     = (210, 200, 240)
TEXT_DIM       = (100, 85, 140)

# Colores por instrumento (Kids Lab vivid)
TRACK_COLORS = [
    (255,  80,  80),   # KICK   → rojo energético
    (255, 180,  30),   # SNARE  → naranja dorado
    ( 50, 220, 255),   # HI-HAT → cyan eléctrico
    (180, 100, 255),   # CLAP   → violeta neón
    ( 60, 230, 130),   # BASS   → verde lima
]

# Versión oscura de cada color (celda apagada)
TRACK_COLORS_DIM = [
    ( 50,  15,  15),
    ( 50,  35,   5),
    (  5,  40,  55),
    ( 30,  10,  55),
    (  5,  45,  20),
]

HIGHLIGHT_COLOR = (255, 255, 255)

# Teclas del teclado que se muestran (solo las necesarias)
KEY_MAP = [
    ("SPACE", "Play/Stop"),
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

# ----------------------------------------------------------------------
# HELPERS DE DIBUJO
# ----------------------------------------------------------------------
def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
    """Dibuja un rect redondeado. border>0 dibuja solo el borde."""
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
            generate_bass()
        ]

        # Estado de la grilla
        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]

        # Secuenciador
        self.bpm = DEFAULT_BPM
        self.playing = False
        self.current_step = 0
        self.last_step_time = 0
        self.step_interval = 60.0 / self.bpm / 4

        # Animaciones: flash por fila cuando se activa
        self.row_flash = [0.0] * GRID_ROWS   # 0.0–1.0 (decae)

        self.running = True
        self.seq_thread = None

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
    # Dibujo: header
    # ------------------------------------------------------------------
    def draw_header(self):
        # Título
        title = self.font_big.render("BEAT LAB", True, ACCENT)
        self.screen.blit(title, (GRID_LEFT, 18))

        sub = self.font_tiny.render("ASPR GARDENER · KIDS LAB", True, TEXT_DIM)
        self.screen.blit(sub, (GRID_LEFT, 44))

        # Estado play/stop con badge
        if self.playing:
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

        # BPM
        bpm_label = self.font_small.render(f"BPM: {self.bpm}", True, ACCENT2)
        self.screen.blit(bpm_label, (GRID_LEFT + 150, 74))

        # Línea separadora
        pygame.draw.line(self.screen, BORDER_COLOR,
                         (GRID_LEFT - 80, 110), (GRID_LEFT + GRID_COLS * CELL_SIZE + 10, 110), 1)

    # ------------------------------------------------------------------
    # Dibujo: grilla
    # ------------------------------------------------------------------
    def draw_grid(self):
        # Números de paso arriba
        for col in range(GRID_COLS):
            x = GRID_LEFT + col * CELL_SIZE + CELL_SIZE // 2 - 8
            num = self.font_tiny.render(str(col + 1), True,
                                        ACCENT if (self.playing and col == self.current_step) else TEXT_DIM)
            self.screen.blit(num, (x, GRID_TOP - 22))

        for row in range(GRID_ROWS):
            color_on  = TRACK_COLORS[row]
            color_off = TRACK_COLORS_DIM[row]
            flash_t   = self.row_flash[row]

            # Etiqueta de pista (izquierda)
            lx = GRID_LEFT - 78
            ly = GRID_TOP + row * CELL_SIZE + CELL_SIZE // 2 - 8
            track_label = self.font_small.render(SOUND_NAMES[row], True, color_on)
            self.screen.blit(track_label, (lx, ly))

            # Flash del nombre cuando suena
            if flash_t > 0:
                bright = self.font_small.render(SOUND_NAMES[row], True,
                                                lerp_color(color_on, (255, 255, 255), flash_t * 0.6))
                self.screen.blit(bright, (lx, ly))

            for col in range(GRID_COLS):
                x = GRID_LEFT + col * CELL_SIZE
                y = GRID_TOP + row * CELL_SIZE
                rect = (x + 3, y + 3, CELL_SIZE - 8, CELL_SIZE - 8)

                if self.grid[row][col]:
                    # Celda activa: color vivo con brillo si está en el paso actual
                    c = lerp_color(color_on, (255, 255, 255),
                                   0.4 if (self.playing and col == self.current_step) else 0.0)
                    draw_rounded_rect(self.screen, c, rect, radius=8)
                    # Pequeño punto central
                    cx = x + CELL_SIZE // 2
                    cy = y + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, (255, 255, 255, 80), (cx, cy), 4)
                else:
                    draw_rounded_rect(self.screen, color_off, rect, radius=8)
                    # Borde sutil
                    draw_rounded_rect(self.screen, color_off, rect, radius=8,
                                      border=1, border_color=lerp_color(color_off, color_on, 0.3))

                # Cursor de paso activo
                if self.playing and col == self.current_step:
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOR,
                                     (x + 2, y + 2, CELL_SIZE - 6, CELL_SIZE - 6), 2)

    # ------------------------------------------------------------------
    # Dibujo: teclado retro (solo teclas necesarias)
    # ------------------------------------------------------------------
    def draw_keyboard(self):
        kb_y = GRID_TOP + GRID_ROWS * CELL_SIZE + 28
        kb_x = GRID_LEFT - 80
        pygame.draw.line(self.screen, BORDER_COLOR, (kb_x, kb_y - 10), (kb_x + 500, kb_y - 10), 1)

        label = self.font_tiny.render("KEYBOARD SHORTCUTS", True, TEXT_DIM)
        self.screen.blit(label, (kb_x, kb_y - 7))
        kb_y += 14

        key_w, key_h = 90, 44
        gap = 12

        for i, (key, action) in enumerate(KEY_MAP):
            kx = kb_x + i * (key_w + gap)
            ky = kb_y

            # Cuerpo de la tecla (estilo keycap 3D retro)
            body_color = (28, 20, 50)
            shadow_color = (10, 6, 22)
            # Sombra inferior (efecto 3D)
            draw_rounded_rect(self.screen, shadow_color, (kx + 2, ky + 4, key_w, key_h), radius=7)
            # Cuerpo principal
            draw_rounded_rect(self.screen, body_color, (kx, ky, key_w, key_h), radius=7)
            # Borde brillante (arriba/izq)
            pygame.draw.line(self.screen, (60, 45, 100), (kx + 7, ky), (kx + key_w - 7, ky), 1)
            pygame.draw.line(self.screen, (60, 45, 100), (kx, ky + 7), (kx, ky + key_h - 7), 1)

            # Texto de la tecla
            k_surf = self.font_med.render(key, True, ACCENT)
            kw = k_surf.get_width()
            self.screen.blit(k_surf, (kx + (key_w - kw) // 2, ky + 6))

            # Acción
            a_surf = self.font_tiny.render(action, True, TEXT_DIM)
            aw = a_surf.get_width()
            self.screen.blit(a_surf, (kx + (key_w - aw) // 2, ky + 27))

    # ------------------------------------------------------------------
    # Dibujo: footer / créditos
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
        if (GRID_LEFT <= x < GRID_LEFT + GRID_COLS * CELL_SIZE and
                GRID_TOP <= y < GRID_TOP + GRID_ROWS * CELL_SIZE):
            col = (x - GRID_LEFT) // CELL_SIZE
            row = (y - GRID_TOP) // CELL_SIZE
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                self.grid[row][col] = not self.grid[row][col]

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
                    elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        self.bpm = min(200, self.bpm + 5)
                        self.step_interval = 60.0 / self.bpm / 4
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.bpm = max(60, self.bpm - 5)
                        self.step_interval = 60.0 / self.bpm / 4
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            self.update_animations(dt)

            # Fondo con grid puntillado sutil
            self.screen.fill(BG_COLOR)
            for gx in range(0, WIDTH, 40):
                for gy in range(0, HEIGHT, 40):
                    pygame.draw.circle(self.screen, BORDER_COLOR, (gx, gy), 1)

            self.draw_header()
            self.draw_grid()
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
