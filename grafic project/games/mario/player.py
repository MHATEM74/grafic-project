# games/mario/player.py
import pygame
from core.assets import snd_jump
from characters.renderer import draw_character_sprite

class Player:
    def __init__(self, char_data):
        self.char = char_data
        self.rect = pygame.Rect(100, 400, 28, 48)
        self.vx = 0; self.vy = 0
        self.on_ground = False
        self.facing = 1
        self.anim = 0
        self.dead = False
        self.invincible = 0
        
        self.has_double_jump = False
        self.can_double_jump = False
        self.has_shield = False
        
        self.powerup_timers = {
            "star": 0,
            "lightning": 0
        }

    def reset(self, x=100, y=400):
        self.rect.x = x; self.rect.y = y
        self.vx = 0; self.vy = 0
        self.on_ground = False; self.dead = False
        self.invincible = 120
        self.has_shield = False
        self.has_double_jump = False
        self.powerup_timers = {"star": 0, "lightning": 0}

    def handle_input(self, keys):
        if self.dead: return
        speed = 6 if self.powerup_timers["star"] > 0 else 4
        self.vx = 0
        
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx = -speed; self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx =  speed; self.facing =  1
        
        # Jump logic handled in game loop events to prevent holding
            
    def jump(self):
        if self.on_ground:
            self.vy = -14
            self.on_ground = False
            self.can_double_jump = True
            snd_jump.play()
        elif self.can_double_jump and self.powerup_timers["lightning"] > 0:
            self.vy = -12
            self.can_double_jump = False
            snd_jump.play()

    def update(self, platforms):
        if self.dead: return
        self.anim += 1
        if self.invincible > 0: self.invincible -= 1
        
        for p in self.powerup_timers:
            if self.powerup_timers[p] > 0:
                self.powerup_timers[p] -= 1
                
        # If moving platforms gave us dx, we add it here (handled in game loop normally)
        
        self.vy = min(self.vy + 0.6, 16)
        self.rect.x += int(self.vx)
        self.on_ground = False
        
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vx > 0: self.rect.right = plat.rect.left
                if self.vx < 0: self.rect.left  = plat.rect.right
                
        self.rect.y += int(self.vy)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vy > 0:
                    self.rect.bottom = plat.rect.top
                    self.vy = 0
                    self.on_ground = True
                    self.can_double_jump = False
                    
                    # If it's a moving platform, inherit its velocity
                    if hasattr(plat, 'vx') and plat.vx != 0:
                        self.rect.x += plat.vx
                        
                elif self.vy < 0:
                    self.rect.top = plat.rect.bottom
                    self.vy = 0

    def draw(self, surface, offset_x):
        if self.invincible > 0 and (self.anim // 4) % 2 == 0: return
        rx = self.rect.x - offset_x; ry = self.rect.y
        
        # Apply star effect (rainbow color)
        char_to_draw = self.char
        if self.powerup_timers["star"] > 0:
            import math
            char_to_draw = dict(self.char)
            r = int(127 * math.sin(self.anim * 0.2) + 128)
            g = int(127 * math.sin(self.anim * 0.2 + 2) + 128)
            b = int(127 * math.sin(self.anim * 0.2 + 4) + 128)
            char_to_draw["color"] = (r, g, b)
            
        draw_character_sprite(surface, char_to_draw, rx+14, ry+20, 0.65, self.anim)
        
        if self.has_shield:
            pygame.draw.circle(surface, (100, 200, 255, 100), (rx+14, ry+20), 30, 2)
