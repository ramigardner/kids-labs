# ui_utils.py
import pygame
import math
from config import C64, W, H, BORDER_COL, GRID_COLOR

def px(surf, text, x, y, font, color=None, center=False, right=False):
    color = color or C64["white"]
    sh = font.render(text, False, (0,0,0))
    rx = x - sh.get_width()//2 if center else (x - sh.get_width() if right else x)
    surf.blit(sh, (rx+1, y+1))
    r = font.render(text, False, color)
    rx2 = x - r.get_width()//2 if center else (x - r.get_width() if right else x)
    surf.blit(r, (rx2, y))
    return r.get_width()

def draw_border_box(surf, rect, color=BORDER_COL, fill=None, thickness=2):
    if fill: pygame.draw.rect(surf, fill, rect)
    pygame.draw.rect(surf, color, rect, thickness)
    x, y, w, h = rect
    for corner in [(x,y),(x+w-2,y),(x,y+h-2),(x+w-2,y+h-2)]:
        pygame.draw.rect(surf, C64["white"], (*corner, 2, 2))

def draw_grid(surf, rect, cell=32, color=GRID_COLOR):
    x, y, w, h = rect
    for gx in range(x, x+w, cell): pygame.draw.line(surf, color, (gx, y), (gx, y+h))
    for gy in range(y, y+h, cell): pygame.draw.line(surf, color, (x, gy), (x+w, gy))

def draw_bar(surf, x, y, w, h, val, maxv, color):
    pygame.draw.rect(surf, (10,10,40), (x, y, w, h))
    fill = int(w * val / max(maxv,1))
    for bx in range(0, fill, 4):
        bw = min(3, fill-bx)
        pygame.draw.rect(surf, color, (x+bx, y+1, bw, h-2))
    pygame.draw.rect(surf, C64["mid_grey"], (x, y, w, h), 1)

def scanlines(surf):
    sl = pygame.Surface((W, H), pygame.SRCALPHA)
    for gy in range(0, H, 4): pygame.draw.line(sl, (0,0,0,20), (0,gy), (W,gy))
    surf.blit(sl, (0,0))

def draw_fade(surf, alpha):
    fade_surf = pygame.Surface((W, H))
    fade_surf.fill((0, 0, 0))
    fade_surf.set_alpha(alpha)
    surf.blit(fade_surf, (0, 0))

def draw_demo_banner(surf, fonts, t):
    banner_w, banner_h = 110, 28
    bx = W - banner_w - 8; by = 8
    s = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
    alpha = int(160 + 40 * math.sin(t * 2))
    s.fill((20, 180, 80, alpha))
    surf.blit(s, (bx, by))
    pygame.draw.rect(surf, (50, 255, 120), (bx, by, banner_w, banner_h), 2)
    for cx, cy in [(bx,by),(bx+banner_w-2,by),(bx,by+banner_h-2),(bx+banner_w-2,by+banner_h-2)]:
        pygame.draw.rect(surf, (255,255,255), (cx, cy, 2, 2))
    txt = fonts["sm"].render("★ DEMO ★", False, (255, 255, 255))
    surf.blit(txt, (bx + banner_w//2 - txt.get_width()//2, by + banner_h//2 - txt.get_height()//2))

def normalize_input(text: str) -> str:
    import re; text = text.strip().upper()
    m = re.match(r'^([A-Z]+)\(([^)]+)\)$', text)
    if m: return f"{m.group(1)} {m.group(2)}"
    m2 = re.match(r'^([A-Z]+)(\d+(?:\.\d+)?)$', text)
    if m2: return f"{m2.group(1)} {m2.group(2)}"
    return text
