# games/space_shooter/powerups.py
import pygame
import math
from core.constants import SCREEN_H, GREEN, YELLOW, CYAN, MAGENTA, WHITE, BLACK

class SpacePowerUp:
    def __init__(self, x, y, type_):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.type = type_ # 'Laser', 'Shield', 'Triple', 'Nuke'
        self.vy = 2
        self.anim = 0
        self.alive = True
        
    def update(self):
        self.anim += 1
        self.rect.y += self.vy
        if self.rect.y > SCREEN_H:
            self.alive = False
            
    def draw(self, surface):
        if not self.alive: return
        cx, cy = self.rect.centerx, self.rect.centery
        
        colors = {
            'Laser': MAGENTA,
            'Shield': CYAN,
            'Triple': YELLOW,
            'Nuke': GREEN
        }
        color = colors.get(self.type, WHITE)
        
        pulse = math.sin(self.anim * 0.1) * 3
        
        pygame.draw.rect(surface, color, (self.rect.x - pulse, self.rect.y - pulse, self.rect.w + pulse*2, self.rect.h + pulse*2), border_radius=4)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=4)
        
        font = pygame.font.Font(None, 24)
        text = font.render(self.type[0], True, BLACK)
        surface.blit(text, text.get_rect(center=(cx, cy)))
