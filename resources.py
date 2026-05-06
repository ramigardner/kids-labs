# resources.py
import pygame
import math
import random
from config import C64, W, H

class SFX:
    def __init__(self):
        self.initialized = False
    def init(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.initialized = True
        except Exception as e:
            print(f"[Sonido] No se pudo inicializar: {e}")
    def play(self, name):
        if not self.initialized: return
        if name == "piece": self.beep(880, 50, "square", 0.12)
        elif name == "error": self.beep(440, 100, "square", 0.15)
        elif name == "win": self.beep(1046, 200, "square", 0.2)
        elif name == "pet": self.beep(1318, 80, "square", 0.12)
        elif name == "door": self.beep(392, 80, "square", 0.1)
    
    def beep(self, freq, duration_ms, wave_type="square", volume=0.3):
        if not self.initialized: return
        try:
            import numpy as np
            sample_rate = 44100
            n_samples = int(sample_rate * duration_ms / 1000)
            t = np.linspace(0, duration_ms/1000, n_samples, endpoint=False)
            wave = np.where((t * freq) % 1.0 < 0.5, 1.0, -1.0) if wave_type == "square" else np.sin(2 * np.pi * freq * t)
            fade = np.ones(n_samples)
            fade_len = min(int(n_samples * 0.1), 100)
            if fade_len > 0: fade[-fade_len:] = np.linspace(1, 0, fade_len)
            wave = (wave * fade * volume * 32767).astype(np.int16)
            stereo = np.column_stack([wave, wave])
            sound = pygame.sndarray.make_sound(stereo)
            sound.play()
        except Exception:
            pass

sfx = SFX()

def load_fonts():
    mono = pygame.font.match_font("px437ibmvga8x16,couriernew,lucidaconsole,monospace,courier")
    try:
        return {
            "title": pygame.font.Font(mono, 22),
            "lg": pygame.font.Font(mono, 18),
            "md": pygame.font.Font(mono, 14),
            "sm": pygame.font.Font(mono, 12),
            "xs": pygame.font.Font(mono, 10),
            "emoji": pygame.font.SysFont("segoeuiemoji,noto emoji", 26),
        }
    except Exception:
        return {k: pygame.font.SysFont("monospace", s) for k, s in [("title",22),("lg",18),("md",14),("sm",12),("xs",10),("emoji",24)]}
