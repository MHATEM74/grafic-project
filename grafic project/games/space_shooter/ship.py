# games/space_shooter/ship.py
import pygame
from core.constants import SCREEN_W, SCREEN_H, WHITE, CYAN, BLUE
from core.assets import snd_shoot
from characters.renderer import draw_character_sprite
from games.space_shooter.bullets import Bullet

class Ship:
    def __init__(self, char_data):
        self.char = char_data
        self.rect = pygame.Rect(SCREEN_W//2 - 24, SCREEN_H - 100, 48, 48)
        self.speed = 6
        self.vx = 0
        self.vy = 0
        self.anim = 0
        self.shoot_timer = 0
        self.shoot_delay = 15
        
        # Powerups
        self.shield_hp = 0
        self.weapon_level = 1
        self.laser_timer = 0
        self.invincible = 120
        self.alive = True

    def handle_input(self, keys, bullets_list):
        if not self.alive: return
        self.vx = 0
        self.vy = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.vy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.vy = self.speed
        
        # Auto-shoot when holding space
        if keys[pygame.K_SPACE] and self.shoot_timer <= 0:
            self._shoot(bullets_list)

    def _shoot(self, bullets_list):
        self.shoot_timer = self.shoot_delay
        snd_shoot.play()
        
        w_type = "Laser" if self.laser_timer > 0 else "Normal"
        
        if self.weapon_level == 1:
            bullets_list.append(Bullet(self.rect.centerx, self.rect.top, False, w_type))
        elif self.weapon_level == 2:
            bullets_list.append(Bullet(self.rect.left + 10, self.rect.top, False, w_type))
            bullets_list.append(Bullet(self.rect.right - 10, self.rect.top, False, w_type))
        else: # Level 3+ (Triple)
            bullets_list.append(Bullet(self.rect.centerx, self.rect.top, False, w_type))
            bullets_list.append(Bullet(self.rect.left, self.rect.top + 10, False, w_type, vx=-3))
            bullets_list.append(Bullet(self.rect.right, self.rect.top + 10, False, w_type, vx=3))

    def update(self):
        if not self.alive: return
        self.anim += 1
        
        if self.shoot_timer > 0: self.shoot_timer -= 1
        if self.invincible > 0: self.invincible -= 1
        if self.laser_timer > 0: self.laser_timer -= 1
        
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Bounds
        self.rect.x = max(0, min(SCREEN_W - self.rect.w, self.rect.x))
        self.rect.y = max(0, min(SCREEN_H - self.rect.h, self.rect.y))

    def take_damage(self):
        if self.invincible > 0: return False
        
        if self.shield_hp > 0:
            self.shield_hp -= 1
            self.invincible = 30
            return False
            
        self.alive = False
        return True

    def draw(self, surface):
        if not self.alive: return
        if self.invincible > 0 and (self.anim // 4) % 2 == 0: return
        
        # Ship body
        cx, cy = self.rect.centerx, self.rect.centery
        
        # Engine flame
        flame_len = 20 + (self.anim % 5) * 2
        pygame.draw.polygon(surface, (255, 100, 0), [(cx-10, cy+15), (cx+10, cy+15), (cx, cy+15+flame_len)])
        pygame.draw.polygon(surface, (255, 255, 0), [(cx-5, cy+15), (cx+5, cy+15), (cx, cy+10+flame_len)])
        
        # Wings
        c = self.char["color"]
        ac = self.char["accent"]
        pygame.draw.polygon(surface, c, [(cx, cy-24), (cx+24, cy+16), (cx-24, cy+16)])
        pygame.draw.polygon(surface, ac, [(cx, cy-15), (cx+15, cy+10), (cx-15, cy+10)])
        
        # Character sitting inside cockpit
        draw_character_sprite(surface, self.char, cx, cy+5, 0.4, 0)
        
        # Cockpit glass
        pygame.draw.ellipse(surface, (150, 200, 255, 150), (cx-10, cy-10, 20, 25))
        
        # Shield
        if self.shield_hp > 0:
            import math
            pulse = math.sin(self.anim * 0.1) * 2
            pygame.draw.circle(surface, (100, 200, 255, 100), (cx, cy), int(35 + pulse), 3)
