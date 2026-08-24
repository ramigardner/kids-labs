"""
KIDS-LABS — LUKI DRAW EDITION  🐸
========================================
Versión Android táctil para Lucas (6 años)
- Estética KINDER LABS (CRT + terminal retro)
- Dibujo libre con Luki la ranita
- Cofres con objetivo claro (envolver con el rastro)
- Botones grandes estilo terminal [▶ COMANDO]
- Selector de colores · Borrar · Deshacer
- Sin internet · Sin publicidad · 100% libre
"""

import pygame
import sys
import math
import random
import array
import os

# ==================================================================
# DETECCIÓN DE PLATAFORMA
# ==================================================================
ANDROID = os.environ.get("ANDROID_ARGUMENT") is not None or \
          os.environ.get("ANDROID_ROOT") is not None

# ==================================================================
# PALETA DE COLORES — estilo CRT / terminal Kinder Labs
# ==================================================================
PAL = {
    "bg":        (8,   12,  28),    # casi negro con tinte azul
    "bg_deep":   (4,   6,   16),    # canvas interior
    "grid":      (18,  26,  52),    # grilla tenue
    "border":    (0,   220, 180),   # cyan verde — borde principal
    "border_d":  (0,   120, 100),   # cyan oscuro
    "white":     (230, 245, 240),
    "cyan":      (0,   255, 210),   # texto terminal principal
    "green":     (80,  255, 120),   # ok / Luki
    "yellow":    (255, 220, 60),    # estrellas / alerta
    "amber":     (255, 170, 40),    # acento
    "red":       (255, 90,  90),    # peligro / borrar
    "magenta":   (255, 80,  200),
    "grey":      (120, 140, 160),
    "grey_d":    (60,  72,  88),
    "black":     (0,   0,   0),
    "chest":     (180, 110, 50),    # marrón del cofre
    "chest_lid": (140, 80,  30),    # marrón oscuro tapa
    "gold":      (255, 200, 40),    # oro del cofre
}

# Colores que puede elegir Luki para dibujar
INK_COLORS = [
    ("VERDE",    (80,  255, 120)),
    ("CYAN",     (0,   255, 210)),
    ("AMARILLO", (255, 220, 60)),
    ("ROSA",     (255, 100, 180)),
    ("NARANJA",  (255, 160, 60)),
]

# ==================================================================
# SONIDO (onda cuadrada sin archivos externos)
# ==================================================================
class SFX:
    def __init__(self):
        self.ok = False

    def init(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            self.ok = True
        except Exception:
            pass

    def beep(self, freq=880, ms=80, vol=0.18):
        if not self.ok:
            return
        try:
            import numpy as np
            sr = 22050
            n  = int(sr * ms / 1000)
            wave = array.array("h", [
                int(((1 if (i * freq / sr) % 1 < 0.5 else -1)
                     * vol * 32767
                     * (1 - i / n)))
                for i in range(n)
            ])
            stereo = array.array("h")
            for s in wave:
                stereo.append(s); stereo.append(s)
            snd = pygame.sndarray.make_sound(
                np.frombuffer(stereo, dtype="int16").reshape(-1, 2)
            )
            snd.play()
        except Exception:
            pass

    def tap(self):     self.beep(587,  50, 0.08)
    def move(self):    self.beep(523,  70, 0.10)
    def turn(self):    self.beep(440,  60, 0.08)
    def chest(self):
        self.beep(523, 80, 0.15)
        pygame.time.delay(60)
        self.beep(659, 80, 0.15)
        pygame.time.delay(60)
        self.beep(784, 140, 0.18)
    def err(self):     self.beep(220, 80, 0.10)
    def clear_sfx(self): self.beep(330, 100, 0.08)

sfx = SFX()

# ==================================================================
# UTILIDADES DE DIBUJO
# ==================================================================
def draw_grid(surf, color, size=32):
    w, h = surf.get_size()
    for x in range(0, w, size):
        pygame.draw.line(surf, color, (x, 0), (x, h))
    for y in range(0, h, size):
        pygame.draw.line(surf, color, (0, y), (w, y))

def render_text(surf, text, x, y, font, color, center=False, shadow=False):
    if shadow:
        s_shadow = font.render(str(text), True, (0, 0, 0))
        sx = x - s_shadow.get_width() // 2 if center else x
        surf.blit(s_shadow, (sx + 2, y + 2))
    s = font.render(str(text), True, color)
    if center:
        x -= s.get_width() // 2
    surf.blit(s, (x, y))

def draw_progress_bar(surf, x, y, w, h, pct, color_on, color_off, segments=10):
    """Barra de progreso estilo terminal: ████████░░"""
    seg_w = w / segments
    filled = int(pct * segments)
    for i in range(segments):
        rect = pygame.Rect(x + i * seg_w + 1, y, seg_w - 2, h)
        c = color_on if i < filled else color_off
        pygame.draw.rect(surf, c, rect)

def draw_ascii_frame(surf, rect, color, font, title=None):
    """Marco estilo ASCII/terminal con esquinitas."""
    pygame.draw.rect(surf, color, rect, 2)
    # esquinitas brillantes
    for cx, cy in [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]:
        pygame.draw.rect(surf, color, (cx - 3, cy - 3, 8, 8))
    if title:
        title_s = font.render(f" {title} ", True, color)
        tx = rect.x + 16
        ty = rect.y - title_s.get_height() // 2
        # borrar fondo detrás del título
        pygame.draw.rect(surf, PAL["bg"],
                         (tx - 2, ty, title_s.get_width() + 4, title_s.get_height()))
        surf.blit(title_s, (tx, ty))

# ==================================================================
# LUKI — pixel art
# ==================================================================
FROG_PIXELS = [
    *[((4+i), 2, "body") for i in range(7)],
    *[((3+i), 3, "body") for i in range(9)],
    *[((3+i), 4, "body") for i in range(9)],
    *[((3+i), 5, "body") for i in range(9)],
    (4, 3, "eye"), (5, 3, "eye"), (9, 3, "eye"), (10, 3, "eye"),
    (5, 5, "dark"), (6, 5, "mouth"), (7, 5, "mouth"), (8, 5, "mouth"), (9, 5, "dark"),
    *[((3+i), 6, "body") for i in range(9)],
    *[((2+i), 7, "body") for i in range(11)],
    *[((2+i), 8, "body") for i in range(11)],
    *[((2+i), 9, "body") for i in range(11)],
    *[((3+i),10, "body") for i in range(9)],
    (2,11,"dark"),(3,11,"dark"),(4,11,"dark"),
    (9,11,"dark"),(10,11,"dark"),(11,11,"dark"),
    (1,12,"dark"),(2,12,"dark"),(3,12,"dark"),(4,12,"dark"),
    (10,12,"dark"),(11,12,"dark"),(12,12,"dark"),
    (1, 9,"light"),(2, 9,"light"),(13,9,"light"),(12,9,"light"),
    (5,0,"crown"),(6,0,"crown"),(7,0,"crown"),(8,0,"crown"),(9,0,"crown"),
    (4,1,"crown"),(10,1,"crown"),
    (5,1,"star"),(7,1,"star"),(9,1,"star"),
]

def draw_luki(surf, x, y, S=8, bounce=0):
    palette = {
        "body":  (80, 220, 110),
        "dark":  (30, 130, 60),
        "light": (140, 255, 160),
        "eye":   (255, 230, 60),
        "mouth": (20, 100, 40),
        "crown": (240, 200, 0),
        "star":  (255, 255, 120),
    }
    for (col, row, key) in FROG_PIXELS:
        color = palette.get(key, (0, 200, 0))
        pygame.draw.rect(surf, color,
                         (x + col * S, y + row * S + bounce, S, S))

# ==================================================================
# COFRE — dibujo grande y entendible
# ==================================================================
def draw_chest(surf, cx, cy, size=48, open_progress=0.0, t=0.0):
    """Dibuja un cofre grande y claro.
    open_progress: 0.0 = cerrado, 1.0 = completamente abierto
    """
    w = size
    h = int(size * 0.7)
    body_h = int(h * 0.6)
    lid_h = int(h * 0.45)

    # Sombra
    pygame.draw.ellipse(surf, (0, 0, 0),
                        (cx - w//2 + 4, cy + body_h - 6, w, 10))

    # CUERPO del cofre (rectángulo marrón)
    body_rect = pygame.Rect(cx - w//2, cy, w, body_h)
    pygame.draw.rect(surf, PAL["chest"], body_rect)
    pygame.draw.rect(surf, PAL["chest_lid"], body_rect, 3)

    # Tablas verticales del cuerpo
    for i in range(1, 3):
        lx = cx - w//2 + (w * i) // 3
        pygame.draw.line(surf, PAL["chest_lid"],
                         (lx, cy + 2), (lx, cy + body_h - 2), 2)

    # Banda metálica dorada
    band_y = cy + body_h // 2 - 2
    pygame.draw.rect(surf, PAL["gold"], (cx - w//2, band_y, w, 5))
    pygame.draw.rect(surf, (180, 140, 0), (cx - w//2, band_y, w, 5), 1)

    # Cerradura (cuadradito dorado al frente)
    lock_size = 8
    lock_rect = pygame.Rect(cx - lock_size//2, band_y - 2, lock_size, lock_size + 4)
    pygame.draw.rect(surf, PAL["gold"], lock_rect)
    pygame.draw.rect(surf, (120, 90, 0), lock_rect, 1)
    pygame.draw.circle(surf, (120, 90, 0), (cx, band_y + 3), 2)

    # TAPA del cofre (se levanta con open_progress)
    lid_lift = int(lid_h * open_progress)
    lid_rotate = open_progress * 0.6  # inclinación

    # Curva de la tapa
    lid_rect = pygame.Rect(cx - w//2, cy - lid_h + 4 - lid_lift, w, lid_h)
    pygame.draw.rect(surf, PAL["chest"], lid_rect, border_radius=6)
    pygame.draw.rect(surf, PAL["chest_lid"], lid_rect, 3, border_radius=6)

    # Línea horizontal en la tapa
    pygame.draw.line(surf, PAL["chest_lid"],
                     (lid_rect.x + 3, lid_rect.centery),
                     (lid_rect.right - 3, lid_rect.centery), 2)

    # Si está abierto, mostrar tesoro (estrella dorada brillando)
    if open_progress > 0.3:
        shine = abs(math.sin(t * 5)) * 4
        star_y = cy - int(open_progress * 8) - int(shine)
        # rayos de luz
        for a in range(0, 360, 45):
            rad = math.radians(a)
            r = 18 + int(shine)
            pygame.draw.line(surf, PAL["gold"],
                             (cx, star_y),
                             (cx + int(math.cos(rad)*r),
                              star_y + int(math.sin(rad)*r)), 1)
        # estrella central
        draw_star(surf, cx, star_y, size=10, color=PAL["yellow"])


def draw_star(surf, cx, cy, size=10, color=(255, 220, 60)):
    """Estrella de 5 puntas en pixel art."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size // 2
        points.append((cx + r * math.cos(angle),
                       cy - r * math.sin(angle)))
    pygame.draw.polygon(surf, color, points)
    pygame.draw.polygon(surf, (255, 255, 200), points, 1)


def draw_question_mark(surf, cx, cy, font, color, bounce=0):
    """Signo de pregunta flotando sobre cofre cerrado."""
    # circulo de fondo
    pygame.draw.circle(surf, PAL["bg_deep"], (cx, cy + bounce), 11)
    pygame.draw.circle(surf, color, (cx, cy + bounce), 11, 2)
    s = font.render("?", True, color)
    surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2 + bounce))

# ==================================================================
# BOTÓN TÁCTIL — estilo terminal [▶ COMANDO]
# ==================================================================
class TermButton:
    def __init__(self, rect, label, color, font, icon=""):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.color   = color
        self.font    = font
        self.icon    = icon
        self.pressed = False
        self._press_t = 0
        self.enabled = True

    def handle(self, ev):
        if not self.enabled:
            return False
        if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if ev.type == pygame.FINGERDOWN:
                W, H = pygame.display.get_surface().get_size()
                pos = (int(ev.x * W), int(ev.y * H))
            else:
                pos = ev.pos
            if self.rect.collidepoint(pos):
                self.pressed = True
                self._press_t = 8
                sfx.tap()
                return True
        return False

    def update(self):
        if self._press_t > 0:
            self._press_t -= 1
        else:
            self.pressed = False

    def draw(self, surf):
        r = self.rect.inflate(-4, -4) if self.pressed else self.rect
        alpha = 255 if self.enabled else 100

        # Sombra negra debajo
        shadow = r.move(4, 4) if not self.pressed else r.move(1, 1)
        pygame.draw.rect(surf, (0, 0, 0), shadow, border_radius=4)

        # Fondo del botón (oscuro)
        pygame.draw.rect(surf, PAL["bg_deep"], r, border_radius=4)
        # Borde de color
        pygame.draw.rect(surf, self.color, r, 3, border_radius=4)

        # Esquinitas decorativas estilo terminal ┌ ┐ └ ┘
        cs = 8
        for (cx, cy, dx1, dy1, dx2, dy2) in [
            (r.x,         r.y,           0,  cs,  cs,  0),   # ┌
            (r.right-1,   r.y,           0,  cs, -cs,  0),   # ┐
            (r.x,         r.bottom-1,    0, -cs,  cs,  0),   # └
            (r.right-1,   r.bottom-1,    0, -cs, -cs,  0),   # ┘
        ]:
            pygame.draw.line(surf, self.color, (cx, cy), (cx + dx1, cy + dy1), 3)
            pygame.draw.line(surf, self.color, (cx, cy), (cx + dx2, cy + dy2), 3)

        # Texto (ícono + label)
        full = f"{self.icon} {self.label}" if self.icon else self.label
        txt = self.font.render(full, True, self.color if self.enabled else PAL["grey_d"])
        tx = r.centerx - txt.get_width() // 2
        ty = r.centery - txt.get_height() // 2
        surf.blit(txt, (tx, ty))

# ==================================================================
# PANTALLA — tamaño adaptativo
# ==================================================================
def get_screen_size():
    if ANDROID:
        info = pygame.display.Info()
        return info.current_w, info.current_h
    return 1024, 640

# ==================================================================
# PANTALLA DE BIENVENIDA
# ==================================================================
class WelcomeScreen:
    def __init__(self, fonts, W, H):
        self.fonts = fonts
        self.W, self.H = W, H
        self.done = False
        self.t = 0.0
        self.load_pct = 0.0  # barra de "carga" decorativa

        btn_w, btn_h = int(W * 0.55), int(H * 0.14)
        self.btn = TermButton(
            ((W - btn_w) // 2, int(H * 0.74), btn_w, btn_h),
            "JUGAR",
            PAL["green"],
            fonts["btn"],
            icon="▶"
        )

    def handle(self, ev):
        if self.btn.handle(ev):
            self.done = True

    def update(self, dt):
        self.t += dt
        self.btn.update()
        # barra que va subiendo de 0 a 1 en 2 segundos y se queda
        if self.load_pct < 1.0:
            self.load_pct = min(1.0, self.load_pct + dt * 0.6)

    def draw(self, surf):
        surf.fill(PAL["bg"])
        draw_grid(surf, PAL["grid"])
        W, H = self.W, self.H

        # ── HEADER estilo terminal ─────────────────────────────
        render_text(surf, "★ KINDER LABS ★", W // 2, int(H * 0.04),
                    self.fonts["title"], PAL["cyan"], center=True, shadow=True)
        render_text(surf, "── LUKI DRAW EDITION ──", W // 2, int(H * 0.13),
                    self.fonts["sub"], PAL["amber"], center=True)

        # Luki animado con corona
        bounce = int(math.sin(self.t * 3) * 6)
        S = max(6, W // 90)
        luki_w = 14 * S
        draw_luki(surf, W // 2 - luki_w // 2, int(H * 0.20), S=S, bounce=bounce)

        # Nombre del jugador
        render_text(surf, "HOLA LUCAS", W // 2, int(H * 0.50),
                    self.fonts["sub"], PAL["yellow"], center=True, shadow=True)
        render_text(surf, "Luki te espera para dibujar", W // 2, int(H * 0.58),
                    self.fonts["small"], PAL["green"], center=True)

        # Barra de carga decorativa ████████░░
        bar_w = int(W * 0.45)
        bar_x = (W - bar_w) // 2
        bar_y = int(H * 0.66)
        render_text(surf, f"CARGANDO... {int(self.load_pct*100)}%",
                    W // 2, bar_y - 22,
                    self.fonts["small"], PAL["cyan"], center=True)
        draw_progress_bar(surf, bar_x, bar_y, bar_w, 14,
                          self.load_pct, PAL["green"], PAL["grey_d"], segments=12)

        # Botón JUGAR
        self.btn.draw(surf)

        # ── FOOTER ─────────────────────────────
        render_text(surf, "─── CONECTADO · MIT LICENSE · v2.0 ───",
                    W // 2, H - 22,
                    self.fonts["tiny"], PAL["grey"], center=True)

# ==================================================================
# PANTALLA PRINCIPAL DE DIBUJO
# ==================================================================
class DrawScreen:
    CELL = 28  # tamaño de celda de la grilla lógica

    def __init__(self, fonts, W, H):
        self.fonts = fonts
        self.W, self.H = W, H
        self.done = False
        self.t = 0.0

        # ── LAYOUT ────────────────────────────────────────
        # Barra de status arriba
        self.header_h = int(H * 0.08)
        # Barra de status abajo
        self.footer_h = int(H * 0.06)
        # Panel de botones a la derecha
        self.panel_w = int(W * 0.30)

        # Canvas a la izquierda
        canvas_max_w = W - self.panel_w - int(W * 0.04)
        canvas_max_h = H - self.header_h - self.footer_h - int(H * 0.04)
        canvas_size = min(canvas_max_w, canvas_max_h)
        canvas_x = int(W * 0.02)
        canvas_y = self.header_h + (canvas_max_h - canvas_size) // 2

        self.canvas_rect = pygame.Rect(canvas_x, canvas_y, canvas_size, canvas_size)
        self.cells = canvas_size // self.CELL

        # Estado de Luki
        self.start_pos = (self.cells // 2, self.cells // 2)
        self.frog_x = float(self.start_pos[0])
        self.frog_y = float(self.start_pos[1])
        self.frog_angle = 0  # 0=arriba, 90=derecha, 180=abajo, 270=izquierda

        # Rastros con colores (lista de (x1,y1,x2,y2,color))
        self.trail_segments = []
        self.last_pos = (int(self.frog_x), int(self.frog_y))

        # Color actual
        self.color_idx = 0

        # Historial para DESHACER (lista de estados)
        self.history = []

        # Cofres
        self.chests = []
        self._generate_chests()
        self.chests_opened = 0

        # Efectos visuales
        self.flash_alpha = 0
        self.flash_col = None
        self.particles = []  # [{x, y, vx, vy, ttl, color}, ...]

        # Construir botones
        self._build_buttons()

        # Mensaje de instrucción (aparece al inicio)
        self.hint_t = 5.0  # 5 segundos de tutorial

    def _generate_chests(self):
        """Coloca 3 cofres en posiciones aleatorias pero no sobre Luki."""
        self.chests = []
        sx, sy = self.start_pos
        attempts = 0
        while len(self.chests) < 3 and attempts < 50:
            attempts += 1
            cx = random.randint(2, self.cells - 3)
            cy = random.randint(2, self.cells - 3)
            # no poner cofre cerca de Luki
            if abs(cx - sx) < 3 and abs(cy - sy) < 3:
                continue
            # no superponer con otro cofre
            if any(abs(cx - c["x"]) < 2 and abs(cy - c["y"]) < 2 for c in self.chests):
                continue
            self.chests.append({
                "x": cx, "y": cy,
                "opened": False,
                "open_t": 0.0,
            })

    def _build_buttons(self):
        """Construye la botonera lateral estilo terminal."""
        W, H = self.W, self.H
        px = self.canvas_rect.right + int(W * 0.015)
        pw = self.panel_w - int(W * 0.03)
        py = self.header_h + int(H * 0.02)

        bh = int(H * 0.10)
        gap = int(H * 0.012)

        # Botones direccionales
        self.btn_fd = TermButton((px, py, pw, bh),
                                  "ADELANTE", PAL["green"], self.fonts["btn"], icon="▲")
        py += bh + gap
        # Fila: izquierda - derecha
        half = (pw - gap) // 2
        self.btn_lt = TermButton((px, py, half, bh),
                                  "IZQ", PAL["cyan"], self.fonts["btn"], icon="◀")
        self.btn_rt = TermButton((px + half + gap, py, half, bh),
                                  "DER", PAL["cyan"], self.fonts["btn"], icon="▶")
        py += bh + gap

        # Botón de color (cicla entre los colores)
        bh2 = int(H * 0.085)
        self.btn_color = TermButton((px, py, pw, bh2),
                                     INK_COLORS[0][0],
                                     INK_COLORS[0][1],
                                     self.fonts["btn"], icon="🎨")
        py += bh2 + gap

        # Deshacer + borrar
        self.btn_undo = TermButton((px, py, half, bh2),
                                    "DESH", PAL["amber"], self.fonts["btn"], icon="↶")
        self.btn_clear = TermButton((px + half + gap, py, half, bh2),
                                     "BORRAR", PAL["red"], self.fonts["btn"], icon="✖")
        py += bh2 + gap

        # Volver (home)
        self.btn_home = TermButton((px, py, pw, int(bh2 * 0.75)),
                                    "INICIO", PAL["grey"], self.fonts["small"], icon="⌂")

        self.buttons = [
            self.btn_fd, self.btn_lt, self.btn_rt,
            self.btn_color, self.btn_undo, self.btn_clear,
            self.btn_home
        ]

    def _save_state(self):
        """Guarda el estado actual en el historial (para deshacer)."""
        state = {
            "fx": self.frog_x, "fy": self.frog_y,
            "angle": self.frog_angle,
            "trails": list(self.trail_segments),
            "chests": [dict(c) for c in self.chests],
            "opened": self.chests_opened,
        }
        self.history.append(state)
        # Limitar historial a 30 pasos
        if len(self.history) > 30:
            self.history.pop(0)

    def _undo(self):
        if not self.history:
            sfx.err()
            return
        state = self.history.pop()
        self.frog_x = state["fx"]
        self.frog_y = state["fy"]
        self.frog_angle = state["angle"]
        self.trail_segments = state["trails"]
        self.chests = state["chests"]
        self.chests_opened = state["opened"]
        sfx.turn()

    def _clear(self):
        """Resetea todo."""
        self._save_state()
        self.trail_segments = []
        self.frog_x = float(self.start_pos[0])
        self.frog_y = float(self.start_pos[1])
        self.frog_angle = 0
        self.chests_opened = 0
        self._generate_chests()
        sfx.clear_sfx()
        self.flash_col = PAL["cyan"]
        self.flash_alpha = 60

    def _move_forward(self):
        """Avanza una celda en la dirección actual."""
        self._save_state()
        dx = round(math.sin(math.radians(self.frog_angle)))
        dy = -round(math.cos(math.radians(self.frog_angle)))
        new_x = max(0, min(self.cells - 1, self.frog_x + dx))
        new_y = max(0, min(self.cells - 1, self.frog_y + dy))

        if new_x == self.frog_x and new_y == self.frog_y:
            # No se movió (pared)
            sfx.err()
            self.flash_col = PAL["red"]
            self.flash_alpha = 80
            self.history.pop()  # No guardar estado si no pasó nada
            return

        # agregar segmento de rastro
        x1, y1 = int(self.frog_x), int(self.frog_y)
        x2, y2 = int(new_x), int(new_y)
        color = INK_COLORS[self.color_idx][1]
        self.trail_segments.append((x1, y1, x2, y2, color))

        self.frog_x = new_x
        self.frog_y = new_y

        sfx.move()
        self.flash_col = PAL["green"]
        self.flash_alpha = 50

        self._check_chests()

    def _turn(self, delta):
        """Gira 90° a izquierda (-90) o derecha (+90)."""
        self._save_state()
        self.frog_angle = (self.frog_angle + delta) % 360
        sfx.turn()

    def _cycle_color(self):
        self.color_idx = (self.color_idx + 1) % len(INK_COLORS)
        name, color = INK_COLORS[self.color_idx]
        self.btn_color.label = name
        self.btn_color.color = color

    def _check_chests(self):
        """Un cofre se abre si Luki lo toca o está rodeado por el rastro."""
        trail_points = set()
        for (x1, y1, x2, y2, _) in self.trail_segments:
            trail_points.add((x1, y1))
            trail_points.add((x2, y2))

        fx, fy = int(self.frog_x), int(self.frog_y)

        for chest in self.chests:
            if chest["opened"]:
                continue
            cx, cy = chest["x"], chest["y"]

            # Condición 1: Luki está sobre el cofre
            touched = (fx == cx and fy == cy)

            # Condición 2: el rastro pasa por al menos 3 celdas adyacentes al cofre
            neighbors = [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]
            near_count = sum(1 for n in neighbors if n in trail_points)

            if touched or near_count >= 3:
                chest["opened"] = True
                chest["open_t"] = 0.0
                self.chests_opened += 1
                self._burst_particles(cx, cy)
                sfx.chest()

    def _burst_particles(self, cell_x, cell_y):
        """Explosión de estrellitas al abrir cofre."""
        cr = self.canvas_rect
        px = cr.x + cell_x * self.CELL + self.CELL // 2
        py = cr.y + cell_y * self.CELL + self.CELL // 2
        for _ in range(18):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 200)
            self.particles.append({
                "x": px, "y": py,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 50,
                "ttl": random.uniform(0.6, 1.2),
                "ttl_max": 1.2,
                "color": random.choice([PAL["yellow"], PAL["gold"], PAL["amber"]]),
                "size": random.randint(3, 6),
            })

    def handle(self, ev):
        if self.btn_fd.handle(ev):
            self._move_forward()
        elif self.btn_lt.handle(ev):
            self._turn(-90)
        elif self.btn_rt.handle(ev):
            self._turn(90)
        elif self.btn_color.handle(ev):
            self._cycle_color()
        elif self.btn_undo.handle(ev):
            self._undo()
        elif self.btn_clear.handle(ev):
            self._clear()
        elif self.btn_home.handle(ev):
            self.done = True

    def update(self, dt):
        self.t += dt
        for b in self.buttons:
            b.update()

        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 6)

        # Animación de apertura de cofres
        for chest in self.chests:
            if chest["opened"] and chest["open_t"] < 1.0:
                chest["open_t"] = min(1.0, chest["open_t"] + dt * 2.5)

        # Partículas
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 220 * dt  # gravedad
            p["ttl"] -= dt
        self.particles = [p for p in self.particles if p["ttl"] > 0]

        # Hint decrece
        if self.hint_t > 0:
            self.hint_t -= dt

    def draw(self, surf):
        surf.fill(PAL["bg"])
        draw_grid(surf, PAL["grid"])
        W, H = self.W, self.H

        # ── HEADER ─────────────────────────────────────────
        header_rect = pygame.Rect(0, 0, W, self.header_h)
        pygame.draw.rect(surf, PAL["bg_deep"], header_rect)
        pygame.draw.line(surf, PAL["border"],
                         (0, self.header_h), (W, self.header_h), 2)

        # Título izquierda
        render_text(surf, "★ LUKI DRAW",
                    14, int(self.header_h * 0.25),
                    self.fonts["sub"], PAL["cyan"])

        # Contador de cofres (centro)
        total = len(self.chests)
        render_text(surf, f"COFRES: {self.chests_opened}/{total}",
                    W // 2, int(self.header_h * 0.20),
                    self.fonts["sub"], PAL["yellow"], center=True)
        # barra de progreso de cofres
        bar_w = int(W * 0.18)
        bar_x = W // 2 - bar_w // 2
        bar_y = int(self.header_h * 0.65)
        pct = self.chests_opened / total if total > 0 else 0
        draw_progress_bar(surf, bar_x, bar_y, bar_w, 8,
                          pct, PAL["yellow"], PAL["grey_d"], segments=total or 1)

        # Color actual (derecha)
        cname, ccol = INK_COLORS[self.color_idx]
        col_x = W - 180
        pygame.draw.rect(surf, ccol,
                         (col_x, int(self.header_h * 0.3), 22, 22))
        pygame.draw.rect(surf, PAL["white"],
                         (col_x, int(self.header_h * 0.3), 22, 22), 2)
        render_text(surf, f"TINTA: {cname}",
                    col_x + 30, int(self.header_h * 0.35),
                    self.fonts["small"], ccol)

        # ── CANVAS ─────────────────────────────────────────
        cr = self.canvas_rect
        pygame.draw.rect(surf, PAL["bg_deep"], cr)
        draw_ascii_frame(surf, cr, PAL["border"], self.fonts["tiny"], "CANVAS")

        # Grilla interna
        for i in range(self.cells + 1):
            x = cr.x + i * self.CELL
            pygame.draw.line(surf, PAL["grid"],
                             (x, cr.y), (x, cr.y + cr.height), 1)
            y = cr.y + i * self.CELL
            pygame.draw.line(surf, PAL["grid"],
                             (cr.x, y), (cr.x + cr.width, y), 1)

        # RASTROS
        for (x1, y1, x2, y2, color) in self.trail_segments:
            px1 = cr.x + x1 * self.CELL + self.CELL // 2
            py1 = cr.y + y1 * self.CELL + self.CELL // 2
            px2 = cr.x + x2 * self.CELL + self.CELL // 2
            py2 = cr.y + y2 * self.CELL + self.CELL // 2
            pygame.draw.line(surf, color, (px1, py1), (px2, py2), 5)
            # punto en cada extremo
            pygame.draw.circle(surf, color, (px2, py2), 3)

        # COFRES
        for chest in self.chests:
            ccx = cr.x + chest["x"] * self.CELL + self.CELL // 2
            ccy = cr.y + chest["y"] * self.CELL - 6
            chest_size = int(self.CELL * 1.4)
            draw_chest(surf, ccx, ccy, size=chest_size,
                       open_progress=chest["open_t"], t=self.t)
            # Signo "?" flotante sobre cofres cerrados
            if not chest["opened"]:
                qb = int(math.sin(self.t * 3 + chest["x"]) * 4)
                draw_question_mark(surf, ccx, ccy - chest_size // 2 - 8,
                                   self.fonts["sub"], PAL["yellow"], bounce=qb)

        # PARTÍCULAS (estrellitas al abrir cofre)
        for p in self.particles:
            alpha_f = max(0, p["ttl"] / p["ttl_max"])
            size = int(p["size"] * alpha_f) + 1
            draw_star(surf, int(p["x"]), int(p["y"]), size=size, color=p["color"])

        # LUKI
        S = 4
        luki_cx = cr.x + int(self.frog_x) * self.CELL + self.CELL // 2 - 7 * S
        luki_cy = cr.y + int(self.frog_y) * self.CELL + self.CELL // 2 - 7 * S
        bounce = int(math.sin(self.t * 4) * 3)
        draw_luki(surf, luki_cx, luki_cy, S=S, bounce=bounce)

        # Flecha de dirección de Luki
        self._draw_direction_indicator(surf, luki_cx + 7 * S, luki_cy + 7 * S)

        # Halo alrededor de Luki
        glow_r = int(20 + 4 * math.sin(self.t * 3))
        pygame.draw.circle(surf, (80, 220, 110),
                           (luki_cx + 7 * S, luki_cy + 7 * S + bounce),
                           glow_r, 1)

        # Flash de feedback
        if self.flash_alpha > 0 and self.flash_col:
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((*self.flash_col, self.flash_alpha))
            surf.blit(flash, (0, 0))

        # ── PANEL DE BOTONES ───────────────────────────────
        for b in self.buttons:
            b.draw(surf)

        # ── MENSAJE DE AYUDA (tutorial inicial) ─────────────
        if self.hint_t > 0 and self.chests_opened == 0:
            alpha = min(220, int(self.hint_t * 80))
            hint_surf = pygame.Surface((int(W * 0.55), 60), pygame.SRCALPHA)
            hint_surf.fill((0, 0, 0, alpha))
            pygame.draw.rect(hint_surf, (*PAL["yellow"], alpha),
                             hint_surf.get_rect(), 2)
            hx = cr.x + (cr.width - hint_surf.get_width()) // 2
            hy = cr.y + 8
            surf.blit(hint_surf, (hx, hy))
            render_text(surf, "¡TOCA LOS COFRES CON EL RASTRO!",
                        hx + hint_surf.get_width() // 2, hy + 10,
                        self.fonts["small"], PAL["yellow"], center=True)
            render_text(surf, "Camina hasta ellos o rodéalos",
                        hx + hint_surf.get_width() // 2, hy + 32,
                        self.fonts["tiny"], PAL["white"], center=True)

        # ── CELEBRACIÓN SI TERMINÓ TODOS LOS COFRES ─────────
        if self.chests_opened >= len(self.chests) and len(self.chests) > 0:
            pulse = abs(math.sin(self.t * 4))
            col = (
                int(PAL["yellow"][0] * pulse + PAL["gold"][0] * (1 - pulse)),
                int(PAL["yellow"][1] * pulse + PAL["gold"][1] * (1 - pulse)),
                int(PAL["yellow"][2] * pulse + PAL["gold"][2] * (1 - pulse)),
            )
            render_text(surf, "★ ¡LO LOGRASTE! ★",
                        cr.centerx, cr.y - 4,
                        self.fonts["title"], col, center=True, shadow=True)

        # ── FOOTER ─────────────────────────────────────────
        foot_y = H - self.footer_h
        pygame.draw.line(surf, PAL["border_d"], (0, foot_y), (W, foot_y), 2)
        render_text(surf, f"X:{int(self.frog_x):02d}  Y:{int(self.frog_y):02d}  "
                          f"DIR:{int(self.frog_angle):03d}°",
                    14, foot_y + int(self.footer_h * 0.25),
                    self.fonts["small"], PAL["cyan"])
        render_text(surf, "─── KINDER LABS · LUKI DRAW ───",
                    W - 14, foot_y + int(self.footer_h * 0.25),
                    self.fonts["small"], PAL["grey"])
        # alinear derecha
        right_txt = self.fonts["small"].render(
            "─── KINDER LABS · LUKI DRAW ───", True, PAL["grey"])
        surf.blit(right_txt, (W - right_txt.get_width() - 14,
                              foot_y + int(self.footer_h * 0.25)))

    def _draw_direction_indicator(self, surf, cx, cy):
        """Flecha pequeña indicando a dónde mira Luki."""
        rad = math.radians(self.frog_angle)
        dx = math.sin(rad)
        dy = -math.cos(rad)
        tip_x = int(cx + dx * 24)
        tip_y = int(cy + dy * 24)
        # línea
        pygame.draw.line(surf, PAL["yellow"],
                         (cx, cy), (tip_x, tip_y), 2)
        # punta
        perp_x = -dy
        perp_y = dx
        p1 = (tip_x - int(dx * 6) + int(perp_x * 4),
              tip_y - int(dy * 6) + int(perp_y * 4))
        p2 = (tip_x - int(dx * 6) - int(perp_x * 4),
              tip_y - int(dy * 6) - int(perp_y * 4))
        pygame.draw.polygon(surf, PAL["yellow"], [(tip_x, tip_y), p1, p2])


# ==================================================================
# FUENTES
# ==================================================================
def load_fonts(W, H):
    base = max(12, W // 60)
    try:
        return {
            "title": pygame.font.SysFont("monospace", int(base * 2.4), bold=True),
            "sub":   pygame.font.SysFont("monospace", int(base * 1.5), bold=True),
            "btn":   pygame.font.SysFont("monospace", int(base * 1.3), bold=True),
            "small": pygame.font.SysFont("monospace", int(base * 1.0), bold=True),
            "tiny":  pygame.font.SysFont("monospace", int(base * 0.8)),
        }
    except Exception:
        f = pygame.font.Font(None, int(base * 2))
        return {k: f for k in ("title", "sub", "btn", "small", "tiny")}

# ==================================================================
# APP PRINCIPAL
# ==================================================================
class App:
    def __init__(self):
        pygame.init()
        sfx.init()

        if ANDROID:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(get_screen_size())

        pygame.display.set_caption("🐸 Kinder Labs · Luki Draw")
        self.clock = pygame.time.Clock()
        self.W, self.H = self.screen.get_size()
        self.fonts = load_fonts(self.W, self.H)

        self._go_welcome()

    def _go_welcome(self):
        self.scene = "welcome"
        self.screen_obj = WelcomeScreen(self.fonts, self.W, self.H)

    def _go_draw(self):
        self.scene = "draw"
        self.screen_obj = DrawScreen(self.fonts, self.W, self.H)

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                self.screen_obj.handle(ev)

            self.screen_obj.update(dt)

            if self.screen_obj.done:
                if self.scene == "welcome":
                    self._go_draw()
                elif self.scene == "draw":
                    self._go_welcome()

            self.screen_obj.draw(self.screen)

            # ── SCANLINES CRT (sutil) ─────────────
            W, H = self.W, self.H
            scan = pygame.Surface((W, H), pygame.SRCALPHA)
            for y in range(0, H, 3):
                pygame.draw.line(scan, (0, 0, 0, 24), (0, y), (W, y))
            self.screen.blit(scan, (0, 0))

            pygame.display.flip()

# ==================================================================
# ENTRY POINT
# ==================================================================
if __name__ == "__main__":
    App().run()
