# games/duck_hunt/background.py
import pygame
from core.constants import SCREEN_W, SCREEN_H

class DuckHuntBackground:
    def __init__(self):
        self.scroll = 0

    def draw(self, surface):
        self.scroll += 0.5
        
        # Sky gradient (Sunset)
        for i in range(SCREEN_H):
            ratio = i / SCREEN_H
            r = int(180 + ratio*75)
            g = int(100 + ratio*80)
            b = int(40 + ratio*60)
            pygame.draw.line(surface, (r, g, b), (0, i), (SCREEN_W, i))

        # Parallax clouds
        for cx, cy, size, speed in [
            (200, 100, 1.0, 1.0), 
            (600, 80, 0.8, 0.8), 
            (900, 120, 1.2, 1.2),
            (100, 180, 0.6, 0.6),
            (500, 200, 0.9, 0.9)
        ]:
            pos_x = (cx - self.scroll * speed) % (SCREEN_W + 200) - 100
            
            # Base cloud shape
            c_color = (255, 240, 230)
            pygame.draw.ellipse(surface, c_color, (pos_x, cy, 120*size, 50*size))
            pygame.draw.ellipse(surface, c_color, (pos_x+30*size, cy-25*size, 90*size, 50*size))

        # Distant mountains
        pygame.draw.polygon(surface, (120, 60, 40), [(0, SCREEN_H-80), (300, SCREEN_H-250), (600, SCREEN_H-80)])
        pygame.draw.polygon(surface, (100, 50, 30), [(400, SCREEN_H-80), (750, SCREEN_H-300), (SCREEN_W, SCREEN_H-80)])

        # Ground
        pygame.draw.rect(surface, (60, 140, 40), (0, SCREEN_H-80, SCREEN_W, 80))
        pygame.draw.rect(surface, (50, 110, 30), (0, SCREEN_H-80, SCREEN_W, 12))
