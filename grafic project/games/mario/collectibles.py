# games/mario/collectibles.py
import pygame
import math
from core.constants import GOLD, RED, BLUE, WHITE, YELLOW

class Collectible:
    def __init__(self, x, y, type_):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.type = type_ # 'coin', 'mushroom', 'star', 'lightning'
        self.anim = 0
        self.alive = True
        
    def update(self):
        self.anim += 1
        
    def draw(self, surface, offset_x):
        if not self.alive: return
        r = self.rect.move(-offset_x, 0)
        
        y_float = math.sin(self.anim * 0.1) * 3
        
        if self.type == 'coin':
            pygame.draw.circle(surface, GOLD, (r.centerx, r.centery + int(y_float)), 10)
            pygame.draw.circle(surface, YELLOW, (r.centerx, r.centery + int(y_float)), 6)
        elif self.type == 'mushroom':
            pygame.draw.circle(surface, RED, (r.centerx, r.centery + int(y_float) - 5), 10)
            pygame.draw.rect(surface, WHITE, (r.centerx - 6, r.centery + int(y_float) - 5, 12, 10))
            pygame.draw.circle(surface, WHITE, (r.centerx - 4, r.centery + int(y_float) - 8), 3)
            pygame.draw.circle(surface, WHITE, (r.centerx + 4, r.centery + int(y_float) - 8), 3)
        elif self.type == 'star':
            color = GOLD if self.anim % 10 < 5 else WHITE
            pygame.draw.polygon(surface, color, [
                (r.centerx, r.y + int(y_float)),
                (r.right, r.bottom + int(y_float)),
                (r.x, r.centery + int(y_float)),
                (r.right, r.centery + int(y_float)),
                (r.x, r.bottom + int(y_float))
            ])
        elif self.type == 'lightning':
            pygame.draw.polygon(surface, BLUE, [
                (r.centerx + 5, r.y + int(y_float)),
                (r.x, r.centery + int(y_float) + 3),
                (r.centerx + 2, r.centery + int(y_float) + 3),
                (r.centerx - 2, r.bottom + int(y_float)),
                (r.right, r.centery + int(y_float) - 2),
                (r.centerx, r.centery + int(y_float) - 2)
            ])
