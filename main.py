"""Punto de entrada principal para KidsLab."""

import asyncio
import logging
import sys
from typing import Final

import pygame

# Importamos la nueva pantalla visual del juego
from src.screens import HakerBoxScreen

SCREEN_WIDTH: Final[int] = 800
SCREEN_HEIGHT: Final[int] = 600
FPS: Final[int] = 60


async def main() -> None:
    """Bucle principal asíncrono compatible con WASM/Pygbag."""
    pygame.init()

    try:
        pygame.mixer.init()
    except pygame.error as e:
        logging.warning(f"Audio no detectado ({e}).")

    pantalla: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("🧪 KidsLab · HakerBox")
    reloj: pygame.time.Clock = pygame.time.Clock()

    # Instanciamos el juego
    juego_actual = HakerBoxScreen(pantalla)
    esta_corriendo: bool = True

    while esta_corriendo:
        # Procesamiento de Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                esta_corriendo = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                esta_corriendo = False
            else:
                # Si no es salir, le pasamos el evento al juego para que lea el teclado
                juego_actual.procesar_evento(evento)

        if not esta_corriendo:
            break

        # Renderizado delegando a la pantalla del juego
        juego_actual.renderizar()

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
