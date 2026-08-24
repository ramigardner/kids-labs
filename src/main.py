"""Punto de entrada principal para KidsLab - Oracle Kids Edition."""

import asyncio
import logging
import sys
from typing import Final

import pygame

# Importamos las pantallas del juego completo
from screens import LoginSolo, RoleReveal, RetroLoader, TriviaScreen, GameOverScreen, GameSolo
from config import W, H, FPS

SCREEN_WIDTH: Final[int] = W
SCREEN_HEIGHT: Final[int] = H


async def main() -> None:
    """Bucle principal asíncrono compatible con WASM/Pygbag."""
    pygame.init()
    
    try:
        pygame.mixer.init()
    except pygame.error as e:
        logging.warning(f"Audio no detectado ({e}).")

    pantalla: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("🧪 KidsLab · Oracle Kids - Hackers vs Nerds")
    reloj: pygame.time.Clock = pygame.time.Clock()
    
    # Inicializamos fuentes
    fuentes = {
        "title": pygame.font.Font(None, 48),
        "lg": pygame.font.Font(None, 42),
        "md": pygame.font.Font(None, 32),
        "sm": pygame.font.Font(None, 24),
        "xs": pygame.font.Font(None, 18),
        "emoji": pygame.font.Font(None, 36),
    }
    
    # Estado del juego
    estado = "login"
    login_screen = LoginSolo(fuentes)
    game_screen = None
    role_screen = None
    loader_screen = None
    trivia_screen = None
    game_over_screen = None
    
    nivel_actual = 0
    player_data = {"name": "", "mode": "cpu", "wins": 0, "level_wins": 0}
    
    esta_corriendo: bool = True

    while esta_corriendo:
        # Procesamiento de Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                esta_corriendo = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                esta_corriendo = False
            else:
                # Delegar eventos según el estado actual
                if estado == "login":
                    login_screen.handle(evento)
                elif estado == "game":
                    game_screen.handle_event(evento)
                elif estado == "gameover":
                    game_over_screen.handle_event(evento)

        if not esta_corriendo:
            break

        # Actualizar lógica según estado
        if estado == "login":
            if login_screen.done:
                player_data["name"] = login_screen.result["name"]
                player_data["mode"] = login_screen.result["mode"]
                estado = "loader"
                loader_screen = RetroLoader(fuentes, next_level=0)
        
        elif estado == "loader":
            loader_screen.update(0.016)
            if loader_screen.done:
                nivel_actual = 0
                game_screen = GameSolo(fuentes, player_data["name"], nivel_actual, player_data["mode"])
                estado = "role"
                role_screen = RoleReveal(fuentes, game_screen.my_role, nivel_actual + 1)
        
        elif estado == "role":
            role_screen.update(0.016)
            if role_screen.done:
                estado = "playing"
        
        elif estado == "playing":
            game_screen.update(0.016)
            if game_screen.level_done:
                # Nivel completado, mostrar trivia
                estado = "trivia"
                player_won = game_screen.wins > (game_screen.cpu.wins if game_screen.cpu else 0)
                trivia_screen = TriviaScreen(fuentes, nivel_actual, player_won)
                if player_won:
                    player_data["level_wins"] += 1
        
        elif estado == "trivia":
            trivia_screen.update(0.016)
            if trivia_screen.done:
                nivel_actual += 1
                if nivel_actual >= 6:
                    # Juego completado
                    estado = "gameover"
                    game_over_screen = GameOverScreen(fuentes, player_data["level_wins"], 6 - player_data["level_wins"], player_data["name"], player_data["mode"])
                else:
                    # Siguiente nivel
                    estado = "loader"
                    loader_screen = RetroLoader(fuentes, next_level=nivel_actual, pet_data=game_screen.pet_data if game_screen.has_pet else None)
                    game_screen = GameSolo(fuentes, player_data["name"], nivel_actual, player_data["mode"])
                    estado = "role"
                    role_screen = RoleReveal(fuentes, game_screen.my_role, nivel_actual + 1)
        
        elif estado == "gameover":
            if game_over_screen.restart_requested:
                # Reiniciar juego
                estado = "login"
                login_screen = LoginSolo(fuentes)
                player_data = {"name": "", "mode": "cpu", "wins": 0, "level_wins": 0}

        # Renderizado
        pantalla.fill((16, 16, 64))
        
        if estado == "login":
            login_screen.draw(pantalla)
        elif estado == "loader":
            loader_screen.draw(pantalla)
        elif estado == "role":
            role_screen.draw(pantalla)
        elif estado == "playing":
            game_screen.draw(pantalla)
        elif estado == "trivia":
            trivia_screen.draw(pantalla)
        elif estado == "gameover":
            game_over_screen.draw(pantalla)
        
        pygame.display.flip()
        reloj.tick(FPS)
        await asyncio.sleep(0)

    if pygame.mixer.get_init():
        pygame.mixer.quit()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    