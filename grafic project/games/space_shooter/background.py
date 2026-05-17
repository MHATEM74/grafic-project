# games/space_shooter/background.py
import pygame
import random
from core.constants import SCREEN_W, SCREEN_H, DARKER

class StarfieldBackground:
    def __init__(self):
        self.stars = []
        # 4 layers of stars (x, y, speed, size, color)
        for _ in range(150):
            layer = random.choice([1, 2, 3, 4])
            x = random.randint(0, SCREEN_W)
            y = random.randint(0, SCREEN_H)
            
            if layer == 1:
                self.stars.append([x, y, 0.5, 1, (100, 100, 150)])
            elif layer == 2:
                self.stars.append([x, y, 1.5, 2, (150, 150, 200)])
            elif layer == 3:
                self.stars.append([x, y, 3.0, 2, (200, 200, 255)])
            else:
                self.stars.append([x, y, 5.0, 3, (255, 255, 255)])

    def draw(self, surface):
        surface.fill(DARKER)
        
        # Deep space nebula effect (static)
        for i in range(5):
            pygame.draw.ellipse(surface, (20, 20, 40), (-100 + i*300, 100 + (i%2)*200, 400, 300))

        for star in self.stars:
            star[1] += star[2] # move y
            if star[1] > SCREEN_H:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_W)
                
            pygame.draw.rect(surface, star[4], (int(star[0]), int(star[1]), star[3], star[3]))
