# games/duck_hunt/powerups.py
import pygame
import random
import math
from core.constants import SCREEN_W, SCREEN_H, RED, YELLOW, BLUE, ORANGE, WHITE, BLACK

class PowerUp:
    def __init__(self):
        self.type = random.choice(["DoubleDamage", "ExtraAmmo", "TimeFreeze", "Bomb"])
        self.x = random.randint(100, SCREEN_W-100)
        self.y = -50
        self.vy = random.uniform(1.0, 2.5)
        self.alive = True
        self.anim = 0
        self.radius = 20
        
    def update(self):
        self.y += self.vy
        self.anim += 1
        if self.y > SCREEN_H:
            self.alive = False
            
    def get_rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius*2, self.radius*2)
        
    def draw(self, surface):
        if not self.alive: return
        
        pulse = math.sin(self.anim * 0.1) * 3
        r = self.radius + pulse
        
        color_map = {
            "DoubleDamage": RED,
            "ExtraAmmo": YELLOW,
            "TimeFreeze": BLUE,
            "Bomb": ORANGE
        }
        color = color_map.get(self.type, WHITE)
        
        # Outer glow
        pygame.draw.circle(surface, (*color, 150), (int(self.x), int(self.y)), int(r + 5))
        # Inner circle
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(r))
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(r), 2)
        
        # Icon
        font = pygame.font.Font(None, 24)
        icon_map = {
            "DoubleDamage": "x2",
            "ExtraAmmo": "+5",
            "TimeFreeze": "T",
            "Bomb": "B"
        }
        txt = font.render(icon_map[self.type], True, BLACK)
        surface.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))
