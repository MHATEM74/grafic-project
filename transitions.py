# ui/transitions.py
import pygame
from core.constants import SCREEN_W, SCREEN_H, BLACK, FPS

def fade_transition(surface, clock, color=BLACK, speed=8):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H))
    overlay.fill(color)
    for alpha in range(0, 256, speed):
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0,0))
        pygame.display.flip()
        clock.tick(FPS)
    for alpha in range(255, -1, -speed):
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0,0))
        pygame.display.flip()
        clock.tick(FPS)
