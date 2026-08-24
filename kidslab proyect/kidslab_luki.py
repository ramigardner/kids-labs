"""
KidsLab — LUKI EDITION  🐸
Versión Android táctil para Lucas (6 años)
- Sin teclado — todo botones grandes
- Luki la ranita desde el inicio
- 2 niveles: Adelante / Giros
- Sin internet, sin rival, sin reloj
- Estética Commodore 64
- Buildozer / Android 8+ / Tablet 10"
"""

import pygame
import sys
import math
import random
import array

# ==================================================================
# DETECCIÓN DE PLATAFORMA
# ==================================================================
import os
ANDROID = os.environ.get("ANDROID_ARGUMENT") is not None or \
          os.environ.get("ANDROID_ROOT") is not None

# ==================================================================
# NIVELES  (5 para Lucas — progresivos y divertidos)
# ==================================================================
LEVELS = [
    {
        "id": 1,
        "titulo": "¡Adelante!",
        "emoji":  "➡️",
        "concepto": "Tocá ADELANTE para mover a Luki",
        "color": (100, 220, 100),
        "pasos": [
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2"},
            {"cmd": "FD 3", "action": ("fd", 3), "desc": "Adelante 3"},
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2 más"},
        ]
    },
    {
        "id": 2,
        "titulo": "¡Giramos!",
        "emoji":  "🔄",
        "concepto": "Adelante, giro a derecha, adelante",
        "color": (100, 180, 255),
        "pasos": [
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2"},
            {"cmd": "RT 90","action": ("rt", 90),"desc": "Girá a la derecha"},
            {"cmd": "FD 3", "action": ("fd", 3), "desc": "Adelante 3"},
            {"cmd": "RT 90","action": ("rt", 90),"desc": "Girá derecha otra vez"},
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2"},
        ]
    },
    {
        "id": 3,
        "titulo": "¡El Cuadrado!",
        "emoji":  "⬛",
        "concepto": "Luki dibuja un cuadrado perfecto",
        "color": (255, 180, 80),
        "pasos": [
            {"cmd": "FD 4", "action": ("fd", 4), "desc": "Adelante 4"},
            {"cmd": "RT 90","action": ("rt", 90),"desc": "Gira derecha"},
            {"cmd": "FD 4", "action": ("fd", 4), "desc": "Adelante 4"},
            {"cmd": "RT 90","action": ("rt", 90),"desc": "Gira derecha"},
            {"cmd": "FD 4", "action": ("fd", 4), "desc": "Adelante 4"},
            {"cmd": "RT 90","action": ("rt", 90),"desc": "Gira derecha"},
            {"cmd": "FD 4", "action": ("fd", 4), "desc": "Adelante 4 - ¡cerramos!"},
        ]
    },
    {
        "id": 4,
        "titulo": "¡El Triángulo!",
        "emoji":  "🔺",
        "concepto": "Ahora a Luki le toca dibujar un triángulo",
        "color": (255, 100, 150),
        "pasos": [
            {"cmd": "FD 5", "action": ("fd", 5), "desc": "Adelante 5"},
            {"cmd": "RT 120","action": ("rt", 120),"desc": "Gira 120°"},
            {"cmd": "FD 5", "action": ("fd", 5), "desc": "Adelante 5"},
            {"cmd": "RT 120","action": ("rt", 120),"desc": "Gira 120°"},
            {"cmd": "FD 5", "action": ("fd", 5), "desc": "Adelante 5 - ¡triángulo!"},
        ]
    },
    {
        "id": 5,
        "titulo": "¡Camino Secreto!",
        "emoji":  "🌀",
        "concepto": "Un camino complicado con giros y trucos",
        "color": (200, 80, 255),
        "pasos": [
            {"cmd": "FD 3", "action": ("fd", 3), "desc": "Adelante 3"},
            {"cmd": "RT 90","action": ("rt", 90),"desc": "Gira derecha"},
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2"},
            {"cmd": "LT 90","action": ("lt", 90),"desc": "Gira izquierda"},
            {"cmd": "FD 3", "action": ("fd", 3), "desc": "Adelante 3"},
            {"cmd": "RT 90","action": ("rt", 90),"desc": "Gira derecha"},
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2"},
            {"cmd": "LT 90","action": ("lt", 90),"desc": "Gira izquierda"},
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2 - ¡listo!"},
        ]
    },
]

# ==================================================================
# COLORES  C64
# ==================================================================
C64 = {
    "bg":       (16,  16,  64),
    "grid":     (28,  28,  88),
    "border":   (100, 100, 255),
    "white":    (255, 255, 240),
    "cyan":     (84,  255, 255),
    "yellow":   (240, 240, 80),
    "green":    (112, 255, 112),
    "red":      (255,  80,  80),
    "grey":     (128, 128, 192),
    "black":    (0,   0,   0),
    "orange":   (255, 160,  40),
}

# ==================================================================
# MASCOTAS DESBLOQUEABLES (1 por cada 5 estrellas)
# ==================================================================
PETS = [
    {"emoji": "🐧", "name": "Pinguino", "power": "Anda rápido en el hielo"},
    {"emoji": "🐬", "name": "Delfín", "power": "Salta sobre el agua"},
    {"emoji": "🦉", "name": "Búho", "power": "Ve en la oscuridad"},
    {"emoji": "🦋", "name": "Mariposa", "power": "Vuela entre las flores"},
    {"emoji": "🐝", "name": "Abejita", "power": "Toca la miel"},
]

# ==================================================================
# SONIDO  (onda cuadrada, sin archivos externos)
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
            t  = [i / sr for i in range(n)]
            wave = array.array("h", [
                int(((1 if (i * freq / sr) % 1 < 0.5 else -1) *
                     vol * 32767 *
                     (1 - i / n))            # fade out
                    )
                for i in range(n)
            ])
            stereo = array.array("h")
            for s in wave:
                stereo.append(s)
                stereo.append(s)
            snd = pygame.sndarray.make_sound(
                __import__("numpy").frombuffer(stereo, dtype="int16")
                .reshape(-1, 2)
            )
            snd.play()
        except Exception:
            pass

    def ok_sound(self):   self.beep(523, 100, 0.12)   # pastel
    def win_sound(self):
        self.beep(659, 120, 0.15)   # pastel
        pygame.time.delay(80)
        self.beep(784, 160, 0.15)   # pastel
    def err_sound(self):  self.beep(392, 100, 0.10)   # pastel
    def tap_sound(self):  self.beep(587, 50, 0.08)    # pastel
    def chest_sound(self): self.beep(698, 200, 0.2)   # sonido de cofre abierto

sfx = SFX()

# ==================================================================
# PANTALLA  — adaptada a tablet 10" landscape
# ==================================================================
def get_screen_size():
    if ANDROID:
        info = pygame.display.Info()
        return info.current_w, info.current_h
    return 1024, 640          # debug en PC

# ==================================================================
# UTILIDADES DE DIBUJO
# ==================================================================
def draw_grid(surf, color, size=32):
    w, h = surf.get_size()
    for x in range(0, w, size):
        pygame.draw.line(surf, color, (x, 0), (x, h))
    for y in range(0, h, size):
        pygame.draw.line(surf, color, (0, y), (w, y))

def draw_rect_border(surf, rect, color, width=3, fill=None):
    if fill:
        pygame.draw.rect(surf, fill, rect)
    pygame.draw.rect(surf, color, rect, width)

def render_text(surf, text, x, y, font, color, center=False):
    s = font.render(str(text), True, color)
    if center:
        x -= s.get_width() // 2
    surf.blit(s, (x, y))

def draw_arrow(surf, x, y, direction, size=40, color=(255, 255, 0), alpha=255):
    """Dibuja una flecha animada luminosa.
    direction: 0=arriba, 1=derecha, 2=abajo, 3=izquierda
    """
    arrow = pygame.Surface((size, size), pygame.SRCALPHA)
    col = (*color, alpha)
    
    # Punta de flecha
    points = {
        0: [(size//2, 0), (0, size), (size, size)],           # arriba
        1: [(size, size//2), (0, 0), (0, size)],              # derecha
        2: [(size//2, size), (0, 0), (size, 0)],              # abajo
        3: [(0, size//2), (size, 0), (size, size)],           # izquierda
    }
    pygame.draw.polygon(arrow, col, points.get(direction, []))
    
    # Brillo blanco
    glow_col = (255, 255, 255, int(alpha * 0.5))
    pygame.draw.polygon(arrow, glow_col, points.get(direction, []), 3)
    
    surf.blit(arrow, (x - size//2, y - size//2))

# ==================================================================
# RANA  (pixel art en canvas pygame)
# ==================================================================
FROG_PIXELS = [
    # (col, fila, color_key)
    # cuerpo
    *[((4+i), 2, "body") for i in range(7)],
    *[((3+i), 3, "body") for i in range(9)],
    *[((3+i), 4, "body") for i in range(9)],
    *[((3+i), 5, "body") for i in range(9)],
    # ojos
    (4, 3, "eye"), (5, 3, "eye"), (9, 3, "eye"), (10, 3, "eye"),
    # boca sonriente
    (5, 5, "dark"), (6, 5, "mouth"), (7, 5, "mouth"), (8, 5, "mouth"), (9, 5, "dark"),
    # panza
    *[((3+i), 6, "body") for i in range(9)],
    *[((2+i), 7, "body") for i in range(11)],
    *[((2+i), 8, "body") for i in range(11)],
    *[((2+i), 9, "body") for i in range(11)],
    *[((3+i),10, "body") for i in range(9)],
    # patas
    (2,11,"dark"),(3,11,"dark"),(4,11,"dark"),
    (9,11,"dark"),(10,11,"dark"),(11,11,"dark"),
    (1,12,"dark"),(2,12,"dark"),(3,12,"dark"),(4,12,"dark"),
    (10,12,"dark"),(11,12,"dark"),(12,12,"dark"),
    # manitos
    (1, 9,"light"),(2, 9,"light"),(13,9,"light"),(12,9,"light"),
    # coronita de Luki
    (5,0,"crown"),(6,0,"crown"),(7,0,"crown"),(8,0,"crown"),(9,0,"crown"),
    (4,1,"crown"),(10,1,"crown"),
    (5,1,"star"),(7,1,"star"),(9,1,"star"),
]

def draw_luki(surf, x, y, S=8, bounce=0):
    """Dibuja a Luki con pixel art en posición (x,y), S=tamaño de pixel."""
    palette = {
        "body":  (80, 200, 100),
        "dark":  (30, 130, 60),
        "light": (140, 255, 160),
        "eye":   (255, 220, 50),
        "mouth": (20, 100, 40),
        "crown": (240, 200, 0),
        "star":  (255, 255, 100),
    }
    for (col, row, key) in FROG_PIXELS:
        color = palette.get(key, (0, 200, 0))
        pygame.draw.rect(surf, color,
                         (x + col * S, y + row * S + bounce, S, S))

# ==================================================================
# BOTÓN TÁCTIL
# ==================================================================
class TouchButton:
    def __init__(self, rect, label, color, font, emoji=""):
        self.rect   = pygame.Rect(rect)
        self.label  = label
        self.color  = color
        self.font   = font
        self.emoji  = emoji
        self.pressed = False
        self._press_t = 0

    def handle(self, ev):
        """Devuelve True si fue tocado/clickeado."""
        if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if ev.type == pygame.FINGERDOWN:
                W, H = pygame.display.get_surface().get_size()
                pos = (int(ev.x * W), int(ev.y * H))
            else:
                pos = ev.pos
            if self.rect.collidepoint(pos):
                self.pressed = True
                self._press_t = 8
                sfx.tap_sound()
                return True
        return False

    def update(self):
        if self._press_t > 0:
            self._press_t -= 1
        else:
            self.pressed = False

    def draw(self, surf):
        r = self.rect.inflate(-6, -6) if self.pressed else self.rect
        # sombra dinamica
        shadow = r.move(5 + (2 if self.pressed else 0), 5 + (2 if self.pressed else 0))
        pygame.draw.rect(surf, (0, 0, 0), shadow, border_radius=14)
        # fondo
        pygame.draw.rect(surf, self.color, r, border_radius=14)
        # borde blanco grueso
        pygame.draw.rect(surf, C64["white"], r, 4, border_radius=14)
        # pequeña esquinita brillante
        for corner in [r.topleft, (r.right-6, r.top), r.bottomleft, (r.right-6, r.bottom-6)]:
            pygame.draw.rect(surf, (255, 255, 255), (*corner, 3, 3))
        # texto con sombra
        txt_shadow = self.font.render(self.label, True, (0, 0, 0))
        tx_s = r.centerx - txt_shadow.get_width() // 2
        ty_s = r.centery - txt_shadow.get_height() // 2
        surf.blit(txt_shadow, (tx_s + 2, ty_s + 2))
        # texto principal
        txt = self.font.render(self.label, True, C64["black"])
        tx  = r.centerx - txt.get_width() // 2
        ty  = r.centery - txt.get_height() // 2
        surf.blit(txt, (tx, ty))

# ==================================================================
# PANTALLA DE BIENVENIDA
# ==================================================================
class WelcomeScreen:
    def __init__(self, fonts, W, H):
        self.fonts = fonts
        self.W, self.H = W, H
        self.done = False
        self.t    = 0.0
        btn_w, btn_h = int(W * 0.5), int(H * 0.15)  # mas grande
        self.btn = TouchButton(
            ((W - btn_w) // 2, int(H * 0.70), btn_w, btn_h),
            "¡VAMOS A JUGAR!",
            C64["green"],
            fonts["btn"],
        )

    def handle(self, ev):
        if self.btn.handle(ev):
            self.done = True

    def update(self, dt):
        self.t += dt
        self.btn.update()

    def draw(self, surf):
        surf.fill(C64["bg"])
        draw_grid(surf, C64["grid"])
        W, H = self.W, self.H

        # Luki animado
        bounce = int(math.sin(self.t * 3) * 6)
        S = max(6, W // 90)
        luki_w = 14 * S
        draw_luki(surf, W // 2 - luki_w // 2, int(H * 0.05), S=S, bounce=bounce)

        # Título personalizado para Lucas
        render_text(surf, "👋 Lucas 👋", W // 2, int(H * 0.35),
                    self.fonts["title"], C64["yellow"], center=True)
        render_text(surf, "🐸 🎮 📖", W // 2, int(H * 0.50),
                    self.fonts["title"], C64["cyan"], center=True)
        render_text(surf, "Luki te espera", W // 2, int(H * 0.62),
                    self.fonts["sub"], C64["green"], center=True)

        self.btn.draw(surf)

        # versión
        render_text(surf, "KIDSLAB · LUKI EDITION", W // 2, H - 24,
                    self.fonts["tiny"], C64["grey"], center=True)

# ==================================================================
# PANTALLA DE JUEGO
# ==================================================================
class GameScreen:
    CELL = 28  # tamaño de celda del grid lógico

    def __init__(self, fonts, W, H):
        self.fonts = fonts
        self.W, self.H = W, H
        self.done  = False
        self.won   = False
        self.t     = 0.0
        self.flash_col   = None
        self.flash_alpha = 0

        # posición lógica de Luki en el grid
        self.frog_x = 3.0
        self.frog_y = 3.0
        self.frog_angle = 0.0   # 0=arriba, 90=derecha, etc.
        self.trail  = [(3, 3)]
        
        # Sorpresas random
        self.surprises = []  # [(x, y, emoji, ttl), ...]

        # área del canvas - PRIMERO
        canvas_size = min(int(W * 0.70), int(H * 0.75))
        self.canvas_rect = pygame.Rect(
            int((W - canvas_size) // 2),
            int(H * 0.12),
            canvas_size, canvas_size
        )
        self.cells = canvas_size // self.CELL
        
        # Cofres - DESPUÉS de definir self.cells
        self.chests = []  # [{x, y, opened=False, opening_t=0}, ...]
        self._generate_chests()
        
        # Flechitas para las direcciones
        self._build_arrows()

    def _build_buttons(self):
        W, H = self.W, self.H
        # zona de botones: mitad derecha
        bx = int(W * 0.55)
        bw = int(W * 0.20)
        bh = int(H * 0.15)
        gap = int(H * 0.03)

        cy = int(H * 0.18)

        # comandos disponibles según nivel
        cmds = [p["cmd"] for p in self.pasos]
        unique_cmds = []
        seen = set()
        for c in cmds:
            base = c.split()[0]
            if base not in seen:
                unique_cmds.append(base)
                seen.add(base)

        btn_colors = {
            "FD":  (80, 255, 120),   # verde brillante
            "RT":  (100, 200, 255),  # azul
            "LT":  (255, 200, 80),   # naranja
            "BK":  (255, 120, 120),  # rojo
        }
        btn_labels = {
            "FD": "ADELANTE ➡️",
            "RT": "DERECHA ↻",
            "LT": "IZQUIERDA ↺",
            "BK": "ATRÁS ←",
        }

        self.buttons = []
        for cmd in unique_cmds:
            label = btn_labels.get(cmd, cmd)
            color = btn_colors.get(cmd, C64["white"])
            btn_width = bw * 2.2 - int(W * 0.02)  # mas anchos
            btn_height = int(bh * 1.15)  # mas altos
            self.buttons.append(TouchButton(
                (bx - int(W * 0.05), cy, btn_width, btn_height),
                label, color, self.fonts["btn"]
            ))
            cy += btn_height + int(gap * 1.3)

        # panel de pasos (solo visual, debajo de botones)
        self.steps_y = cy + gap

    def _build_arrows(self):
        """Construye flechitas animadas para modo libre."""
        W, H = self.W, self.H
        # 4 flechitas en forma de cruz, a la derecha del canvas
        arrow_x = int(W * 0.75)
        arrow_y = int(H * 0.50)
        spacing = int(H * 0.12)
        
        self.arrows = {
            "up":    {"pos": (arrow_x, arrow_y - spacing), "dir": 0},  # ↑
            "right": {"pos": (arrow_x + spacing, arrow_y), "dir": 1},  # →
            "down":  {"pos": (arrow_x, arrow_y + spacing), "dir": 2},  # ↓
            "left":  {"pos": (arrow_x - spacing, arrow_y), "dir": 3},  # ←
        }
        self.arrow_size = int(H * 0.08)

    def _generate_chests(self):
        """Genera cofres aleatorios en el canvas."""
        num_chests = random.randint(2, 4)
        for _ in range(num_chests):
            cx = random.randint(1, self.cells - 2)
            cy = random.randint(1, self.cells - 2)
            self.chests.append({"x": cx, "y": cy, "opened": False, "opening_t": 0.0})

    def _check_chest_enclosed(self, chest):
        """Detecta si un cofre fue envuelto por el rastro de Luki."""
        # Verificar si el cofre está rodeado por el rastro
        cx, cy = chest["x"], chest["y"]
        trail_points = set(self.trail)
        
        # Buscar puntos alrededor del cofre
        neighbors = [
            (cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1),
            (cx-1, cy-1), (cx+1, cy-1), (cx-1, cy+1), (cx+1, cy+1)
        ]
        
        # Si al menos 4 de los 8 vecinos están en el rastro, se considera envuelto
        enclosed_count = sum(1 for n in neighbors if n in trail_points)
        return enclosed_count >= 4

    def _move_frog(self, cmd):
        """Mueve la rana según comando (FD, RT, LT, BK)."""
        action_map = {
            "FD": ("fd", 1),
            "RT": ("rt", 90),
            "LT": ("lt", 90),
            "BK": ("bk", 1),
        }
        if cmd not in action_map:
            return
        
        action, val = action_map[cmd]
        
        if action == "fd":
            dx = round(math.sin(math.radians(self.frog_angle)))
            dy = -round(math.cos(math.radians(self.frog_angle)))
            self.frog_x = max(0, min(self.cells - 1, self.frog_x + dx * val))
            self.frog_y = max(0, min(self.cells - 1, self.frog_y + dy * val))
        elif action == "bk":
            dx = round(math.sin(math.radians(self.frog_angle)))
            dy = -round(math.cos(math.radians(self.frog_angle)))
            self.frog_x = max(0, min(self.cells - 1, self.frog_x - dx * val))
            self.frog_y = max(0, min(self.cells - 1, self.frog_y - dy * val))
        elif action == "rt":
            self.frog_angle = (self.frog_angle + val) % 360
        elif action == "lt":
            self.frog_angle = (self.frog_angle - val) % 360
        
        self.trail.append((self.frog_x, self.frog_y))
        sfx.ok_sound()
        self.flash_col   = C64["green"]
        self.flash_alpha = 80
        
        # Agregar sorpresas random
        if random.random() < 0.3:
            surp_emojis = ["🌟", "✨", "🎈", "🎊", "💫", "⭐", "🌺", "🦋", "🐝", "🐞"]
            surp_x = random.randint(0, self.cells - 1)
            surp_y = random.randint(0, self.cells - 1)
            surp = {
                "x": surp_x,
                "y": surp_y,
                "emoji": random.choice(surp_emojis),
                "ttl": 2.0,
                "angle": random.uniform(0, 360)
            }
            self.surprises.append(surp)
        
        # Verificar si algún cofre fue envuelto
        for chest in self.chests:
            if not chest["opened"] and self._check_chest_enclosed(chest):
                chest["opened"] = True
                chest["opening_t"] = 0.5  # Duración de la animación
                sfx.chest_sound()  # Sonido pastel cuando se abre

    def handle(self, ev):
        """Detecta toques en las flechitas."""
        if ev.type == pygame.MOUSEBUTTONDOWN or (hasattr(ev, 'type') and ev.type in (pygame.FINGERDOWN, pygame.FINGERUP)):
            if ev.type == pygame.MOUSEBUTTONDOWN:
                pos = ev.pos
            else:
                pos = (int(ev.x * self.W), int(ev.y * self.H))
            
            # Detectar cuál flecha fue tocada
            for arrow_name, arrow_data in self.arrows.items():
                ax, ay = arrow_data["pos"]
                if abs(pos[0] - ax) < self.arrow_size and abs(pos[1] - ay) < self.arrow_size:
                    cmd_map = {"up": "FD", "right": "RT", "down": "BK", "left": "LT"}
                    self._move_frog(cmd_map[arrow_name])

    def update(self, dt):
        self.t += dt
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 6)
        
        # Actualizar sorpresas
        self.surprises = [s for s in self.surprises if s["ttl"] > 0]
        for s in self.surprises:
            s["ttl"] -= dt
        
        # Actualizar cofres
        for chest in self.chests:
            if chest["opened"] and chest["opening_t"] > 0:
                chest["opening_t"] -= dt

    def draw(self, surf):
        surf.fill(C64["bg"])
        W, H = self.W, self.H

        # Grid de fondo
        draw_grid(surf, C64["grid"])

        # ── Título simple ──────────────────────────────────────────────
        render_text(surf, "🎨 DIBUJA CON LUKI 🎨", W // 2, 15,
                    self.fonts["sub"], C64["cyan"], center=True)

        # ── Canvas del juego ─────────────────────────────────────
        cr = self.canvas_rect

        # fondo del canvas
        pygame.draw.rect(surf, (8, 8, 32), cr, border_radius=8)
        draw_rect_border(surf, cr, C64["border"], 3)

        # grid del canvas
        for i in range(self.cells + 1):
            x = cr.x + i * self.CELL
            pygame.draw.line(surf, C64["grid"], (x, cr.y), (x, cr.y + cr.height))
        for i in range(self.cells + 1):
            y = cr.y + i * self.CELL
            pygame.draw.line(surf, C64["grid"], (cr.x, y), (cr.x + cr.width, y))

        # rastro de Luki
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                x1 = cr.x + int(self.trail[i][0]) * self.CELL + self.CELL // 2
                y1 = cr.y + int(self.trail[i][1]) * self.CELL + self.CELL // 2
                x2 = cr.x + int(self.trail[i+1][0]) * self.CELL + self.CELL // 2
                y2 = cr.y + int(self.trail[i+1][1]) * self.CELL + self.CELL // 2
                pygame.draw.line(surf, (80, 180, 80), (x1, y1), (x2, y2), 3)

        # Luki en el canvas
        S = 5
        luki_cx = cr.x + int(self.frog_x) * self.CELL + self.CELL // 2 - 7 * S
        luki_cy = cr.y + int(self.frog_y) * self.CELL + self.CELL // 2 - 7 * S
        bounce  = int(math.sin(self.t * 4) * 4)
        draw_luki(surf, luki_cx, luki_cy, S=S, bounce=bounce)
        # Brillo alrededor de Luki
        glow_r = int(25 + 8 * math.sin(self.t * 3))
        pygame.draw.circle(surf, (80, 200, 100),
                          (int(luki_cx + 7*S), int(luki_cy + 7*S + bounce)),
                          glow_r, 1)

        # Flash de feedback
        if self.flash_alpha > 0 and self.flash_col:
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((*self.flash_col, self.flash_alpha))
            surf.blit(flash, (0, 0))
        
        # ── Dibujar sorpresas ────────────────────────────────
        for surp in self.surprises:
            surp_alpha = int(255 * (surp["ttl"] / 2.0))  # fade out
            x = cr.x + int(surp["x"]) * self.CELL + self.CELL // 2
            y = cr.y + int(surp["y"]) * self.CELL + self.CELL // 2
            surp_surf = self.fonts["emoji"].render(surp["emoji"], True, (255, 255, 255))
            surp_surf.set_alpha(surp_alpha)
            bounce = int(math.sin(self.t * 4 + surp["angle"]) * 3)
            surf.blit(surp_surf, (x - surp_surf.get_width()//2, y - surp_surf.get_height()//2 + bounce))

        # ── Dibujar cofres ────────────────────────────────
        for chest in self.chests:
            cx = cr.x + int(chest["x"]) * self.CELL + self.CELL // 2
            cy = cr.y + int(chest["y"]) * self.CELL + self.CELL // 2
            chest_size = 20
            
            if chest["opened"]:
                # Cofre abierto con animación
                open_progress = 1.0 - (chest["opening_t"] / 0.5)  # de 0 a 1
                open_angle = open_progress * math.pi  # 0 a pi
                
                # Cuerpo del cofre
                pygame.draw.rect(surf, (200, 100, 50),
                               (cx - chest_size//2, cy, chest_size, int(chest_size * 0.6)))
                pygame.draw.rect(surf, C64["yellow"],
                               (cx - chest_size//2, cy, chest_size, int(chest_size * 0.6)), 2)
                
                # Tapa abriéndose
                lid_open = chest_size * 0.3 * math.sin(open_angle)
                pygame.draw.arc(surf, (200, 100, 50),
                               pygame.Rect(cx - chest_size//2, int(cy - lid_open),
                                          chest_size, chest_size//2),
                               math.pi, 2*math.pi, 2)
                
                # Resplandor de apertura
                glow = int(30 * (1 - open_progress))
                pygame.draw.circle(surf, (255, 255, 100, glow),
                                 (cx, cy - 5), glow, 1)
            else:
                # Cofre cerrado
                pygame.draw.rect(surf, (200, 100, 50),
                               (cx - chest_size//2, cy, chest_size, int(chest_size * 0.6)))
                pygame.draw.rect(surf, C64["yellow"],
                               (cx - chest_size//2, cy, chest_size, int(chest_size * 0.6)), 2)
                pygame.draw.rect(surf, (255, 200, 0),
                               (cx - chest_size//2 + 2, cy - 4, chest_size - 4, 3))

        # ── Flechitas animadas ─────────────────────────────────────────────
        pulse = int(math.sin(self.t * 4) * 20) + 80
        for arrow_name, arrow_data in self.arrows.items():
            ax, ay = arrow_data["pos"]
            direction = arrow_data["dir"]
            colors = [C64["green"], (100, 200, 255), (255, 200, 80), C64["red"]]
            draw_arrow(surf, ax, ay, direction, self.arrow_size, colors[direction], pulse)

# ==================================================================
# PANTALLA DE VICTORIA
# ==================================================================
class WinScreen:
    def __init__(self, fonts, W, H, level_index, progress_data=None):
        self.fonts = fonts
        self.W, self.H = W, H
        self.li   = level_index
        self.done = False
        self.t    = 0.0
        self.progress = progress_data or {"stars": 0, "unlocked_pets": []}
        self.new_star = True
        self.star_anim_t = 0.0
        self.stars = [(random.randint(0, W), random.randint(0, H),
                       random.choice(["⭐","🌟","✨"]),
                       random.uniform(0.5, 2.0)) for _ in range(12)]
        last = (level_index + 1) >= len(LEVELS)
        label = "¡FIN! 🏆" if last else "¡SIGUIENTE!"
        color = C64["yellow"] if last else C64["green"]
        bw, bh = int(W * 0.50), int(H * 0.15)
        self.btn = TouchButton(
            ((W - bw) // 2, int(H * 0.70), bw, bh),
            label, color, fonts["btn"]
        )
        self.is_last = last

    def handle(self, ev):
        if self.btn.handle(ev):
            self.done = True

    def update(self, dt):
        self.t += dt
        self.star_anim_t += dt
        self.btn.update()

    def draw(self, surf):
        surf.fill(C64["bg"])
        draw_grid(surf, C64["grid"])
        W, H = self.W, self.H

        # estrellas animadas
        font_e = self.fonts.get("emoji", self.fonts["sub"])
        for sx, sy, star, speed in self.stars:
            bounce = int(math.sin(self.t * speed * 3) * 12)
            s = font_e.render(star, True, C64["yellow"])
            surf.blit(s, (sx, sy + bounce))

        # Luki grande celebrando
        S = max(8, W // 75)
        luki_w = 14 * S
        bounce = int(math.sin(self.t * 5) * 12)
        draw_luki(surf, W // 2 - luki_w // 2, int(H * 0.02), S=S, bounce=bounce)

        # Texto personalizado para Lucas
        render_text(surf, "¡¡EXCELENTE, LUCAS!!", W // 2, int(H * 0.44),
                    self.fonts["title"], C64["yellow"], center=True)
        render_text(surf, f"Nivel {self.li + 1}/5 completado",
                    W // 2, int(H * 0.54),
                    self.fonts["sub"], C64["green"], center=True)
        
        # COFRE CON ESTRELLA
        chest_x, chest_y = W // 2, int(H * 0.62)
        chest_size = 40
        chest_open = abs(math.sin(self.star_anim_t * 2)) * 0.7
        pygame.draw.rect(surf, (200, 100, 50),
                        (chest_x - chest_size//2, chest_y, chest_size, int(chest_size * 0.6)))
        pygame.draw.rect(surf, C64["yellow"],
                        (chest_x - chest_size//2, chest_y, chest_size, int(chest_size * 0.6)), 2)
        # Tapa del cofre
        pygame.draw.arc(surf, (200, 100, 50),
                       pygame.Rect(chest_x - chest_size//2, int(chest_y - chest_size * chest_open),
                                   chest_size, chest_size//2),
                       math.pi, 2*math.pi, 2)
        # Estrella dentro del cofre
        star_bounce = abs(math.sin(self.star_anim_t * 4)) * 6
        font_e = self.fonts.get("emoji", self.fonts["sub"])
        star_surf = font_e.render("⭐", True, C64["yellow"])
        surf.blit(star_surf, (chest_x - star_surf.get_width()//2,
                             chest_y - int(star_bounce)))
        
        # Contador de estrellas
        total_stars = self.progress["stars"] + (1 if self.new_star else 0)
        render_text(surf, f"Estrellas: {total_stars}/5",
                    W // 2, int(H * 0.78),
                    self.fonts["sub"], C64["yellow"], center=True)
        
        # Mostrar mascota desbloqueada
        if total_stars > 0 and (total_stars % 5) == 0:
            pet_idx = (total_stars // 5) - 1
            if pet_idx < len(PETS):
                pet = PETS[pet_idx]
                render_text(surf, f"Desbloqueaste: {pet['name']} {pet['emoji']}",
                           W // 2, int(H * 0.86),
                           self.fonts["small"], C64["green"], center=True)

        self.btn.draw(surf)

# ==================================================================
# PANTALLA FINAL CON CELEBRACION
# ==================================================================
class CelebrationScreen:
    def __init__(self, fonts, W, H, progress_data):
        self.fonts = fonts
        self.W, self.H = W, H
        self.progress = progress_data
        self.done = False
        self.t    = 0.0
        bw, bh = int(W * 0.50), int(H * 0.15)
        self.btn = TouchButton(
            ((W - bw) // 2, int(H * 0.80), bw, bh),
            "¡OTRA VEZ!", C64["cyan"], fonts["btn"]
        )

    def handle(self, ev):
        if self.btn.handle(ev):
            self.done = True

    def update(self, dt):
        self.t += dt
        self.btn.update()

    def draw(self, surf):
        surf.fill(C64["bg"])
        draw_grid(surf, C64["grid"])
        W, H = self.W, self.H

        S = max(8, W // 72)
        luki_w = 14 * S
        bounce = int(math.sin(self.t * 3) * 8)
        draw_luki(surf, W // 2 - luki_w // 2, int(H * 0.02), S=S, bounce=bounce)

        render_text(surf, "¡¡LO LOGRASTE, LUCAS!!",
                    W // 2, int(H * 0.40),
                    self.fonts["title"], C64["yellow"], center=True)
        render_text(surf, "Desbloqueaste TODOS los animalitos",
                    W // 2, int(H * 0.50),
                    self.fonts["sub"], C64["green"], center=True)
        render_text(surf, "Sos un programador de verdad!",
                    W // 2, int(H * 0.58),
                    self.fonts["sub"], C64["cyan"], center=True)
        
        # Mostrar todos los animalitos celebrando
        font_e = self.fonts.get("emoji", self.fonts["sub"])
        num_pets = len([p for p in range(len(PETS)) if p in self.progress.get("unlocked_pets", [])])
        if num_pets == len(PETS):  # Todos desbloqueados
            pet_y = int(H * 0.65)
            pets_per_row = 3
            for i, pet in enumerate(PETS):
                row = i // pets_per_row
                col = i % pets_per_row
                pet_x = W // 2 - (pets_per_row - 1) * 60 // 2 + col * 80
                pet_py = pet_y + row * 50
                
                # Animacion de salto
                jump = int(math.sin((self.t + i * 0.2) * 3) * 8)
                pet_surf = font_e.render(pet['emoji'], True, C64["white"])
                surf.blit(pet_surf, (pet_x - pet_surf.get_width()//2,
                                     pet_py + jump))
                render_text(surf, pet['name'], pet_x, pet_py + 25,
                           self.fonts["tiny"], C64["white"], center=True)
        
        self.btn.draw(surf)

        render_text(surf, "Luki esta MUY orgullosa de vos",
                    W // 2, H - 22,
                    self.fonts["tiny"], C64["grey"], center=True)

# ==================================================================
# CARGA DE FUENTES
# ==================================================================
def load_fonts(W, H):
    base = max(12, W // 60)
    try:
        return {
            "title": pygame.font.SysFont("monospace", int(base * 2.8), bold=True),
            "sub":   pygame.font.SysFont("monospace", int(base * 1.8), bold=True),
            "btn":   pygame.font.SysFont("monospace", int(base * 1.6), bold=True),
            "small": pygame.font.SysFont("monospace", int(base * 1.2)),
            "tiny":  pygame.font.SysFont("monospace", int(base * 0.9)),
            "emoji": pygame.font.SysFont("seguiemj",  int(base * 1.8)),
        }
    except Exception:
        f = pygame.font.Font(None, int(base * 2))
        return {k: f for k in ("title","sub","btn","small","tiny","emoji")}

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
            self.screen = pygame.display.set_mode((1024, 640))

        pygame.display.set_caption("🐸 KidsLab Luki Edition")
        self.clock  = pygame.time.Clock()
        self.W, self.H = self.screen.get_size()
        self.fonts  = load_fonts(self.W, self.H)

        # Sistema de progreso
        self.progress = {"stars": 0, "unlocked_pets": []}

        self._go_welcome()

    def _go_welcome(self):
        self.scene = "welcome"
        self.screen_obj = WelcomeScreen(self.fonts, self.W, self.H)

    def _go_game(self, level_index):
        self.scene = "game"
        self.level_index = level_index
        self.screen_obj = GameScreen(self.fonts, self.W, self.H)

    def _go_win(self, level_index):
        self.scene = "win"
        # Agregar una estrella
        self.progress["stars"] += 1
        # Desbloquear mascota si es múltiplo de 5
        if self.progress["stars"] % 5 == 0:
            pet_idx = (self.progress["stars"] // 5) - 1
            if pet_idx < len(PETS) and pet_idx not in self.progress["unlocked_pets"]:
                self.progress["unlocked_pets"].append(pet_idx)
                sfx.beep(1318, 200, 0.2)  # sonido especial
        self.screen_obj = WinScreen(self.fonts, self.W, self.H, level_index, self.progress)

    def _go_celebration(self):
        self.scene = "celebration"
        self.screen_obj = CelebrationScreen(self.fonts, self.W, self.H, self.progress)

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

            # Transiciones
            if self.screen_obj.done:
                if self.scene == "welcome":
                    self._go_game(0)
                elif self.scene == "game":
                    self._go_welcome()  # volver a bienvenida (juego libre sin límite)

            self.screen_obj.draw(self.screen)

            # Scanlines sutiles
            W, H = self.W, self.H
            scan = pygame.Surface((W, H), pygame.SRCALPHA)
            for y in range(0, H, 4):
                pygame.draw.line(scan, (0, 0, 0, 18), (0, y), (W, y))
            self.screen.blit(scan, (0, 0))

            pygame.display.flip()

# ==================================================================
# ENTRY POINT
# ==================================================================
if __name__ == "__main__":
    App().run()
