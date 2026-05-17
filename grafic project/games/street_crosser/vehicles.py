# games/street_crosser/vehicles.py
import pygame
from core.constants import SCREEN_W, RED, YELLOW, BLUE, WHITE, BLACK, ORANGE, GRAY

class Vehicle:
    def __init__(self, x, y, type_, direction, speed):
        self.type = type_
        self.direction = direction # 1 for right, -1 for left
        self.speed = speed * direction
        
        # Configurations
        configs = {
            "Car": {"w": 60, "h": 30, "color": random_color()},
            "Taxi": {"w": 60, "h": 30, "color": YELLOW},
            "Bus": {"w": 120, "h": 40, "color": ORANGE},
            "Truck": {"w": 140, "h": 40, "color": GRAY},
            "Racecar": {"w": 50, "h": 25, "color": RED},
            "Bike": {"w": 30, "h": 15, "color": BLUE},
            "Ambulance": {"w": 80, "h": 35, "color": WHITE}
        }
        cfg = configs.get(type_, configs["Car"])
        
        self.rect = pygame.Rect(x, y, cfg["w"], cfg["h"])
        self.color = cfg["color"]
        self.alive = True
        self.anim = 0

    def update(self):
        self.anim += 1
        self.rect.x += self.speed
        
        if self.direction == 1 and self.rect.left > SCREEN_W + 100:
            self.alive = False
        elif self.direction == -1 and self.rect.right < -100:
            self.alive = False

    def draw(self, surface):
        if not self.alive: return
        
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        
        # Windows
        win_color = (150, 200, 255)
        if self.direction == 1: # Moving right
            pygame.draw.rect(surface, win_color, (self.rect.right - 15, self.rect.y + 5, 10, self.rect.h - 10))
            # Headlights
            pygame.draw.circle(surface, (255, 255, 200), (self.rect.right, self.rect.y + 5), 3)
            pygame.draw.circle(surface, (255, 255, 200), (self.rect.right, self.rect.bottom - 5), 3)
            # Taillights
            pygame.draw.circle(surface, RED, (self.rect.left, self.rect.y + 5), 3)
            pygame.draw.circle(surface, RED, (self.rect.left, self.rect.bottom - 5), 3)
        else: # Moving left
            pygame.draw.rect(surface, win_color, (self.rect.left + 5, self.rect.y + 5, 10, self.rect.h - 10))
            # Headlights
            pygame.draw.circle(surface, (255, 255, 200), (self.rect.left, self.rect.y + 5), 3)
            pygame.draw.circle(surface, (255, 255, 200), (self.rect.left, self.rect.bottom - 5), 3)
            # Taillights
            pygame.draw.circle(surface, RED, (self.rect.right, self.rect.y + 5), 3)
            pygame.draw.circle(surface, RED, (self.rect.right, self.rect.bottom - 5), 3)
            
        if self.type == "Ambulance" and (self.anim // 10) % 2 == 0:
            pygame.draw.rect(surface, RED, (self.rect.centerx - 5, self.rect.y - 4, 10, 4))
            pygame.draw.rect(surface, BLUE, (self.rect.centerx - 5, self.rect.y - 4, 10, 4)) # Overlap for flashing

def random_color():
    import random
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
