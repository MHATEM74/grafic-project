# games/street_crosser/background.py
import pygame
from core.constants import SCREEN_W, SCREEN_H, GRAY, WHITE, YELLOW, GREEN

class StreetBackground:
    def __init__(self):
        self.anim = 0

    def draw(self, surface, safe_zones, lanes):
        self.anim += 1
        
        # Base road
        surface.fill((40, 40, 45))
        
        # Safe Zones (Sidewalks/Islands)
        for zone in safe_zones:
            pygame.draw.rect(surface, (100, 150, 100), (0, zone['y'], SCREEN_W, zone['h']))
            # Curb
            pygame.draw.rect(surface, (150, 200, 150), (0, zone['y'], SCREEN_W, 5))
            pygame.draw.rect(surface, (150, 200, 150), (0, zone['y']+zone['h']-5, SCREEN_W, 5))
            
            # Simple trees/bushes
            for tx in range(50, SCREEN_W, 100):
                pygame.draw.circle(surface, (50, 100, 50), (tx, zone['y'] + zone['h']//2), 15)

        # Lane markings
        for i in range(len(lanes) - 1):
            y = lanes[i]['y'] + lanes[i]['h']
            # Don't draw if next is a safe zone
            if not any(z['y'] <= y <= z['y']+z['h'] for z in safe_zones):
                dash_offset = (self.anim * 2) % 40
                for lx in range(-40, SCREEN_W, 40):
                    pygame.draw.rect(surface, (200, 200, 50), (lx + dash_offset, y - 2, 20, 4))
