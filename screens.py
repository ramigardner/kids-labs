# screens.py
import pygame
import math
import time
import random
from config import *
from resources import sfx
from ui_utils import *
from entities import Frog, CPUPlayer
from achievements import achievement_manager

class LoginSolo:
    def __init__(self, fonts): self.fonts = fonts; self.name = ""; self.t = 0.0; self.done = False; self.result = {}; self.error = ""; self.mode = "cpu"; self.mode_selected = False
    def handle(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                if not self.name.strip(): self.error = "INGRESA TU NOMBRE"; return
                if not self.mode_selected: self.error = "PRIMERO SELECCIONA MODO (← →)"; return
                self.result = {"name": self.name.strip(), "mode": self.mode}; self.done = True
            elif ev.key == pygame.K_BACKSPACE: self.name = self.name[:-1]
            elif ev.key == pygame.K_LEFT: self.mode = "cpu"; self.mode_selected = True; sfx.beep(660, 30, "square", 0.08)
            elif ev.key == pygame.K_RIGHT: self.mode = "solo"; self.mode_selected = True; sfx.beep(660, 30, "square", 0.08)
            else:
                ch = ev.unicode
                if ch and ch.isprintable() and len(self.name) < 10: self.name += ch.upper(); sfx.beep(880, 20, "square", 0.05)
    def draw(self, surf):
        self.t += 0.016; surf.fill(BG_COLOR); draw_grid(surf, (0,0,W,H), 32, GRID_COLOR)
        glow = abs(math.sin(self.t*1.5)); title_col = tuple(int(80 + 175*glow) for _ in range(3))
        px(surf, "🧪 KIDSLAB — ORACLE KIDS", W//2, 20, self.fonts["title"], C64["cyan"], center=True)
        px(surf, "HACKERS  VS  NERDS  EDITION", W//2, 46, self.fonts["sm"], C64["yellow"], center=True)
        pygame.draw.line(surf, BORDER_COL, (80, 66), (W-80, 66), 1)
        draw_border_box(surf, (30, 78, 290, 380), BORDER_COL, fill=(8,8,30))
        px(surf, "CÓMO JUGAR", 175, 88, self.fonts["sm"], C64["yellow"], center=True)
        pygame.draw.line(surf, BORDER_COL, (40, 104), (310, 104), 1)
        instrucciones = [("ESCRIBÍ", "el comando y ENTER"), ("ADELANTE 4", "→ la rana avanza"), ("DERECHA 90", "→ gira a la derecha"), ("IZQUIERDA 90", "→ gira izquierda"), (" ", " "), ("CTRL+F", "→ alimentá la mascota"), ("GRACE", "→ comando secreto")]
        iy = 110
        for cmd, desc in instrucciones:
            if cmd == " ": iy += 6; continue
            px(surf, cmd, 42, iy, self.fonts["xs"], C64["cyan"]); px(surf, desc, 42, iy+12, self.fonts["xs"], DIM_COL); iy += 28
        draw_border_box(surf, (340, 78, 380, 130), BORDER_COL, fill=(10,10,40))
        px(surf, "TU NOMBRE: ", 352, 90, self.fonts["sm"], DIM_COL)
        bc = CURSOR_COL if int(self.t*2)%2==0 else C64["mid_grey"]
        draw_border_box(surf, (352, 108, 356, 30), bc, fill=(0,0,20), thickness=2)
        disp = (self.name + ("|" if int(self.t*2)%2==0 else " ")) or "  "
        px(surf, disp, 360, 114, self.fonts["md"], C64["white"])
        px(surf, "MODO  ←  →", 530, 224, self.fonts["sm"], C64["yellow"], center=True)
        cpu_col = C64["lt_green"] if self.mode=="cpu" else DIM_COL; solo_col = C64["lt_green"] if self.mode=="solo" else DIM_COL
        cpu_fill = (0,40,0) if self.mode=="cpu" else (15,15,30); solo_fill = (0,40,0) if self.mode=="solo" else (15,15,30)
        draw_border_box(surf, (350, 240, 160, 50), cpu_col, fill=cpu_fill, thickness=3 if self.mode=="cpu" else 1)
        draw_border_box(surf, (520, 240, 160, 50), solo_col, fill=solo_fill, thickness=3 if self.mode=="solo" else 1)
        px(surf, "VS CPU 🤖", 430, 258, self.fonts["sm"], cpu_col, center=True); px(surf, "SOLO 🐸", 600, 258, self.fonts["sm"], solo_col, center=True)
        desc = "Competís contra la máquina" if self.mode == "cpu" else "Sin rival — seguís la guía"
        px(surf, desc, 530, 302, self.fonts["xs"], DIM_COL, center=True)
        pulse = abs(math.sin(self.t*3)); bc2 = tuple(int(60+pulse*195) for _ in range(3))
        draw_border_box(surf, (370, 326, 320, 42), bc2, fill=(5,20,5), thickness=2)
        px(surf, "[ ENTER ]  EMPEZAR", 530, 339, self.fonts["md"], C64["lt_green"], center=True)
        if self.error: px(surf, "⚠  " + self.error, 530, 382, self.fonts["sm"], ERR_COL, center=True)
        draw_border_box(surf, (734, 78, 260, 380), BORDER_COL, fill=(8,8,30))
        px(surf, "MASCOTAS", W-130, 88, self.fonts["sm"], C64["yellow"], center=True)
        pygame.draw.line(surf, BORDER_COL, (744, 104), (984, 104), 1)
        py_pet = 114
        for pet in PET_TYPES:
            emoji_surf = self.fonts["emoji"].render(pet["emoji"], True, C64["white"]); surf.blit(emoji_surf, (750, py_pet))
            px(surf, pet["name"], 788, py_pet+2, self.fonts["sm"], C64["cyan"]); px(surf, pet["poder"], 788, py_pet+16, self.fonts["xs"], DIM_COL)
            py_pet += 40
        px(surf, "Ganá un nivel para", W-130, py_pet+8, self.fonts["xs"], DIM_COL, center=True)
        px(surf, "desbloquear mascota", W-130, py_pet+22, self.fonts["xs"], DIM_COL, center=True)
        pygame.draw.line(surf, BORDER_COL, (0, H-50), (W, H-50), 1)
        px(surf, "ASPR ORACLE NODE v2.0  ·  KIDSLAB.IO  ·  🧪", W//2, H-36, self.fonts["xs"], DIM_COL, center=True)
        px(surf, "Aprender jugando, competir pensando", W//2, H-20, self.fonts["xs"], (60,60,100), center=True)

class RoleReveal:
    def __init__(self, fonts, role, level_num): self.fonts = fonts; self.role = role; self.level_num = level_num; self.t = 0.0; self.phase = 0; self.count = 3; self.count_t = 0.0; self.done = False; sfx.beep(440, 100, "square", 0.12)
    def update(self, dt):
        self.t += dt
        if self.phase == 0:
            self.count_t += dt
            if self.count_t >= 1.0:
                self.count_t = 0; self.count -= 1
                if self.count > 0: sfx.beep(440 + self.count*100, 80, "square", 0.12)
                else: self.phase = 1; # sfx.play("level_start")
        elif self.phase == 1:
            if self.t > 2.5: self.phase = 2
        elif self.phase == 2:
            if self.t > 3.5: self.done = True
    def draw(self, surf):
        surf.fill(BG_COLOR); draw_grid(surf, (0,0,W,H), 32, GRID_COLOR)
        role_col = HACKER_COL if self.role=="hacker" else NERD_COL; role_icon = "☠" if self.role=="hacker" else "🛡"; role_name = "HACKER" if self.role=="hacker" else "NERD"
        px(surf, f"NIVEL {self.level_num} DE 6", W//2, 120, self.fonts["md"], DIM_COL, center=True)
        if self.phase == 0: px(surf, str(self.count), W//2, H//2-40, self.fonts["title"], C64["yellow"], center=True); px(surf, "PREPARATE...", W//2, H//2+40, self.fonts["sm"], DIM_COL, center=True)
        elif self.phase >= 1:
            flash = abs(math.sin(self.t*4)); col = tuple(int(c*flash + 50*(1-flash)) for c in role_col)
            px(surf, "TU ROL ES...", W//2, H//2-80, self.fonts["md"], DIM_COL, center=True)
            px(surf, f"{role_icon}  {role_name}  {role_icon}", W//2, H//2-20, self.fonts["title"], col, center=True)
            lv = LEVELS[self.level_num-1] if self.level_num <= len(LEVELS) else LEVELS[-1]
            px(surf, f"FIGURA: {lv['emoji_titulo']} {lv['titulo']}", W//2, H//2+50, self.fonts["sm"], C64["cyan"], center=True)
            px(surf, lv.get("concepto", " "), W//2, H//2+74, self.fonts["xs"], DIM_COL, center=True)
            if self.phase == 2 and int(self.t*3)%2==0: px(surf, "— COMENZANDO —", W//2, H//2+110, self.fonts["sm"], C64["lt_green"], center=True)

class TriviaScreen:
    def __init__(self, fonts, level_completed, player_won): self.fonts = fonts; self.t = 0.0; self.done = False; self.player_won = player_won; idx = min(level_completed, len(TRIVIA)-1); self.year, self.text = TRIVIA[idx]; sfx.play("door")
    def update(self, dt): self.t += dt; if self.t > 6.0: self.done = True
    def draw(self, surf):
        surf.fill(BG_COLOR); draw_grid(surf, (0,0,W,H), 32, GRID_COLOR)
        if self.player_won: px(surf, "★ NIVEL COMPLETADO ★", W//2, 100, self.fonts["lg"], C64["lt_green"], center=True)
        else: px(surf, "CPU GANÓ ESTE NIVEL", W//2, 100, self.fonts["md"], ERR_COL, center=True); px(surf, "PERO SEGUÍS APRENDIENDO...", W//2, 124, self.fonts["xs"], DIM_COL, center=True)
        draw_border_box(surf, (240, 200, W-480, 300), BORDER_COL, fill=(8,8,30))
        px(surf, f"// {self.year}", W//2, 230, self.fonts["md"], C64["yellow"], center=True)
        pygame.draw.line(surf, BORDER_COL, (260,256),(W-260,256),1)
        lines = self.text.split("\n")
        for i, line in enumerate(lines): px(surf, line, W//2, 274 + i*28, self.fonts["sm"], C64["cyan"], center=True)
        progress = min(1.0, self.t / 6.0); draw_bar(surf, 240, 520, W-480, 8, int(progress*100), 100, BORDER_COL)
        px(surf, "SIGUIENTE NIVEL EN...", W//2, 534, self.fonts["xs"], DIM_COL, center=True)
        bounce = int(math.sin(self.t*4)*10); px(surf, "🐸", W//2-16, 420+bounce, self.fonts["emoji"])

class RetroLoader:
    MESSAGES = [(0.0, "cyan", "ASPR ORACLE LAB v2.0"), (0.4, "grey", "INICIALIZANDO SIGUIENTE NIVEL..."), (0.9, "yellow", "CARGANDO MAPA DE BUGS..."), (1.4, "cyan", "CALIBRANDO KARMA ENGINE..."), (1.9, "green", "VERIFICANDO MASCOTA..."), (2.4, "yellow", "PREPARANDO RIVAL CPU..."), (2.75, "white", "LISTO.")]
    DURATION = 3.0
    def __init__(self, fonts, next_level, pet_data=None): self.fonts = fonts; self.next_level = next_level; self.pet_data = pet_data; self.t = 0.0; self.done = False; self._beeped = set(); sfx.beep(220, 80, "square", 0.08)
    def update(self, dt):
        self.t += dt
        for i, (trigger, *_) in enumerate(self.MESSAGES):
            if i not in self._beeped and self.t >= trigger: sfx.beep(400 + i * 80, 30, "square", 0.05); self._beeped.add(i)
        if self.t >= self.DURATION: self.done = True
    def draw(self, surf):
        surf.fill((0,0,0)); draw_grid(surf, (0,0,W,H), 32, (10,10,40))
        cx = W//2; lv_txt = f"— NIVEL {self.next_level + 1} DE 6 —"
        px(surf, lv_txt, cx, 80, self.fonts["title"], C64["yellow"], center=True)
        pygame.draw.line(surf, C64["mid_grey"], (W//2 - 200, 110), (W//2 + 200, 110), 1)
        col_map = {"cyan": C64["cyan"], "yellow": C64["yellow"], "green": C64["lt_green"], "grey": C64["mid_grey"], "white": C64["white"]}
        y = 150
        for trigger, col_key, msg in self.MESSAGES:
            if self.t >= trigger:
                color = col_map.get(col_key, C64["white"])
                is_last = (trigger == max(tr for tr, *_ in self.MESSAGES if self.t >= tr))
                suffix = ("_" if int(self.t * 4) % 2 == 0 else "  ") if is_last and not self.done else " "
                px(surf, " >  " + msg + suffix, cx, y, self.fonts["sm"], color, center=True)
            y += 28
        if self.pet_data: px(surf, f"{self.pet_data['emoji']}  {self.pet_data['name']}  ·  {self.pet_data['poder']}", cx, H - 160, self.fonts["sm"], C64["yellow"], center=True)
        progress = min(1.0, self.t / self.DURATION); bar_w = 400; bar_x = cx - bar_w//2; bar_y = H - 110
        pygame.draw.rect(surf, C64["mid_grey"], (bar_x - 2, bar_y - 2, bar_w + 4, 18), 1)
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            pygame.draw.rect(surf, C64["cyan"], (bar_x, bar_y, fill_w, 14))
            for bx in range(bar_x, bar_x + fill_w, 10): pygame.draw.rect(surf, (0,0,0,60), (bx+7, bar_y, 3, 14))
        px(surf, f"{int(progress * 100)}%", cx, bar_y + 20, self.fonts["xs"], C64["mid_grey"], center=True)
        px(surf, "ASPR ORACLE NODE v2.0  ·  KIDSLAB.IO", cx, H - 40, self.fonts["xs"], (50,50,100), center=True)

class GameOverScreen:
    def __init__(self, fonts, player_wins, cpu_wins, name, mode):
        self.fonts = fonts; self.player_wins = player_wins; self.cpu_wins = cpu_wins; self.name = name; self.mode = mode; self.restart_requested = False; self.t = 0.0
        if mode == "solo": sfx.play("win")
        elif player_wins > cpu_wins: sfx.play("win")
        else: sfx.play("error")
    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE): self.restart_requested = True
    def draw(self, surf):
        self.t += 0.016; surf.fill(BG_COLOR); draw_grid(surf, (0,0,W,H), 32, GRID_COLOR)
        if self.mode == "solo": title = "★ COMPLETASTE EL JUEGO ★"; col = C64["lt_green"]; msg = "¡Aprendiste los comandos como una campeona o campeón!"
        else: won = self.player_wins > self.cpu_wins; col = C64["lt_green"] if won else ERR_COL; title = "★ GANASTE ★" if won else "PERDISTE"; msg = f"{self.name}: {self.player_wins}  vs  CPU: {self.cpu_wins}"
        px(surf, title, W//2, H//2-100, self.fonts["title"], col, center=True)
        if self.mode != "solo": px(surf, msg, W//2, H//2-40, self.fonts["md"], C64["white"], center=True)
        else: px(surf, msg, W//2, H//2-40, self.fonts["sm"], C64["cyan"], center=True)
        px(surf, "ASPR ORACLE LAB · KIDSLAB.IO", W//2, H//2+40, self.fonts["xs"], DIM_COL, center=True)
        if int(self.t*2)%2==0: px(surf, "[ R ]  [ ENTER ]  [ ESPACIO ]  — REINICIAR", W//2, H//2+80, self.fonts["sm"], C64["yellow"], center=True)
        else: px(surf, "PRESIONA R PARA REINICIAR", W//2, H//2+80, self.fonts["sm"], C64["lt_green"], center=True)
        b = int(math.sin(self.t*3)*8); px(surf, "🐸", W//2-60, H//2+140+b, self.fonts["emoji"]); px(surf, "🐸", W//2+30, H//2+140-b, self.fonts["emoji"])

class GameSolo:
    def __init__(self, fonts, name, level_index=0, mode="cpu"):
        self.fonts = fonts; self.name = name; self.mode = mode; self.t = 0.0; self.blink = 0.0; self.level_index = level_index; self.my_role = ROLES_PER_LEVEL[level_index % len(ROLES_PER_LEVEL)]; self.power = 50; self.karma = 0; self.wins = 0; self.step_index = 0; self.has_pet = False; self.pet_data = None; self.pet_hunger = 100; self.pet_anim_t = 0.0; self.level_done = False; self.input_text = " "; self.log = []; self.result_msg = " "; self.result_col = C64["white"]; self.result_t = 0.0; self.cpu = None
        if self.mode == "cpu": self.cpu = CPUPlayer(level_index=self.level_index)
        self._load_level()
        self.canvas_w = 192; self.canvas_h = 192; self.canvas_x = W//2 - self.canvas_w//2; self.canvas_y = ANIM_H//2 - self.canvas_h//2 - 15
        frog_col = HACKER_COL if self.my_role=="hacker" else NERD_COL; self.my_frog = Frog(self.my_role, self.canvas_x, self.canvas_y, frog_col, len(self.pasos))
        if self.mode == "cpu":
            cpu_role = "nerd" if self.my_role=="hacker" else "hacker"; cpu_col = NERD_COL if cpu_role=="nerd" else HACKER_COL; self.cpu_frog = Frog(cpu_role, self.canvas_x + self.canvas_w + 40, self.canvas_y, cpu_col, len(self.pasos))
        else: self.cpu_frog = None
        self.time_remaining = 120.0 if self.mode == "cpu" else 0.0; self.time_limit = 120.0; self.flash_alpha = 0; self.flash_color = C64["white"]; self.burst_parts = []; self.door_open = 0.0; self.door_opening = False; self.guide_points = []; self._compute_guide_path()
    def _load_level(self):
        lv = LEVELS[self.level_index]; self.pasos = lv["pasos"]; self.level_color = lv["color"]; self.step_index = 0; self.level_done = False
        if self.mode == "cpu": self.time_remaining = 120.0; self.time_limit = 120.0
        else: self.time_remaining = 0.0
        self.my_role = ROLES_PER_LEVEL[self.level_index % len(ROLES_PER_LEVEL)]; self.door_open = 0.0; self.door_opening = False
    def _compute_guide_path(self):
        if self.mode != "solo": return
        cx, cy = 5.0, 5.0; angle = 90.0; points = [(cx, cy)]
        for paso in self.pasos:
            accion = paso["action"]; cmd, val = accion
            if cmd == "fd": rad = math.radians(angle); nx = cx + math.cos(rad)*val; ny = cy - math.sin(rad)*val; cx, cy = nx, ny; points.append((cx, cy))
            elif cmd == "bk": rad = math.radians(angle); nx = cx - math.cos(rad)*val; ny = cy + math.sin(rad)*val; cx, cy = nx, ny; points.append((cx, cy))
            elif cmd == "lt": angle += val
            elif cmd == "rt": angle -= val
        self.guide_points = points
    def add_log(self, msg, color=None):
        self.log.append({"msg": msg[:48], "color": color or C64["white"]})
        if len(self.log) > 8: self.log.pop(0)
    def flash(self, color, alpha=100): self.flash_color = color; self.flash_alpha = alpha
    def burst(self, x, y, color, n=20):
        for _ in range(n):
            angle = random.uniform(0, math.pi*2); speed = random.uniform(2,8)
            self.burst_parts.append({"x":x, "y":y, "vx":math.cos(angle)*speed, "vy":math.sin(angle)*speed, "life":1.0, "color":color, "r":random.randint(2,5)})
    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            pressed = pygame.key.get_pressed(); ctrl_pressed = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
            if ev.key == pygame.K_f and ctrl_pressed:
                if self.has_pet: self.pet_hunger = min(100, self.pet_hunger+20); sfx.beep(880,60,"square",0.08); self.add_log(f"🍖 ¡{self.pet_data['name']} alimentada/o!", C64["lt_green"])
            elif ev.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
            elif ev.key == pygame.K_RETURN: self._submit()
            elif ev.key == pygame.K_ESCAPE: self.input_text = " "
            else:
                ch = ev.unicode
                if ch and ch.isprintable() and len(self.input_text) < 28: self.input_text += ch; sfx.beep(880, 15, "square", 0.04)
        elif ev.type == pygame.MOUSEBUTTONDOWN and MOBILE:
            mx, my = ev.pos
            bx, by = CONSOLE_X + 10, PANEL_Y + 50
            cmds = ["FD", "BK", "RT", "LT", "REPEAT", "IF"]
            for i, c in enumerate(cmds):
                if bx + i*60 <= mx <= bx + i*60 + 50 and by <= my <= by + 30:
                    self.input_text = c + " "; sfx.beep(880, 20, "square", 0.05)

    def _submit(self):
        inp_raw = self.input_text.strip()
        if not inp_raw: return
        self.input_text = " "
        if self.step_index >= len(self.pasos): return
        inp = normalize_input(inp_raw)
        lv = LEVELS[self.level_index]; step = self.pasos[self.step_index]
        
        if inp.strip().upper() == step["cmd"].upper():
            sfx.play("piece"); self.my_frog.execute(step["action"]); self.step_index += 1; self.karma += 5; self.power = min(100, self.power+3); self.add_log(f"✓ ¡Correcto!", OK_COL)
            self.result_msg = "CORRECTO!"; self.result_col = OK_COL; self.flash(OK_COL, 60)
            
            if "REPEAT" in inp.upper(): achievement_manager.unlock("loop_master")
            
            if self.step_index >= len(self.pasos):
                self.level_done = True; self.wins += 1; self.karma += 50; self.power = min(100, self.power+15)
                achievement_manager.unlock("first_win")
                if not self.has_pet:
                    self.has_pet = True; self.pet_data = random.choice(PET_TYPES).copy(); self.pet_hunger = 100; sfx.play("pet")
                    achievement_manager.unlock("pet_owner")
                self.door_opening = True; sfx.play("win"); self.burst(W//2, ANIM_H//2, OK_COL, 35)
        else:
            sfx.play("error"); self.my_frog.shake_error(); self.power = max(0, self.power-5); self.add_log(f"✗ Se esperaba: {step['cmd']}", ERR_COL); self.result_msg = "INCORRECTO"; self.result_col = ERR_COL
        self.result_t = 2.5

    def update(self, dt) -> str:
        self.t += dt; self.blink += dt; self.result_t = max(0, self.result_t-dt); self.flash_alpha = max(0, self.flash_alpha-180*dt); self.pet_anim_t += dt
        if self.mode == "cpu" and not self.level_done and self.cpu and not self.cpu.finished_level: self.time_remaining = max(0, self.time_remaining - dt)
        self.my_frog.update(dt)
        if self.cpu_frog: self.cpu_frog.update(dt)
        if self.door_opening: self.door_open = min(1.0, self.door_open + dt*0.7)
        for p in self.burst_parts: p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=0.2; p["life"]-=dt
        self.burst_parts = [p for p in self.burst_parts if p["life"] > 0]
        if self.mode == "cpu" and self.cpu and not self.cpu.finished_level and not self.level_done: self.cpu.tick(self.pasos, self.cpu_frog, self)
        player_won = self.level_done; cpu_won = False
        if self.mode == "cpu" and self.cpu: cpu_won = self.cpu.finished_level and not self.level_done
        timeout = (self.mode == "cpu") and (self.time_remaining <= 0) and not player_won and not cpu_won
        if player_won or cpu_won or timeout:
            if timeout and not player_won and not cpu_won: self.add_log("TIEMPO AGOTADO", ERR_COL); self.power = max(0, self.power-20)
            return "trivia"
        return ""
    def draw(self, surf):
        surf.fill(BG_COLOR); self._draw_anim(surf); self._draw_stats(surf); self._draw_console(surf)
        if MOBILE: self._draw_touch_controls(surf)
        role_col = HACKER_COL if self.my_role=="hacker" else NERD_COL
        pygame.draw.line(surf, role_col, (0,ANIM_H),(W,ANIM_H), 2); pygame.draw.line(surf, BORDER_COL,(STATS_W,PANEL_Y),(STATS_W,H),1)
        if self.flash_alpha > 0: fl = pygame.Surface((W,H), pygame.SRCALPHA); fl.fill((*self.flash_color, int(self.flash_alpha))); surf.blit(fl, (0,0))
        for p in self.burst_parts: a = int(p["life"]*255); s = pygame.Surface((p["r"]*2,p["r"]*2), pygame.SRCALPHA); pygame.draw.circle(s, (*p["color"],a),(p["r"],p["r"]),p["r"]); surf.blit(s,(int(p["x"])-p["r"],int(p["y"])-p["r"]))
        scanlines(surf)
    def _draw_touch_controls(self, surf):
        cmds = ["FD", "BK", "RT", "LT", "REPEAT", "IF"]
        bx, by = CONSOLE_X + 10, PANEL_Y + 50
        for i, c in enumerate(cmds):
            rect = (bx + i*60, by, 50, 30)
            draw_border_box(surf, rect, C64["cyan"], fill=(20,20,60))
            px(surf, c, bx + i*60 + 25, by + 8, self.fonts["xs"], C64["white"], center=True)
    def _draw_guide(self, surf):
        if self.mode != "solo" or not self.guide_points: return
        ox, oy = self.canvas_x, self.canvas_y
        for i in range(len(self.guide_points)-1):
            x1, y1 = self.guide_points[i]; x2, y2 = self.guide_points[i+1]
            px1 = ox + x1*CELL; py1 = oy + y1*CELL; px2 = ox + x2*CELL; py2 = oy + y2*CELL
            dash_len = 8; step = 4; dist = math.hypot(px2-px1, py2-py1)
            if dist < 0.1: continue
            dx = (px2-px1)/dist; dy = (py2-py1)/dist
            for t in range(0, int(dist), step):
                if (t // dash_len) % 2 == 0: sx = px1 + dx*t; sy = py1 + dy*t; pygame.draw.circle(surf, GUIDE_COL, (int(sx), int(sy)), 3)
        if self.step_index < len(self.guide_points):
            cx, cy = self.guide_points[self.step_index]; px = ox + cx*CELL; py = oy + cy*CELL
            pygame.draw.circle(surf, C64["yellow"], (int(px), int(py)), 8, 2); pygame.draw.circle(surf, C64["white"], (int(px), int(py)), 4)
    def _draw_anim(self, surf):
        for dy in range(ANIM_H):
            ratio = dy/ANIM_H; c = tuple(int(BG_COLOR[i]*(0.7+0.3*(1-ratio))) for i in range(3)); pygame.draw.line(surf, c, (0,dy),(W,dy))
        draw_grid(surf, (0,0,W,ANIM_H), 32, GRID_COLOR)
        ground_y = ANIM_H-45
        for gx in range(0, W, 16): c = C64["mid_grey"] if (gx//16)%2==0 else (50,50,100); pygame.draw.rect(surf, c, (gx, ground_y, 16, 3))
        canvas_surf = pygame.Surface((self.canvas_w, self.canvas_h)); canvas_surf.fill((8,8,30))
        for cx in range(0, self.canvas_w, CELL): pygame.draw.line(canvas_surf,(20,20,60),(cx,0),(cx,self.canvas_h))
        for cy in range(0, self.canvas_h, CELL): pygame.draw.line(canvas_surf,(20,20,60),(0,cy),(self.canvas_w,cy))
        surf.blit(canvas_surf,(self.canvas_x, self.canvas_y))
        draw_border_box(surf,(self.canvas_x,self.canvas_y,self.canvas_w,self.canvas_h),self.level_color, thickness=2)
        self._draw_guide(surf); self._draw_door(surf)
        prog = self.step_index / max(len(self.pasos),1); bar_y = self.canvas_y + self.canvas_h + 6
        draw_bar(surf, self.canvas_x, bar_y, self.canvas_w, 7, int(prog*100), 100, self.level_color)
        px(surf, f"TU PROGRESO: {self.step_index}/{len(self.pasos)}", self.canvas_x, bar_y+10, self.fonts["xs"], self.level_color)
        self.my_frog.draw(surf, self.fonts)
        if self.cpu_frog: self.cpu_frog.draw(surf, self.fonts)
        role_col = HACKER_COL if self.my_role=="hacker" else NERD_COL
        px(surf, f"{self.name[:8]} ({self.my_role.upper()})", int(self.my_frog.anim_x), self.canvas_y+self.canvas_h+20, self.fonts["xs"], role_col, center=True)
        if self.mode == "cpu" and self.cpu_frog:
            cpu_role = "nerd" if self.my_role=="hacker" else "hacker"; cpu_col = NERD_COL if cpu_role=="nerd" else HACKER_COL
            px(surf, f"CPU ({cpu_role.upper()})", int(self.cpu_frog.anim_x), self.canvas_y+self.canvas_h+20, self.fonts["xs"], cpu_col, center=True)
            cpu_prog = self.cpu.step_index / max(len(self.pasos),1)
            draw_bar(surf, int(self.cpu_frog.anim_x)-40, self.canvas_y+self.canvas_h+32, 80, 5, int(cpu_prog*100), 100, cpu_col)
        else: px(surf, "★ SIGUE EL CAMINO ★", int(self.my_frog.anim_x), self.canvas_y+self.canvas_h+32, self.fonts["xs"], C64["yellow"], center=True)
        if self.has_pet and self.pet_data:
            pet_x = 80; pet_y = ground_y - 55; b = int(math.sin(self.pet_anim_t*3)*5)
            pet_surf = self.fonts["emoji"].render(self.pet_data["emoji"], True, C64["white"]); surf.blit(pet_surf,(pet_x-pet_surf.get_width()//2, pet_y+b))
            px(surf, self.pet_data["name"], pet_x, pet_y+32, self.fonts["xs"], HACKER_COL if self.my_role=="hacker" else NERD_COL, center=True)
            draw_bar(surf, pet_x-25, pet_y+44, 50,4, self.pet_hunger, 100, C64["lt_green"])
        lv = LEVELS[self.level_index]
        px(surf, f"{lv['emoji_titulo']} {lv['titulo']}", W//2, 10, self.fonts["sm"], self.level_color, center=True)
    def _draw_door(self, surf):
        dw, dh = 100, 120; dx = self.canvas_x + self.canvas_w//2 - dw//2; dy = self.canvas_y - dh - 10
        glow = abs(math.sin(self.t*2)); bc = tuple(int(c*(0.5+0.5*glow)) for c in self.level_color)
        pygame.draw.rect(surf,(10,10,40),(dx,dy,dw,dh)); draw_border_box(surf,(dx,dy,dw,dh), bc, thickness=2)
        half = int(dw/2*(1-self.door_open))
        if half > 0:
            pygame.draw.rect(surf,(30,30,100),(dx,dy+2,half,dh-4)); pygame.draw.rect(surf,(30,30,100),(dx+dw-half,dy+2,half,dh-4))
            for ky in range(dy+8, dy+dh-8, 10): pygame.draw.rect(surf,bc,(dx+3,ky,half-6,1)); pygame.draw.rect(surf,bc,(dx+dw-half+3,ky,half-6,1))
        if self.door_open > 0.1:
            lw = int((dw-4)*self.door_open*0.7); ls = pygame.Surface((lw, dh-8), pygame.SRCALPHA); ls.fill((*self.level_color, int(self.door_open*100))); surf.blit(ls,(dx+(dw-lw)//2, dy+4))
        label = "ABIERTO!" if self.door_open>0.9 else ("ABRIENDO..." if self.door_open>0.05 else "NIVEL BLOQUEADO")
        if int(self.t*3)%2==0: px(surf, label, dx+dw//2, dy+dh//2-6, self.fonts["xs"], bc, center=True)
    def _draw_stats(self, surf):
        rx,ry,rw,rh = 0,PANEL_Y,STATS_W,PANEL_H; pygame.draw.rect(surf,(10,10,40),(rx,ry,rw,rh)); draw_border_box(surf,(rx,ry,rw,rh),BORDER_COL)
        role_col = HACKER_COL if self.my_role=="hacker" else NERD_COL
        px(surf,self.name[:8].upper(), rx+8,ry+8,self.fonts["sm"],role_col); px(surf,self.my_role.upper(), rx+8,ry+24,self.fonts["xs"],DIM_COL)
        stats=[("POWER",self.power,100,role_col),("KARMA",min(self.karma,200),200,C64["yellow"]),("HAMBRE",self.pet_hunger,100,C64["lt_green"])]
        for i,(lbl,val,maxv,col) in enumerate(stats):
            sy=ry+48+i*38; px(surf,lbl,rx+8,sy,self.fonts["xs"],DIM_COL); draw_bar(surf,rx+8,sy+13,rw-16,8,val,maxv,col); px(surf,str(val),rx+rw-8,sy,self.fonts["xs"],col,right=True)
        if self.mode == "cpu":
            ty=ry+48+3*38+4; tr=self.time_remaining; t_col=OK_COL if tr>60 else (C64["yellow"] if tr>30 else ERR_COL)
            px(surf,f"TIEMPO: {int(tr)}s",rx+rw//2,ty,self.fonts["xs"],t_col,center=True); draw_bar(surf,rx+8,ty+14,rw-16,6,int(tr),120,t_col); py2=ty+28
        else: py2=ry+48+3*38+4; px(surf,"★ MODO SOLO ★",rx+rw//2,py2,self.fonts["xs"],C64["lt_green"],center=True); py2+=20
        px(surf,f"NIVEL {self.level_index+1}/6",rx+8,py2,self.fonts["xs"],C64["white"]); px(surf,f"WINS: {self.wins}",rx+8,py2+16,self.fonts["xs"],C64["yellow"])
        if self.has_pet and self.pet_data and "poder" in self.pet_data: px(surf, f"POD:{self.pet_data['poder'][:14]}", rx+8, ry+rh-32, self.fonts["xs"], C64["yellow"])
        px(surf, "CTRL+F=ALIMENTAR",rx+rw//2,ry+rh-16,self.fonts["xs"],DIM_COL,center=True)
    def _draw_console(self, surf):
        rx,ry,rw,rh = CONSOLE_X,PANEL_Y,CONSOLE_W,PANEL_H; pygame.draw.rect(surf,(6,6,26),(rx,ry,rw,rh)); draw_border_box(surf,(rx,ry,rw,rh),BORDER_COL)
        lv=LEVELS[self.level_index]; role_col=HACKER_COL if self.my_role=="hacker" else NERD_COL; cmds=list(lv["comandos_validos"].keys())
        px(surf,f"NIVEL {lv['id']}: {lv['titulo']}", rx+10,ry+8,self.fonts["md"],self.level_color); px(surf, "COMANDOS:  "+"   ".join(cmds), rx+10,ry+28,self.fonts["sm"],C64["cyan"]); pygame.draw.line(surf,BORDER_COL,(rx,ry+46),(rx+rw,ry+46),1)
        if self.step_index < len(self.pasos):
            paso_actual = self.pasos[self.step_index]
            if self.has_pet: cmd_parts = paso_actual["cmd"].split(); display_cmd = f"{cmd_parts[0]}({cmd_parts[1]})" if len(cmd_parts)==2 else paso_actual["cmd"]
            else: display_cmd = paso_actual["cmd"]
            draw_border_box(surf,(rx+8,ry+52,rw-16,58),self.level_color,fill=(8,20,40),thickness=2)
            px(surf, "ESCRIBI ESTE COMANDO:", rx+rw//2,ry+56,self.fonts["xs"],DIM_COL,center=True)
            flash_col = self.level_color if int(self.blink*2)%2==0 else C64["white"]
            px(surf, display_cmd, rx+rw//2, ry+70, self.fonts["lg"], flash_col, center=True)
            px(surf, paso_actual["desc"][:50], rx+rw//2, ry+96, self.fonts["xs"], DIM_COL, center=True)
        pygame.draw.line(surf,BORDER_COL,(rx,ry+118),(rx+rw,ry+118),1)
        paso_y=ry+124
        for i,paso in enumerate(self.pasos):
            if paso_y+15 > ry+rh-100: px(surf,f"  ...{len(self.pasos)-i} pasos mas", rx+10,paso_y,self.fonts["xs"],DIM_COL); break
            if i < self.step_index: col=C64["mid_grey"]; prefix="✓ "
            elif i==self.step_index: col=self.level_color; prefix="► "
            else: col=(50,50,90); prefix="  "
            if self.has_pet: cmd_parts = paso["cmd"].split(); show_cmd = f"{cmd_parts[0]}({cmd_parts[1]})" if len(cmd_parts)==2 else paso["cmd"]
            else: show_cmd = paso["cmd"]
            px(surf,f" {prefix} {i+1}. {show_cmd}", rx+10,paso_y,self.fonts["xs"],col); paso_y+=16
        pygame.draw.line(surf,BORDER_COL,(rx,ry+rh-82),(rx+rw,ry+rh-82),1)
        log_y=ry+rh-80
        for entry in self.log[-3:]: px(surf,entry["msg"],rx+12,log_y,self.fonts["xs"],entry["color"]); log_y+=18
        pygame.draw.line(surf,BORDER_COL,(rx,ry+rh-38),(rx+rw,ry+rh-38),1)
        draw_border_box(surf,(rx+6,ry+rh-36,rw-12,30),role_col,fill=(0,0,20),thickness=2)
        cur="|" if int(self.blink*3)%2==0 else "  "
        px(surf,f"► {self.input_text}{cur}", rx+16,ry+rh-30,self.fonts["md"],CURSOR_COL)
        if self.result_t > 0: alpha = min(1.0, self.result_t); col=tuple(int(c*alpha) for c in self.result_col); px(surf,self.result_msg,rx+rw//2,ry+rh-108,self.fonts["lg"],col,center=True)
