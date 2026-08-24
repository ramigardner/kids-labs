"""
ASPR Oracle Synth v1.0 — Ludic Musical Module
C64 Aesthetic · 8-bit Synthesis · Offline/Online (UDP/LAN)
Mapea la Fórmula del Karma ASPR a parámetros musicales estructurales.
Diseñado para KidsLab, Detective Lab y nodos Oracle.
"""
import pygame, sys, numpy as np, math, random, time, socket, threading, json

# ───────────────────────────────────────────────────────────────
# CONSTANTES & PALETA C64
# ───────────────────────────────────────────────────────────────
W, H, FPS = 1024, 640, 60
C64 = {
    "bg": (16, 16, 64), "grid": (28, 28, 88), "border": (100, 100, 255),
    "white": (255, 255, 240), "cyan": (84, 255, 255), "yellow": (240, 240, 80),
    "green": (112, 255, 112), "red": (255, 80, 80), "grey": (128, 128, 192),
    "dim": (50, 50, 110), "magenta": (220, 80, 220), "orange": (255, 160, 40)
}
KARMA_MAP = {
    "M": {"label": "MEMORY",   "color": C64["cyan"],    "weight": 0.30, "param": "Pitch"},
    "C": {"label": "CYCLES",   "color": C64["yellow"],  "weight": 0.25, "param": "Tempo"},
    "A": {"label": "ANCHOR",   "color": C64["green"],   "weight": 0.20, "param": "Harmony"},
    "E": {"label": "EFFICIENCY","color": C64["orange"],  "weight": 0.15, "param": "Dynamics"},
    "R": {"label": "CORRECTION","color": C64["magenta"], "weight": 0.10, "param": "Modulation"}
}
SCALE_C_MAJOR = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

# ───────────────────────────────────────────────────────────────
# MOTOR DE AUDIO 8-BIT (Síntesis NumPy · Sin archivos)
# ───────────────────────────────────────────────────────────────
class OracleAudio:
    def __init__(self):
        self.ready = False
        self.cache = {}
        self.max_poly = 6
        self.active = 0
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            self.ready = True
        except Exception as e:
            print(f"[Audio] Fallback sin mezcla: {e}")

    def _gen_wave(self, freq, dur, wave="square", vol=0.3, mod=0.0):
        sr, n = 22050, int(22050 * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        if wave == "square":
            w = np.where((t * freq) % 1.0 < 0.5, 1.0, -1.0)
        elif wave == "saw":
            w = 2 * (t * freq - np.floor(0.5 + t * freq))
        else:
            w = np.sin(2 * np.pi * freq * t)
        # Envelope (Attack-Decay)
        env = np.ones(n)
        env[:int(n*0.05)] = np.linspace(0, 1, int(n*0.05))
        env[int(n*0.05):] = np.linspace(1, 0.01, len(env)-int(n*0.05))
        # Modulación (R = Correction)
        if mod > 0:
            w *= np.sin(2 * np.pi * (freq * mod) * t)
        return (w * env * vol * 32767).astype(np.int16)

    def play(self, freq, dur=0.18, wave="square", vol=0.3, mod=0.0):
        if not self.ready: return
        key = (freq, dur, wave, vol, mod)
        if key not in self.cache:
            arr = self._gen_wave(freq, dur, wave, vol, mod)
            self.cache[key] = pygame.sndarray.make_sound(np.column_stack([arr, arr]))
        if self.active < self.max_poly:
            self.cache[key].play()
            self.active += 1
            pygame.time.set_timer(pygame.USEREVENT + 99, int(dur*1000))
        return key

    def free_channel(self):
        self.active = max(0, self.active - 1)

audio = OracleAudio()

# ───────────────────────────────────────────────────────────────
# RED OPCIONAL (UDP · LAN/Tailscale Compatible)
# ───────────────────────────────────────────────────────────────
class OracleNet:
    def __init__(self, port=9999, online=False):
        self.port = port
        self.online = online
        self.sock = None
        self.running = False
        if online:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.running = True
            self._start_listener()

    def _start_listener(self):
        self.bind_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind_sock.bind(("0.0.0.0", self.port))
        self.bind_sock.settimeout(0.1)
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while self.running:
            try:
                data, _ = self.bind_sock.recvfrom(256)
                msg = data.decode("utf-8", errors="ignore")
                if msg.startswith("ASPR_NOTE|"):
                    _, freq, dur, vol, mod = msg.split("|")
                    audio.play(float(freq), float(dur), vol=float(vol), mod=float(mod))
            except: pass

    def broadcast(self, freq, dur, vol, mod):
        if self.online and self.sock:
            payload = f"ASPR_NOTE|{freq}|{dur}|{vol}|{mod}"
            self.sock.sendto(payload.encode(), ("255.255.255.255", self.port))

# ───────────────────────────────────────────────────────────────
# UTILIDADES DE DIBUJO (Consistente con KidsLab/Detective)
# ───────────────────────────────────────────────────────────────
def px(surf, text, x, y, font, color=None, center=False, right=False):
    color = color or C64["white"]
    sh = font.render(str(text), False, (0, 0, 0))
    rx = x - sh.get_width()//2 if center else (x - sh.get_width() if right else x)
    surf.blit(sh, (rx+1, y+1))
    r = font.render(str(text), False, color)
    rx2 = x - r.get_width()//2 if center else (x - r.get_width() if right else x)
    surf.blit(r, (rx2, y))
    return r.get_width()

def box(surf, rect, color=None, fill=None, thick=2):
    color = color or C64["border"]
    if fill: pygame.draw.rect(surf, fill, rect)
    pygame.draw.rect(surf, color, rect, thick)
    x, y, w, h = rect
    for cx, cy in [(x,y),(x+w-2,y),(x,y+h-2),(x+w-2,y+h-2)]:
        pygame.draw.rect(surf, C64["white"], (cx, cy, 2, 2))

def scanlines(surf):
    sl = pygame.Surface((W, H), pygame.SRCALPHA)
    for gy in range(0, H, 4): pygame.draw.line(sl, (0, 0, 0, 18), (0, gy), (W, gy))
    surf.blit(sl, (0, 0))

# ───────────────────────────────────────────────────────────────
# INTERFAZ LÚDICA & LÓGICA MUSICAL
# ───────────────────────────────────────────────────────────────
class OracleSynth:
    def __init__(self, online=False):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("🎵 ASPR Oracle Synth v1.0")
        self.clock = pygame.time.Clock()
        self.fonts = self._load_fonts()
        self.net = OracleNet(online=online)
        self.t, self.bpm, self.beat = 0.0, 120, 0
        self.karma_harmony = 0.0
        self.history = []
        self.waveform = np.zeros(200)
        self._setup_keys()

    def _load_fonts(self):
        mono = pygame.font.match_font("px437ibmvga8x16,couriernew,monospace,courier")
        try:
            return {
                "title": pygame.font.Font(mono, 22), "lg": pygame.font.Font(mono, 18),
                "md": pygame.font.Font(mono, 14), "sm": pygame.font.Font(mono, 12),
                "xs": pygame.font.Font(mono, 10)
            }
        except:
            return {k: pygame.font.SysFont("monospace", s) for k,s in [("title",22),("lg",18),("md",14),("sm",12),("xs",10)]}

    def _setup_keys(self):
        self.key_map = {
            pygame.K_a: ("M", 0), pygame.K_s: ("C", 1), pygame.K_d: ("A", 2),
            pygame.K_f: ("E", 3), pygame.K_g: ("R", 4)
        }
        self.key_pos = {
            "M": (W//2 - 250, H - 180), "C": (W//2 - 125, H - 180),
            "A": (W//2, H - 180), "E": (W//2 + 125, H - 180),
            "R": (W//2 + 250, H - 180)
        }
        self.key_states = {k: 0 for k in self.key_map}

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.t += dt
            self._handle_events()
            self._update_audio(dt)
            self._draw()
            pygame.display.flip()

    def _handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.USEREVENT + 99:
                audio.free_channel()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if ev.key in self.key_map:
                    comp, idx = self.key_map[ev.key]
                    self._trigger_note(comp, idx)
                if ev.key == pygame.K_o:
                    self.net.online = not self.net.online

    def _trigger_note(self, comp, idx):
        freq = SCALE_C_MAJOR[(self.beat + idx) % len(SCALE_C_MAJOR)]
        vol = KARMA_MAP[comp]["weight"]
        mod = 0.15 if comp == "R" else 0.0
        dur = 0.2 if comp == "C" else 0.12
        
        audio.play(freq, dur, vol=vol*1.5, mod=mod)
        self.key_states[comp] = 60
        
        # Karma Harmony Score (ritmo estructural)
        target_beat = time.time()
        if self.history and abs(target_beat - self.history[-1]) < (60/self.bpm)*0.4:
            self.karma_harmony = min(100, self.karma_harmony + 5)
        else:
            self.karma_harmony = max(0, self.karma_harmony - 2)
        self.history.append(target_beat)
        
        # Broadcast si está online
        self.net.broadcast(freq, dur, vol*1.5, mod)
        
        # Update waveform visualization
        t = np.linspace(0, 1, 200)
        self.waveform = np.sin(2*np.pi*freq*t) * np.exp(-t*3)

    def _update_audio(self, dt):
        self.beat = (self.t * self.bpm / 60) % 8
        for k in self.key_states:
            if self.key_states[k] > 0:
                self.key_states[k] -= 1

    def _draw(self):
        self.screen.fill(C64["bg"])
        # Fondo terminal
        for gx in range(0, W, 32): pygame.draw.line(self.screen, C64["grid"], (gx, 0), (gx, H))
        for gy in range(0, H, 32): pygame.draw.line(self.screen, C64["grid"], (0, gy), (W, gy))

        # Header
        px(self.screen, "🎵 ASPR ORACLE SYNTH v1.0", W//2, 12, self.fonts["title"], C64["yellow"], center=True)
        px(self.screen, f"KARMA HARMONY: {self.karma_harmony:.1f}% | BEAT: {int(self.beat)+1}/8", W//2, 36, self.fonts["xs"], C64["grey"], center=True)
        
        # Fórmula Karma
        formula = "K = M·0.30 + C·0.25 + A·0.20 + E·0.15 + R·0.10"
        px(self.screen, formula, W//2, 56, self.fonts["sm"], C64["cyan"], center=True)

        # Métricas Karma
        for i, (comp, data) in enumerate(KARMA_MAP.items()):
            x = 40 + i * 195
            box(self.screen, (x, 80, 180, 120), data["color"], fill=(8,8,30))
            px(self.screen, f"{comp} — {data['label']}", x+90, 88, self.fonts["md"], data["color"], center=True)
            px(self.screen, f"Peso: {data['weight']:.2f} | Param: {data['param']}", x+90, 110, self.fonts["xs"], C64["white"], center=True)
            # Barra de progreso animada
            bar_h = int(60 * abs(math.sin(self.t*3 + i*0.8)))
            pygame.draw.rect(self.screen, data["color"], (x+20, 190-bar_h, 140, 8))

        # Teclado visual
        for comp, (x, y) in self.key_pos.items():
            active = self.key_states[comp] > 0
            col = KARMA_MAP[comp]["color"] if active else C64["dim"]
            fill = (40,40,100) if active else (10,10,40)
            box(self.screen, (x-50, y-20, 100, 40), col, fill=fill, thick=2 if active else 1)
            px(self.screen, comp, x, y-8, self.fonts["lg"], col, center=True)

        # Visualizador de Onda
        wx, wy, ww, wh = W//2 - 200, 240, 400, 100
        box(self.screen, (wx-4, wy-4, ww+8, wh+8), C64["border"], fill=(4,4,20))
        for i in range(0, len(self.waveform)-1, 2):
            x1 = wx + (i/len(self.waveform))*ww
            x2 = wx + ((i+1)/len(self.waveform))*ww
            y1 = wy + wh//2 + int(self.waveform[i]*wh//2)
            y2 = wy + wh//2 + int(self.waveform[i+1]*wh//2)
            pygame.draw.line(self.screen, C64["cyan"], (x1,y1), (x2,y2), 2)

        # Instrucciones & Estado
        px(self.screen, "[A] M  [S] C  [D] A  [F] E  [G] R", W//2, H-110, self.fonts["xs"], C64["grey"], center=True)
        net_stat = "🌐 ONLINE (UDP/Tailscale)" if self.net.online else "🔒 OFFLINE LOCAL"
        px(self.screen, f"ESTADO: {net_stat} | [O] TOGGLE", W//2, H-90, self.fonts["xs"], C64["green"] if self.net.online else C64["yellow"], center=True)

        scanlines(self.screen)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ASPR Oracle Synth")
    parser.add_argument("--lan", action="store_true", help="Enable UDP broadcast for LAN/Tailscale")
    args = parser.parse_args()
    OracleSynth(online=args.lan).run()