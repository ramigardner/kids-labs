# entities.py
import pygame
import math
import random
import time
from config import CELL, C64, HACKER_COL, NERD_COL, PET_TYPES, ERR_COL, DIM_COL
from resources import sfx

class Frog:
    def __init__(self, role: str, ox: int, oy: int, color, total_steps: int):
        self.role = role; self.color = color; self.trail = []
        self.angle = 90.0; self.cx = 5.0; self.cy = 5.0
        self.anim_x = float(ox + self.cx * CELL); self.anim_y = float(oy + self.cy * CELL)
        self.target_px = self.anim_x; self.target_py = self.anim_y
        self.ox = ox; self.oy = oy; self.step_index = 0; self.total_steps = total_steps
        self.error_shake = 0.0; self.jump_t = 0.0; self.jumping = False; self.t = 0.0; self.particles = []
    
    def execute(self, action):
        if action[0] == "repeat":
            _, times, actions = action
            for _ in range(times):
                for a in actions:
                    self.execute(a)
            return
        elif action[0] == "if":
            _, condition, actions = action
            # Por ahora, 'bug' siempre es True si hay partículas cerca o simplemente True para el nivel
            if condition == "bug":
                for a in actions:
                    self.execute(a)
            return

        cmd, val = action; moved = False
        if cmd == "fd":
            rad = math.radians(self.angle)
            nx = self.cx + math.cos(rad) * val; ny = self.cy - math.sin(rad) * val
            self.trail.append((self.cx, self.cy, nx, ny, self.color))
            self.cx, self.cy = nx, ny
            self.target_px = self.ox + nx * CELL; self.target_py = self.oy + ny * CELL
            self.jumping = True; self.jump_t = 0.0; moved = True
        elif cmd == "bk":
            rad = math.radians(self.angle)
            nx = self.cx - math.cos(rad) * val; ny = self.cy + math.sin(rad) * val
            self.trail.append((self.cx, self.cy, nx, ny, self.color))
            self.cx, self.cy = nx, ny
            self.target_px = self.ox + nx * CELL; self.target_py = self.oy + ny * CELL
            self.jumping = True; self.jump_t = 0.0; moved = True
        elif cmd in ("rt", "lt"):
            self.angle += val if cmd == "lt" else -val
        self.step_index += 1
        if moved:
            self.particles.append({"x": self.anim_x, "y": self.anim_y, "vx": random.uniform(-2,2), "vy": random.uniform(-3,-1), "life": 1.0, "emoji": random.choice(["🐛", "🦟", "🪲", "🐞"])})
    
    def shake_error(self):
        self.error_shake = 1.0
    
    def update(self, dt):
        self.t += dt; self.error_shake = max(0, self.error_shake - dt*4)
        if self.jumping:
            self.jump_t = min(1.0, self.jump_t + dt*4)
            self.anim_x += (self.target_px - self.anim_x) * min(1, dt*8)
            self.anim_y += (self.target_py - self.anim_y) * min(1, dt*8)
            if self.jump_t >= 1.0: self.jumping = False; self.anim_x = self.target_px; self.anim_y = self.target_py
        for p in self.particles: p["x"] += p["vx"]; p["y"] += p["vy"]; p["vy"] += 0.15; p["life"] -= dt*1.2
        self.particles = [p for p in self.particles if p["life"] > 0]
    
    def draw(self, surf, fonts):
        for seg in self.trail:
            x0,y0,x1,y1,col = seg
            px0 = int(self.ox + x0*CELL); py0 = int(self.oy + y0*CELL)
            px1 = int(self.ox + x1*CELL); py1 = int(self.oy + y1*CELL)
            for th in [5,3,2]:
                dim = tuple(max(0,int(c*0.35)) for c in col)
                pygame.draw.line(surf, dim, (px0,py0),(px1,py1), th)
            pygame.draw.line(surf, col, (px0,py0),(px1,py1), 2)
        for p in self.particles:
            alpha = int(p["life"]*220)
            bug_surf = fonts["xs"].render(p["emoji"], True, C64["white"]); bug_surf.set_alpha(alpha)
            surf.blit(bug_surf, (int(p["x"])-6, int(p["y"])-6))
        shake = int(self.error_shake*5*math.sin(self.error_shake*25))
        fx = int(self.anim_x) + shake; fy = int(self.anim_y)
        if self.jumping: arc = math.sin(self.jump_t * math.pi) * 12; fy -= int(arc)
        col = self.color; dk = tuple(max(0,c-80) for c in col); lt = tuple(min(255,c+60) for c in col)
        err = self.error_shake > 0; body_col = C64["red"] if err else col; eye_col = HACKER_COL if self.role=="hacker" else NERD_COL
        pygame.draw.ellipse(surf, (0,0,0), (fx-14, fy+20, 28, 8))
        pygame.draw.ellipse(surf, dk, (fx-18, fy+8, 14, 10)); pygame.draw.ellipse(surf, dk, (fx+4, fy+8, 14, 10))
        pygame.draw.ellipse(surf, body_col, (fx-16, fy+7, 10, 8)); pygame.draw.ellipse(surf, body_col, (fx+6, fy+7, 10, 8))
        pygame.draw.ellipse(surf, dk, (fx-18, fy-2, 10, 7)); pygame.draw.ellipse(surf, dk, (fx+8, fy-2, 10, 7))
        pygame.draw.ellipse(surf, body_col, (fx-16, fy-1, 8, 6)); pygame.draw.ellipse(surf, body_col, (fx+8, fy-1, 8, 6))
        pygame.draw.ellipse(surf, body_col, (fx-13, fy-8, 26, 22)); pygame.draw.ellipse(surf, lt, (fx-8, fy-2, 16, 14))
        pygame.draw.ellipse(surf, body_col, (fx-11, fy-22, 22, 18))
        pygame.draw.circle(surf, body_col, (fx-8, fy-22), 6); pygame.draw.circle(surf, body_col, (fx+8, fy-22), 6)
        pygame.draw.circle(surf, eye_col, (fx-8, fy-22), 5); pygame.draw.circle(surf, eye_col, (fx+8, fy-22), 5)
        pygame.draw.circle(surf, C64["black"], (fx-7, fy-22), 2); pygame.draw.circle(surf, C64["black"], (fx+7, fy-22), 2)
        pygame.draw.circle(surf, C64["white"], (fx-6, fy-23), 1); pygame.draw.circle(surf, C64["white"], (fx+8, fy-23), 1)
        if err: pygame.draw.line(surf, C64["white"], (fx-5,fy-10),(fx+5,fy-10), 2)
        else: pygame.draw.arc(surf, C64["white"], pygame.Rect(fx-5, fy-13, 10, 6), math.pi, 2*math.pi, 2)
        pygame.draw.circle(surf, dk, (fx-3, fy-14), 2); pygame.draw.circle(surf, dk, (fx+3, fy-14), 2)
        rad = math.radians(self.angle); ax = int(fx + math.cos(rad)*16); ay = int(fy - math.sin(rad)*16)
        pygame.draw.line(surf, C64["white"], (fx,fy-5), (ax,ay), 2)
        if self.role == "hacker":
            pygame.draw.ellipse(surf, (20,10,50), (fx-12, fy-32, 24, 14))
            pygame.draw.ellipse(surf, HACKER_COL, (fx-12, fy-32, 24, 14), 2)
            pygame.draw.rect(surf, HACKER_COL, (fx-14, fy-24, 4, 6)); pygame.draw.rect(surf, HACKER_COL, (fx+10, fy-24, 4, 6))
        else:
            pygame.draw.rect(surf, C64["yellow"], (fx-10, fy-26, 8, 5), 2); pygame.draw.rect(surf, C64["yellow"], (fx+2, fy-26, 8, 5), 2)
            pygame.draw.line(surf, C64["yellow"], (fx-2,fy-24),(fx+2,fy-24), 2)

class CPUPlayer:
    SPEED = [(6.0, 14.0), (4.0, 9.0), (2.0, 5.0), (1.0, 3.0)]
    def __init__(self, level_index=0):
        self.step_index = 0; self.next_action_at = 0.0; self.power = 50; self.karma = 0; self.has_pet = False; self.pet = {}; self.wins = 0; self.finished_level = False; self.error_rate = max(0.05, 0.20 - level_index * 0.04); self.level_index = level_index; self._schedule_next(delay=self.SPEED[min(level_index, 3)][1])
    
    def _schedule_next(self, delay=None):
        if delay is None: mn, mx = self.SPEED[min(self.level_index, 3)]; delay = random.uniform(mn, mx)
        self.next_action_at = time.time() + delay
    
    def reset_level(self):
        self.step_index = 0; self.finished_level = False; mn, mx = self.SPEED[min(self.level_index, 3)]; self._schedule_next(delay=random.uniform(mn * 0.6, mx * 0.6))
    
    def tick(self, pasos, frog, game) -> bool:
        if self.finished_level: return False
        if time.time() < self.next_action_at: return False
        if self.step_index >= len(pasos): return False
        step = pasos[self.step_index]
        if random.random() < self.error_rate:
            frog.shake_error(); sfx.play("error"); game.add_log("CPU: comando incorrecto", ERR_COL); self._schedule_next(delay=random.uniform(5, 10)); return False
        frog.execute(step["action"]); sfx.play("piece"); self.step_index += 1; self.karma += 5; self.power = min(100, self.power + 3); game.add_log(f"CPU: {step['cmd']}", DIM_COL)
        if self.step_index >= len(pasos):
            self.finished_level = True; self.wins += 1; self.karma += 50
            if not self.has_pet: self.has_pet = True; self.pet = random.choice(PET_TYPES).copy(); self.pet["hunger"] = 100
            sfx.play("win"); game.add_log("CPU completó el nivel!", ERR_COL); return True
        self._schedule_next(); return False
