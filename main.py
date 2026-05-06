# main.py
import pygame
import sys
from config import *
from resources import sfx, load_fonts
from ui_utils import draw_demo_banner, draw_fade
from screens import LoginSolo, RoleReveal, GameSolo, TriviaScreen, RetroLoader, GameOverScreen

class App:
    def __init__(self):
        pygame.init(); pygame.mixer.init(); pygame.display.set_caption("🧪 KidsLab — Oracle Kids: Hackers vs Nerds Edition")
        self.screen = pygame.display.set_mode((W, H)); self.clock = pygame.time.Clock(); self.fonts = load_fonts(); sfx.init()
        self.state = "login"; self.login = LoginSolo(self.fonts); self.reveal = None; self.game = None; self.trivia = None; self.loader = None; self.gameover = None
        self.player_name = ""; self.player_wins = 0; self.cpu_wins = 0; self.game_mode = "cpu"; self._demo_t = 0.0; self._pending_level = 0; self._saved_pet = None; self._saved_hunger = 100
        self.fade_alpha = 0; self.target_state = None; self.transitioning = False

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                self._event(ev)
            self._update(dt); self._draw(); pygame.display.flip()

    def _event(self, ev):
        if self.transitioning: return
        if self.state == "gameover" and self.gameover:
            self.gameover.handle_event(ev)
            if self.gameover.restart_requested:
                self._change_state("login")
                self.login = LoginSolo(self.fonts); self.player_wins = 0; self.cpu_wins = 0; self.game = None; self.gameover = None; self.trivia = None; self.reveal = None; self.loader = None; self._saved_pet = None; self._saved_hunger = 100; self._pending_level = 0
            return
        if self.state == "login":
            self.login.handle(ev)
            if self.login.done:
                self.player_name = self.login.result["name"]
                self.game_mode = self.login.result["mode"]
                self._start_level(0)
        elif self.state == "game" and self.game:
            self.game.handle_event(ev)

    def _change_state(self, new_state):
        self.target_state = new_state
        self.transitioning = True

    def _start_level(self, idx):
        role = ROLES_PER_LEVEL[idx % len(ROLES_PER_LEVEL)]
        self.reveal = RoleReveal(self.fonts, role, idx+1)
        self._change_state("reveal")
        self._pending_level = idx

    def _launch_game(self, idx):
        self.game = GameSolo(self.fonts, self.player_name, idx, mode=self.game_mode)
        if self._saved_pet:
            self.game.has_pet = True; self.game.pet_data = self._saved_pet; self.game.pet_hunger = self._saved_hunger
            pet = self._saved_pet
            self.game.add_log(f"{pet['emoji']} {pet['name']} te acompaña — nivel {idx+1}/6", C64["yellow"])
            self.game.add_log("⚠️ Recordá: comandos con PARÉNTESIS — EJ: FD(50)", C64["cyan"])
        self.game.wins = self.player_wins; self._change_state("game")

    def _update(self, dt):
        if self.transitioning:
            self.fade_alpha = min(255, self.fade_alpha + dt * 1000)
            if self.fade_alpha >= 255:
                self.state = self.target_state
                self.transitioning = False
            return
        
        self.fade_alpha = max(0, self.fade_alpha - dt * 500)
        
        if self.state == "reveal" and self.reveal:
            self.reveal.update(dt)
            if self.reveal.done: self._launch_game(self._pending_level)
        elif self.state == "game" and self.game:
            result = self.game.update(dt)
            if result == "trivia":
                player_won = self.game.level_done
                if self.game_mode == "cpu":
                    self.player_wins += 1 if player_won else 0
                    self.cpu_wins += 1 if not player_won else 0
                else:
                    self.player_wins += 1
                self._saved_pet = self.game.pet_data if self.game.has_pet else None
                self._saved_hunger = self.game.pet_hunger
                self.trivia = TriviaScreen(self.fonts, self.game.level_index, player_won)
                self._change_state("trivia")
        elif self.state == "trivia" and self.trivia:
            self.trivia.update(dt)
            if self.trivia.done:
                next_idx = (self.game.level_index + 1) if self.game else 1
                if next_idx >= len(LEVELS):
                    self.gameover = GameOverScreen(self.fonts, self.player_wins, self.cpu_wins, self.player_name, self.game_mode)
                    self._change_state("gameover")
                else:
                    pet = self._saved_pet
                    self.loader = RetroLoader(self.fonts, next_idx, pet_data=pet)
                    self._pending_level = next_idx
                    self._change_state("loading")
        elif self.state == "loading" and self.loader:
            self.loader.update(dt)
            if self.loader.done: self.loader = None; self._start_level(self._pending_level)

    def _draw(self):
        if self.state == "login": self.login.draw(self.screen)
        elif self.state == "reveal" and self.reveal: self.reveal.draw(self.screen)
        elif self.state == "game" and self.game: self.game.draw(self.screen)
        elif self.state == "loading" and self.loader: self.loader.draw(self.screen)
        elif self.state == "trivia" and self.trivia: self.trivia.draw(self.screen)
        elif self.state == "gameover" and self.gameover: self.gameover.draw(self.screen)
        else: self.screen.fill(BG_COLOR)
        
        if self.fade_alpha > 0:
            draw_fade(self.screen, self.fade_alpha)
            
        draw_demo_banner(self.screen, self.fonts, self._demo_t); self._demo_t += 0.016

if __name__ == "__main__":
    App().run()
