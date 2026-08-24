#!/usr/bin/env python3
"""
Beat Lab v2.4 FINAL - Sonido Personalizado
ASPR Gardener · Kids Lab
"""

import os
# os.environ['SDL_AUDIODRIVER'] = 'dummy'   # Comenta esta línea si ya tienes sonido real

import pygame
import numpy as np
import time
import threading
import json
import wave
from datetime import datetime

# ----------------------------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 1280, 720
GRID_COLS = 15
GRID_ROWS = 9
CELL_WIDTH = 48
CELL_HEIGHT = 52
GRID_LEFT = 60
GRID_TOP = 140

SOUND_NAMES = ["KICK", "SNARE", "HI-HAT", "CLAP", "BASS", "TOM", "RIM", "CRASH", "SHAKER"]

DEFAULT_BPM = 120

BG_COLOR       = (8, 6, 18)
BORDER_COLOR   = (40, 30, 70)
ACCENT         = (0, 229, 180)
ACCENT2        = (180, 100, 255)
TEXT_COLOR     = (210, 200, 240)
TEXT_DIM       = (100, 85, 140)
PANEL_BG       = (12, 9, 22)

TRACK_COLORS = [(255,80,80),(255,180,30),(50,220,255),(180,100,255),(60,230,130),
                (255,140,0),(220,50,220),(255,50,180),(80,255,120)]
TRACK_COLORS_DIM = [(50,15,15),(50,35,5),(5,40,55),(30,10,55),(5,45,20),
                    (40,20,0),(40,0,40),(50,10,35),(15,50,25)]

SAMPLE_RATE = 44100

# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------
def _make_sound_from_array(wave_int16):
    wave_int16 = np.ascontiguousarray(wave_int16)
    try:
        return pygame.sndarray.make_sound(wave_int16)
    except:
        stereo = np.column_stack((wave_int16, wave_int16))
        return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))

def draw_rounded_rect(surface, color, rect, radius=8):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x+radius, y, w-2*radius, h))
    pygame.draw.rect(surface, color, (x, y+radius, w, h-2*radius))
    for cx, cy in [(x+radius,y+radius),(x+w-radius-1,y+radius),
                   (x+radius,y+h-radius-1),(x+w-radius-1,y+h-radius-1)]:
        pygame.draw.circle(surface, color, (cx, cy), radius)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

# ----------------------------------------------------------------------
# SÍNTESIS BASE
# ----------------------------------------------------------------------
def synth_kick(): 
    d=0.2; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); f=np.linspace(150,40,len(t)); return np.sin(2*np.pi*f*t)*np.exp(-5*t)
def synth_snare(): 
    d=0.15; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); n=np.random.normal(0,1,len(t)); e=np.exp(-20*t); return (n*e + np.sin(2*np.pi*180*t)*e*0.5)
def synth_hihat(): 
    d=0.05; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); n=np.random.normal(0,1,len(t)); f=n[1:]-0.8*n[:-1]; f=np.append(f,0); return f*np.exp(-80*t)*0.6
def synth_clap(): 
    d=0.1; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); return np.random.normal(0,1,len(t))*np.exp(-15*t)
def synth_bass(): 
    d=0.3; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); w=np.sin(2*np.pi*70*t)*0.5; saw=2*(t*70-np.floor(0.5+t*70)); return (w+saw*0.3)*np.exp(-3*t)
def synth_tom(): 
    d=0.15; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); f=np.linspace(200,80,len(t)); return np.sin(2*np.pi*f*t)*np.exp(-10*t)
def synth_rim(): 
    d=0.03; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); n=np.random.normal(0,1,len(t)); return (n*0.7 + np.sin(2*np.pi*1200*t)*0.3)*np.exp(-120*t)
def synth_crash(): 
    d=1.5; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); n=np.random.normal(0,1,len(t)); f=n[1:]-0.98*n[:-1]; f=np.append(f,0); return f*np.power(np.exp(-t),1.8)*1.3
def synth_shaker(): 
    d=0.1; t=np.linspace(0,d,int(SAMPLE_RATE*d),False); n=np.random.normal(0,1,len(t)); e=np.exp(-50*t); return (n*e + np.sin(2*np.pi*2500*t)*0.2*e)*0.65

# ----------------------------------------------------------------------
# CLASE PRINCIPAL
# ----------------------------------------------------------------------
class BeatLab:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Beat Lab v2.4 - Sonido Personalizado")
        self.clock = pygame.time.Clock()

        self.font_big   = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_med   = pygame.font.SysFont("Courier New", 16, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 13)
        self.font_tiny  = pygame.font.SysFont("Courier New", 11)

        self.projects_dir = "beatlab_projects"
        os.makedirs(self.projects_dir, exist_ok=True)
        self.samples_dir = "beatlab_samples"
        os.makedirs(self.samples_dir, exist_ok=True)

        self.sample_files = []
        self.loaded_samples = {}
        self.base_sounds = [synth_kick, synth_snare, synth_hihat, synth_clap,
                            synth_bass, synth_tom, synth_rim, synth_crash, synth_shaker]

        self.refresh_sample_list()   # ← Primero cargamos samples

        self.sounds = [None] * GRID_ROWS
        self.reload_sounds()         # ← Ahora sí podemos recargar

        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]
        self.bpm = DEFAULT_BPM
        self.playing = False
        self.recording = False
        self.current_step = 0
        self.last_step_time = 0
        self.step_interval = 60.0 / self.bpm / 4

        self.track_mute = [False] * GRID_ROWS
        self.track_solo = [False] * GRID_ROWS
        self.row_flash = [0.0] * GRID_ROWS

        self.running = True
        self.seq_thread = None
        self.status_message = ""
        self.status_timer = 0
        self.project_list = []
        self.selected_project_index = -1
        self.effects_mode = False
        self.last_triggered_row = 0

        self.refresh_project_list()

    def reload_sounds(self):
        for i in range(GRID_ROWS):
            custom_name = f"{SOUND_NAMES[i].lower()}.wav"
            if custom_name in self.loaded_samples:
                self.sounds[i] = self.loaded_samples[custom_name]
            else:
                arr = self.base_sounds[i]()
                self.sounds[i] = _make_sound_from_array((arr * 32767).astype(np.int16))

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

    def refresh_project_list(self):
        self.project_list = [f for f in os.listdir(self.projects_dir) if f.endswith('.json')]
        self.project_list.sort(reverse=True)

    def set_status(self, msg):
        self.status_message = msg
        self.status_timer = 180

    # ------------------------------------------------------------------
    # Secuenciador y lógica
    # ------------------------------------------------------------------
    def _should_play_track(self, row):
        if any(self.track_solo): return self.track_solo[row]
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

    def mix_pattern(self):
        import random
        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]
        for s in [0,4,8,12]: self.grid[0][s] = True
        for s in [3,7,11]:
            self.grid[1][s] = True
            if s+1 < GRID_COLS: self.grid[3][s+1] = True
        for s in range(0, GRID_COLS, 2):
            self.grid[2][s] = True
            self.grid[4][s] = random.choice([True, False])
        for s in [2,6,10,14]: self.grid[5][s] = True
        for s in [5,9,13]: self.grid[6][s] = True
        self.grid[7][14] = True
        for s in range(1, GRID_COLS, 3):
            if s < GRID_COLS: self.grid[8][s] = True
        self.set_status("Mix con segunda capa (CRASH + SHAKER)")

    def reset_grid(self):
        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]
        self.set_status("Grid reseteado")

    def save_project(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proyecto_{ts}.json"
        path = os.path.join(self.projects_dir, filename)
        data = {"grid": self.grid, "bpm": self.bpm}
        with open(path, 'w') as f: json.dump(data, f, indent=2)
        self.set_status(f"Guardado: {filename}")
        self.refresh_project_list()

    def load_project(self, filename):
        path = os.path.join(self.projects_dir, filename)
        if not os.path.exists(path): return
        with open(path, 'r') as f: data = json.load(f)
        old_grid = data.get("grid", [[False]*GRID_COLS for _ in range(GRID_ROWS)])
        self.bpm = data.get("bpm", DEFAULT_BPM)
        self.step_interval = 60.0 / self.bpm / 4

        self.grid = [[False]*GRID_COLS for _ in range(GRID_ROWS)]
        rows_to_copy = min(len(old_grid), GRID_ROWS)
        for r in range(rows_to_copy):
            cols_to_copy = min(len(old_grid[r]), GRID_COLS)
            for c in range(cols_to_copy):
                self.grid[r][c] = old_grid[r][c]
        self.set_status(f"Cargado: {filename}")

    def export_pattern_to_wav(self, grid, bpm, filename, num_loops=4):
        step_d = 60.0 / bpm / 4
        total = int(GRID_COLS * num_loops * step_d * SAMPLE_RATE)
        buffer = np.zeros(total, dtype=np.float32)

        audios = []
        for i in range(GRID_ROWS):
            try:
                arr = pygame.sndarray.array(self.sounds[i])
                if len(arr.shape) == 2: arr = arr.mean(axis=1).astype(np.float32)
                audios.append(arr / 32767.0)
            except:
                arr = self.base_sounds[i]()
                audios.append(arr)

        for loop in range(num_loops):
            for step in range(GRID_COLS):
                start = int((loop*GRID_COLS + step) * step_d * SAMPLE_RATE)
                end = min(start + int(step_d * SAMPLE_RATE), total)
                for row in range(GRID_ROWS):
                    if row < len(grid) and grid[row][step]:
                        a = audios[row]
                        leng = min(len(a), end - start)
                        buffer[start:start+leng] += a[:leng]

        max_val = np.max(np.abs(buffer))
        if max_val > 0:
            buffer = buffer / max_val * 0.95
        data = (buffer * 32767).astype(np.int16)

        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(data.tobytes())

        self.set_status(f"Exportado: {os.path.basename(filename)}")

    def export_current_pattern(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.projects_dir, f"export_{ts}.wav")
        self.export_pattern_to_wav(self.grid, self.bpm, filename)

    def export_all_projects(self):
        if not self.project_list:
            self.set_status("No hay proyectos")
            return
        count = 0
        for proj in self.project_list:
            try:
                path = os.path.join(self.projects_dir, proj)
                with open(path, 'r') as f:
                    data = json.load(f)
                grid = data.get("grid", [[False]*GRID_COLS for _ in range(GRID_ROWS)])
                bpm = data.get("bpm", DEFAULT_BPM)
                out_name = proj.replace('.json', '.wav')
                self.export_pattern_to_wav(grid, bpm, os.path.join(self.projects_dir, out_name))
                count += 1
            except:
                pass
        self.set_status(f"Exportados {count} proyectos")

    # ----------------------------------------------------------------------
    # DIBUJO Y EVENTOS
    # ----------------------------------------------------------------------
    def draw_header(self):
        title = self.font_big.render("BEAT LAB", True, ACCENT)
        self.screen.blit(title, (GRID_LEFT, 18))
        sub = self.font_tiny.render("v2.4 - Sonido Personalizado", True, TEXT_DIM)
        self.screen.blit(sub, (GRID_LEFT, 44))

        if self.recording:
            col, txt, txtcol = (200,60,60), "● REC", (255,150,150)
        elif self.playing:
            col, txt, txtcol = (0,180,90), "▶ PLAYING", (0,255,140)
        else:
            col, txt, txtcol = (50,30,70), "⏸ STOPPED", TEXT_DIM

        draw_rounded_rect(self.screen, col, (GRID_LEFT, 68, 130, 26))
        self.screen.blit(self.font_small.render(txt, True, txtcol), (GRID_LEFT+8, 75))
        self.screen.blit(self.font_small.render(f"BPM: {self.bpm}", True, ACCENT2), (GRID_LEFT+160, 74))

        if self.status_timer > 0:
            self.screen.blit(self.font_tiny.render(self.status_message, True, ACCENT), (GRID_LEFT+300, 76))
            self.status_timer -= 1

    def draw_grid(self):
        for col in range(GRID_COLS):
            x = GRID_LEFT + col*CELL_WIDTH + CELL_WIDTH//2 - 6
            color = ACCENT if self.playing and col == self.current_step else TEXT_DIM
            num = self.font_tiny.render(str(col+1), True, color)
            self.screen.blit(num, (x, GRID_TOP-22))

        for row in range(GRID_ROWS):
            color_on = TRACK_COLORS[row]
            color_off = TRACK_COLORS_DIM[row]
            flash = self.row_flash[row]
            lx = GRID_LEFT - 52
            ly = GRID_TOP + row*CELL_HEIGHT + CELL_HEIGHT//2 - 8
            self.screen.blit(self.font_small.render(SOUND_NAMES[row], True, color_on), (lx, ly))
            if flash > 0:
                bright = self.font_small.render(SOUND_NAMES[row], True, lerp_color(color_on, (255,255,255), flash*0.6))
                self.screen.blit(bright, (lx, ly))
            for col in range(GRID_COLS):
                x = GRID_LEFT + col * CELL_WIDTH
                y = GRID_TOP + row * CELL_HEIGHT
                rect = (x+2, y+2, CELL_WIDTH-6, CELL_HEIGHT-6)
                if self.grid[row][col]:
                    c = lerp_color(color_on, (255,255,255), 0.4 if self.playing and col==self.current_step else 0)
                    draw_rounded_rect(self.screen, c, rect, 6)
                else:
                    draw_rounded_rect(self.screen, color_off, rect, 6)

    def draw_right_panel(self):
        px = GRID_LEFT + GRID_COLS*CELL_WIDTH + 20
        pw = WIDTH - px - 20
        pygame.draw.rect(self.screen, PANEL_BG, (px, GRID_TOP-20, pw, HEIGHT-GRID_TOP-40))
        pygame.draw.rect(self.screen, BORDER_COLOR, (px, GRID_TOP-20, pw, HEIGHT-GRID_TOP-40), 2)

        y = GRID_TOP + 10
        self.screen.blit(self.font_med.render("MONITOR", True, ACCENT2), (px+10, y))
        y += 25
        self.screen.blit(self.font_tiny.render("TRACK  M  S  ▶", True, TEXT_DIM), (px+10, y))
        y += 20

        self.track_control_rects = []
        for row in range(GRID_ROWS):
            color = TRACK_COLORS[row]
            name = SOUND_NAMES[row][:5]
            self.screen.blit(self.font_tiny.render(name, True, color), (px+10, y+4))
            mrect = pygame.Rect(px+85, y, 18, 18)
            srect = pygame.Rect(px+107, y, 18, 18)
            trect = pygame.Rect(px+130, y, 22, 18)
            draw_rounded_rect(self.screen, (200,60,60) if self.track_mute[row] else (60,60,100), mrect, 3)
            draw_rounded_rect(self.screen, (200,200,60) if self.track_solo[row] else (60,60,100), srect, 3)
            draw_rounded_rect(self.screen, (80,80,120), trect, 3)
            self.screen.blit(self.font_tiny.render("M", True, (255,255,255)), (px+90, y+3))
            self.screen.blit(self.font_tiny.render("S", True, (0,0,0) if self.track_solo[row] else (255,255,255)), (px+112, y+3))
            self.screen.blit(self.font_tiny.render("▶", True, ACCENT), (px+136, y+3))
            self.track_control_rects.append((row, mrect, srect, trect))
            y += 24

        # Samples Personalizados
        y += 15
        self.screen.blit(self.font_med.render("SAMPLES PERSONALIZADOS", True, ACCENT), (px+10, y))
        y += 25
        self.sample_rects = []
        for i, fname in enumerate(self.sample_files[:6]):
            item_y = y + i*24
            rect = pygame.Rect(px+8, item_y, pw-16, 22)
            pygame.draw.rect(self.screen, (60,50,90), rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, rect, 1)
            name = fname.replace(".wav", "")[:18]
            self.screen.blit(self.font_tiny.render(name, True, TEXT_COLOR), (px+12, item_y+4))
            self.sample_rects.append((fname, rect))
        if not self.sample_files:
            self.screen.blit(self.font_tiny.render("(pon .wav en beatlab_samples/)", True, TEXT_DIM), (px+12, y))

        # Botones proyectos
        y += 170
        btn_h = 24
        self.load_btn = pygame.Rect(px+10, y, 70, btn_h)
        self.refresh_btn = pygame.Rect(px+85, y, 50, btn_h)
        self.del_btn = pygame.Rect(px+140, y, 70, btn_h)
        self.expall_btn = pygame.Rect(px+215, y, 85, btn_h)

        draw_rounded_rect(self.screen, (40,80,120), self.load_btn, 5)
        draw_rounded_rect(self.screen, (60,60,90), self.refresh_btn, 5)
        draw_rounded_rect(self.screen, (120,50,50), self.del_btn, 5)
        draw_rounded_rect(self.screen, (70,130,70), self.expall_btn, 5)

        self.screen.blit(self.font_tiny.render("Cargar", True, (220,220,250)), (px+16, y+5))
        self.screen.blit(self.font_tiny.render("↻", True, TEXT_DIM), (px+98, y+5))
        self.screen.blit(self.font_tiny.render("Borrar", True, (220,220,250)), (px+148, y+5))
        self.screen.blit(self.font_tiny.render("EXP ALL", True, (255,255,200)), (px+220, y+5))

    def draw_control_buttons(self):
        btn_y = GRID_TOP + GRID_ROWS * CELL_HEIGHT + 25
        btn_x = GRID_LEFT
        btn_w, btn_h = 78, 36
        gap = 8
        buttons = [
            ("▶ PLAY", self.playing, (0,200,100) if self.playing else (40,40,70)),
            ("⏹ STOP", not self.playing, (200,60,60) if not self.playing else (40,40,70)),
            ("● REC", self.recording, (220,30,30) if self.recording else (40,40,70)),
            ("🔄 MIX", False, (70,50,140)),
            ("💾 SAVE", False, (50,100,150)),
            ("✨ EFX", self.effects_mode, (120,60,180) if self.effects_mode else (40,40,70)),
            ("📀 WAV", False, (30,100,130)),
            ("🔴 RESET", False, (180,40,40))
        ]
        self.button_rects = []
        for i, (text, active, base) in enumerate(buttons):
            bx = btn_x + i*(btn_w + gap)
            color = lerp_color(base, (255,255,255), 0.3) if active else base
            draw_rounded_rect(self.screen, color, (bx, btn_y, btn_w, btn_h))
            label = self.font_small.render(text, True, (220,220,250))
            self.screen.blit(label, (bx + (btn_w - label.get_width())//2, btn_y + 10))
            self.button_rects.append(pygame.Rect(bx, btn_y, btn_w, btn_h))

    def handle_click(self, pos):
        x, y = pos

        # Grid
        if GRID_LEFT <= x < GRID_LEFT + GRID_COLS*CELL_WIDTH and GRID_TOP <= y < GRID_TOP + GRID_ROWS*CELL_HEIGHT:
            col = (x - GRID_LEFT) // CELL_WIDTH
            row = (y - GRID_TOP) // CELL_HEIGHT
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                self.grid[row][col] = not self.grid[row][col]
                self.last_triggered_row = row
                return

        # Botones inferiores
        if hasattr(self, 'button_rects'):
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(x, y):
                    if i == 0: self.start_sequencer()
                    elif i == 1: self.stop_sequencer()
                    elif i == 2: 
                        self.recording = not self.recording
                        self.set_status("REC " + ("ON" if self.recording else "OFF"))
                    elif i == 3: self.mix_pattern()
                    elif i == 4: self.save_project()
                    elif i == 5: 
                        self.effects_mode = not self.effects_mode
                        self.set_status("EFX " + ("ON" if self.effects_mode else "OFF"))
                    elif i == 6: self.export_current_pattern()
                    elif i == 7: self.reset_grid()
                    return

        # Controles de pista
        if hasattr(self, 'track_control_rects'):
            for row, mrect, srect, trect in self.track_control_rects:
                if mrect.collidepoint(x,y):
                    self.track_mute[row] = not self.track_mute[row]
                    if self.track_mute[row]: self.track_solo[row] = False
                    return
                if srect.collidepoint(x,y):
                    self.track_solo[row] = not self.track_solo[row]
                    if self.track_solo[row]: self.track_mute[row] = False
                    return
                if trect.collidepoint(x,y):
                    self.sounds[row].play()
                    self.row_flash[row] = 1.0
                    self.last_triggered_row = row
                    return

        # Samples personalizados
        if hasattr(self, 'sample_rects'):
            for fname, rect in self.sample_rects:
                if rect.collidepoint(x,y):
                    if fname in self.loaded_samples:
                        self.loaded_samples[fname].play()
                        row_to_assign = self.last_triggered_row
                        self.sounds[row_to_assign] = self.loaded_samples[fname]
                        self.set_status(f"Asignado {fname} → {SOUND_NAMES[row_to_assign]}")
                    return

        # Proyectos
        if hasattr(self, 'load_btn') and self.load_btn.collidepoint(x,y):
            if 0 <= self.selected_project_index < len(self.project_list):
                self.load_project(self.project_list[self.selected_project_index])
        if hasattr(self, 'refresh_btn') and self.refresh_btn.collidepoint(x,y):
            self.refresh_project_list()
            self.selected_project_index = -1
        if hasattr(self, 'del_btn') and self.del_btn.collidepoint(x,y):
            if 0 <= self.selected_project_index < len(self.project_list):
                try:
                    os.remove(os.path.join(self.projects_dir, self.project_list[self.selected_project_index]))
                    self.set_status("Proyecto borrado")
                except:
                    self.set_status("Error al borrar")
                self.refresh_project_list()
                self.selected_project_index = -1
        if hasattr(self, 'expall_btn') and self.expall_btn.collidepoint(x,y):
            self.export_all_projects()

    def update_animations(self, dt):
        for i in range(GRID_ROWS):
            if self.row_flash[i] > 0:
                self.row_flash[i] = max(0, self.row_flash[i] - dt*6)

    def run(self):
        prev = time.time()
        while self.running:
            dt = time.time() - prev
            prev = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                    elif event.key == pygame.K_SPACE:
                        if self.playing: self.stop_sequencer()
                        else: self.start_sequencer()
                    elif event.key == pygame.K_m: self.mix_pattern()
                    elif event.key == pygame.K_s: self.save_project()
                    elif event.key == pygame.K_r:
                        self.recording = not self.recording
                        self.set_status("REC " + ("ON" if self.recording else "OFF"))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            self.update_animations(dt)
            self.screen.fill(BG_COLOR)
            self.draw_header()
            self.draw_grid()
            self.draw_right_panel()
            self.draw_control_buttons()
            pygame.display.flip()
            self.clock.tick(60)

        self.stop_sequencer()
        pygame.quit()

if __name__ == "__main__":
    lab = BeatLab()
    lab.run()
