# config.py
import pygame

# ==================================================================
# 1. DEFINICIÓN DE CONSTANTES
# ==================================================================
W, H     = 1024, 640
FPS      = 60
CELL     = 32
MOBILE   = False # Set to True for APK build
ANIM_H   = int(H * 0.58)
PANEL_Y  = ANIM_H
PANEL_H  = H - ANIM_H
STATS_W  = int(W * 0.22)
CONSOLE_X= STATS_W
CONSOLE_W= W - STATS_W

# Paleta Commodore 64
C64 = {
    "white":    (255, 255, 255),
    "cyan":     (0,   255, 255),
    "yellow":   (255, 255, 0),
    "lt_green": (144, 238, 144),
    "red":      (255, 80,  80),
    "mid_grey": (128, 128, 128),
    "black":    (0,   0,   0),
    "lt_grey":  (192, 192, 192),
}

# Colores de la UI
BG_COLOR   = (16,  16,  64)
GRID_COLOR = (30,  30,  90)
BORDER_COL = (100, 100, 255)
HACKER_COL = (255, 80,  80)
NERD_COL   = (80,  200, 255)
OK_COL     = C64["lt_green"]
ERR_COL    = C64["red"]
DIM_COL    = C64["mid_grey"]
CURSOR_COL = C64["yellow"]
GUIDE_COL  = (80, 80, 150)

# ==================================================================
# 2. DATOS DE NIVELES
# ==================================================================
LEVELS = [
    {
        "id": 1, "titulo": "Adelante", "emoji_titulo": "➡️", "concepto": "Usá FD para moverte hacia adelante", "color": (100, 200, 100),
        "comandos_validos": {"FD": None, "ADELANTE": None},
        "pasos": [{"cmd": "FD 4", "action": ("fd", 4), "desc": "Mover 4 casillas adelante"}]
    },
    {
        "id": 2, "titulo": "Giros", "emoji_titulo": "🔄", "concepto": "Gira a la derecha o izquierda", "color": (100, 150, 255),
        "comandos_validos": {"FD": None, "RT": None, "LT": None, "DERECHA": None, "IZQUIERDA": None},
        "pasos": [
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2"},
            {"cmd": "RT 90", "action": ("rt", 90), "desc": "Gira derecha 90°"},
            {"cmd": "FD 3", "action": ("fd", 3), "desc": "Adelante 3"}
        ]
    },
    {
        "id": 3, "titulo": "Cuadrado", "emoji_titulo": "⬛", "concepto": "Dibujá un cuadrado", "color": (255, 180, 100),
        "comandos_validos": {"FD": None, "RT": None, "LT": None},
        "pasos": [
            {"cmd": "FD 4", "action": ("fd", 4), "desc": "Adelante 4"},
            {"cmd": "RT 90", "action": ("rt", 90), "desc": "Derecha"},
            {"cmd": "FD 4", "action": ("fd", 4), "desc": "Adelante 4"},
            {"cmd": "RT 90", "action": ("rt", 90), "desc": "Derecha"},
            {"cmd": "FD 4", "action": ("fd", 4), "desc": "Adelante 4"},
            {"cmd": "RT 90", "action": ("rt", 90), "desc": "Derecha"},
            {"cmd": "FD 4", "action": ("fd", 4), "desc": "Adelante 4"}
        ]
    },
    {
        "id": 4, "titulo": "Camino Secreto", "emoji_titulo": "🌀", "concepto": "Combiná movimientos y giros", "color": (200, 100, 200),
        "comandos_validos": {"FD": None, "BK": None, "RT": None, "LT": None},
        "pasos": [
            {"cmd": "FD 5", "action": ("fd", 5), "desc": "Adelante 5"},
            {"cmd": "LT 90", "action": ("lt", 90), "desc": "Izquierda"},
            {"cmd": "FD 3", "action": ("fd", 3), "desc": "Adelante 3"},
            {"cmd": "RT 90", "action": ("rt", 90), "desc": "Derecha"},
            {"cmd": "FD 2", "action": ("fd", 2), "desc": "Adelante 2"}
        ]
    },
    {
        "id": 5, "titulo": "El Bucle", "emoji_titulo": "🔁", "concepto": "Usá REPEAT para repetir acciones", "color": (255, 255, 100),
        "comandos_validos": {"FD": None, "RT": None, "REPEAT": None},
        "pasos": [
            {"cmd": "REPEAT 4 [ FD 2 RT 90 ]", "action": ("repeat", 4, [("fd", 2), ("rt", 90)]), "desc": "Dibujá un cuadrado pequeño con REPEAT"}
        ]
    },
    {
        "id": 6, "titulo": "Condicional", "emoji_titulo": "❓", "concepto": "IF para tomar decisiones", "color": (100, 255, 255),
        "comandos_validos": {"FD": None, "RT": None, "IF": None},
        "pasos": [
            {"cmd": "IF BUG [ FD 2 ]", "action": ("if", "bug", [("fd", 2)]), "desc": "Si ves un bug, avanzá 2 casillas"}
        ]
    }
]

# ==================================================================
# 3. TRIVIA Y MASCOTAS
# ==================================================================
TRIVIA = [
    ("1947", "Grace Hopper encontró una polilla real\natrapada en un relay del Harvard Mark II.\nNació la palabra BUG — y el debugging."),
    ("1967", "Logo fue el primer lenguaje diseñado\npara enseñar programación a niños.\nUsaba una tortuga que dibujaba con comandos."),
    ("1982", "El Commodore 64 vendió 17 millones\nde unidades. Fue la PC más vendida\nde la historia. Este juego le rinde homenaje."),
    ("HOY",  "Vos escribiste código real.\nAprendiste a depurar como Grace Hopper.\nSos parte de esta historia. 🐸"),
]

PET_TYPES = [
    {"name": "Saltarina", "emoji": "🐸", "poder": "Salta más rápido"},
    {"name": "Tortu", "emoji": "🐢", "poder": "Escudo de error"},
    {"name": "Misifú", "emoji": "🐱", "poder": "Vida extra"},
    {"name": "Pulgi", "emoji": "🐶", "poder": "Olfato de bugs"},
    {"name": "Pinguino", "emoji": "🐧", "poder": "Congela la CPU"},
]

ROLES_PER_LEVEL = ["hacker", "nerd", "hacker", "nerd"]

ACHIEVEMENTS = [
    {"id": "first_win", "name": "Primer Salto", "desc": "Ganá tu primer nivel", "icon": "🐸"},
    {"id": "pet_owner", "name": "Entrenador", "desc": "Conseguí una mascota", "icon": "🦴"},
    {"id": "loop_master", "name": "Rey del Bucle", "desc": "Usá REPEAT correctamente", "icon": "🔁"},
    {"id": "fast_frog", "name": "Rana Relámpago", "desc": "Completá un nivel en menos de 30s", "icon": "⚡"},
]
