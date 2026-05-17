# games/space_shooter/bullets.py
import pygame
from core.constants import SCREEN_W, SCREEN_H, YELLOW, RED, CYAN

class Bullet:
    def __init__(self, x, y, is_enemy=False, type_="Normal", vx=0, vy=-10):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy if not is_enemy else abs(vy)
        self.is_enemy = is_enemy
        self.type = type_
        self.alive = True
        self.damage = 1
        
        if self.type == "Laser":
            self.damage = 2
            
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        if self.y < -50 or self.y > SCREEN_H + 50 or self.x < -50 or self.x > SCREEN_W + 50:
            self.alive = False
            
    def get_rect(self):
        w, h = 4, 12
        if self.type == "Laser":
            w, h = 6, 24
        elif self.type == "Energy":
            w, h = 8, 8
        return pygame.Rect(int(self.x - w//2), int(self.y - h//2), w, h)
        
    def draw(self, surface):
        if not self.alive: return
        r = self.get_rect()
        
        color = CYAN if not self.is_enemy else RED
        if self.type == "Laser":
            color = YELLOW
            
        if self.type == "Energy":
            pygame.draw.circle(surface, color, r.center, r.w)
            pygame.draw.circle(surface, (255,255,255), r.center, r.w//2)
        else:
            pygame.draw.rect(surface, color, r, border_radius=2)
            # Inner core
            inner_r = r.inflate(-2, -4)
            if inner_r.w > 0 and inner_r.h > 0:
                pygame.draw.rect(surface, (255,255,255), inner_r, border_radius=1)
