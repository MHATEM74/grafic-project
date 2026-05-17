# games/space_shooter/enemies.py
import pygame
import random
import math
from core.constants import SCREEN_W, RED, ORANGE, PURPLE, GRAY
from games.space_shooter.bullets import Bullet

class SpaceEnemy:
    def __init__(self, x, y, type_="Drone"):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.type = type_
        self.hp = 1
        self.score_val = 10
        self.alive = True
        self.anim = random.randint(0, 100)
        self.shoot_timer = random.randint(60, 180)
        
        # Stats based on type
        if type_ == "Drone":
            self.vx = random.choice([-2, 2])
            self.vy = random.uniform(1.0, 2.5)
        elif type_ == "Fighter":
            self.vx = random.uniform(-4, 4)
            self.vy = 3.5
            self.hp = 2
            self.score_val = 20
        elif type_ == "Carrier":
            self.rect.w, self.rect.h = 60, 60
            self.vx = random.choice([-1, 1])
            self.vy = 0.5
            self.hp = 5
            self.score_val = 50

    def update(self, bullets_list):
        self.anim += 1
        
        # Movement logic
        if self.type == "Drone":
            self.vx = math.sin(self.anim * 0.05) * 3
            self.rect.x += self.vx
            self.rect.y += self.vy
        elif self.type == "Fighter":
            if self.rect.x < 50 or self.rect.x > SCREEN_W - 50: self.vx *= -1
            self.rect.x += self.vx
            self.rect.y += self.vy
        elif self.type == "Carrier":
            if self.rect.x < 50 or self.rect.x > SCREEN_W - 50: self.vx *= -1
            self.rect.x += self.vx
            self.rect.y += self.vy

        # Shooting logic
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            if self.type == "Drone":
                self.shoot_timer = random.randint(120, 240)
                bullets_list.append(Bullet(self.rect.centerx, self.rect.bottom, True, "Energy", 0, 5))
            elif self.type == "Fighter":
                self.shoot_timer = 90
                bullets_list.append(Bullet(self.rect.centerx, self.rect.bottom, True, "Energy", 0, 7))
            elif self.type == "Carrier":
                self.shoot_timer = 120
                bullets_list.append(Bullet(self.rect.left, self.rect.bottom, True, "Energy", -2, 4))
                bullets_list.append(Bullet(self.rect.right, self.rect.bottom, True, "Energy", 2, 4))

        if self.rect.y > 800:
            self.alive = False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        if not self.alive: return
        cx, cy = self.rect.centerx, self.rect.centery
        
        if self.type == "Drone":
            pygame.draw.circle(surface, ORANGE, (cx, cy), 15)
            pygame.draw.circle(surface, RED, (cx, cy), 8)
            pygame.draw.polygon(surface, GRAY, [(cx-20, cy-10), (cx-10, cy+10), (cx, cy)])
            pygame.draw.polygon(surface, GRAY, [(cx+20, cy-10), (cx+10, cy+10), (cx, cy)])
        elif self.type == "Fighter":
            pygame.draw.polygon(surface, RED, [(cx, cy+20), (cx+20, cy-20), (cx, cy-10), (cx-20, cy-20)])
            pygame.draw.circle(surface, YELLOW, (cx, cy), 6)
        elif self.type == "Carrier":
            pygame.draw.rect(surface, PURPLE, (cx-30, cy-20, 60, 40), border_radius=10)
            pygame.draw.rect(surface, (100, 50, 150), (cx-20, cy-10, 40, 20))
            # Engines
            for i in [-20, 0, 20]:
                pygame.draw.circle(surface, RED, (cx+i, cy-25), 8)
                
class SpaceBoss:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_W//2 - 80, -100, 160, 120)
        self.hp = 50
        self.max_hp = 50
        self.alive = True
        self.phase = 1
        self.anim = 0
        self.shoot_timer = 0
        self.vx = 3
        self.vy = 1
        
    def update(self, bullets_list):
        self.anim += 1
        
        # Enter screen
        if self.rect.y < 50:
            self.rect.y += self.vy
        else:
            # Boss pattern
            self.rect.x += self.vx
            if self.rect.x < 50 or self.rect.right > SCREEN_W - 50:
                self.vx *= -1
                
            self.rect.y = 50 + int(math.sin(self.anim * 0.05) * 30)

            # Shooting
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                if self.phase == 1:
                    self.shoot_timer = 60
                    bullets_list.append(Bullet(self.rect.centerx, self.rect.bottom, True, "Energy", 0, 6))
                    bullets_list.append(Bullet(self.rect.left + 20, self.rect.bottom, True, "Energy", -3, 6))
                    bullets_list.append(Bullet(self.rect.right - 20, self.rect.bottom, True, "Energy", 3, 6))
                else: # Phase 2 (Angry)
                    self.shoot_timer = 40
                    bullets_list.append(Bullet(self.rect.centerx, self.rect.bottom, True, "Laser", 0, 8))
                    
                    if self.anim % 120 < 60:
                        bullets_list.append(Bullet(self.rect.left + 10, self.rect.bottom, True, "Energy", -4, 5))
                        bullets_list.append(Bullet(self.rect.right - 10, self.rect.bottom, True, "Energy", 4, 5))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= self.max_hp // 2:
            self.phase = 2
            self.vx = 5 if self.vx > 0 else -5
            
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        if not self.alive: return
        cx, cy = self.rect.centerx, self.rect.centery
        
        color = (180, 30, 30) if self.phase == 1 else (255, 50, 50)
        
        # Main Body
        pygame.draw.ellipse(surface, color, self.rect)
        pygame.draw.ellipse(surface, (50, 10, 10), self.rect, 4)
        
        # Eye
        eye_y = cy + 20
        pygame.draw.circle(surface, BLACK, (cx, eye_y), 25)
        pygame.draw.circle(surface, YELLOW if self.phase == 1 else RED, (cx, eye_y), 15)
        pygame.draw.circle(surface, WHITE, (cx+5, eye_y-5), 5)
        
        # Cannons
        pygame.draw.rect(surface, GRAY, (self.rect.left+10, cy, 20, 60))
        pygame.draw.rect(surface, GRAY, (self.rect.right-30, cy, 20, 60))
        
        # HP Bar
        bw = 140
        pygame.draw.rect(surface, RED, (cx-70, self.rect.y-20, bw, 8))
        pygame.draw.rect(surface, GREEN, (cx-70, self.rect.y-20, int(bw*(self.hp/self.max_hp)), 8))
        pygame.draw.rect(surface, WHITE, (cx-70, self.rect.y-20, bw, 8), 1)
