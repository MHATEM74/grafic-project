# games/duck_hunt/duck.py
import pygame
import random
import math
from core.constants import SCREEN_W, SCREEN_H, BLACK, WHITE, RED, GOLD

class Duck:
    PATTERNS = ["linear", "zigzag", "diagonal", "sine"]
    
    def __init__(self, level):
        self.level = level
        speed_base = 2 + level * 0.8
        self.speed = random.uniform(speed_base, speed_base+2)
        side = random.choice(["left", "right"])
        if side == "left":
            self.x = -60; self.vx = self.speed
        else:
            self.x = SCREEN_W+60; self.vx = -self.speed
            
        self.y = random.randint(80, SCREEN_H-200)
        self.vy = 0
        self.pattern = random.choice(Duck.PATTERNS)
        self.t = 0
        self.alive = True
        self.hit = False
        self.hit_timer = 0
        self.size = 40
        self.anim = 0
        self.color = random.choice([(60,160,60),(80,180,100),(40,140,80)])
        self.wing_up = True
        
        self.type = "Normal"
        self.hp = 1
        self.coin_value = 1
        
        # Randomly upgrade duck type based on level
        r = random.random()
        if r < 0.05 and level > 1:
            self.type = "Golden"
            self.color = GOLD
            self.size = 25
            self.vx *= 1.5
            self.coin_value = 3
        elif r < 0.15 and level > 2:
            self.type = "Fat"
            self.color = (100, 50, 200)
            self.size = 60
            self.vx *= 0.6
            self.hp = 2
            self.coin_value = 2
        elif r < 0.25 and level > 3:
            self.type = "Ghost"
            self.color = (200, 200, 255)
            self.coin_value = 2
        elif r < 0.35 and level > 4:
            self.type = "Bomb"
            self.color = (200, 50, 50)
            self.coin_value = 5

        self.visible = True

    def update(self):
        self.t += 1
        self.anim += 1
        if self.anim % 8 == 0:
            self.wing_up = not self.wing_up
            
        if self.type == "Ghost":
            self.visible = (self.t % 120) < 80 # Visible 80 frames, hidden 40 frames
            
        if self.pattern == "zigzag":
            self.vy = math.sin(self.t * 0.1) * 4
        elif self.pattern == "sine":
            self.vy = math.sin(self.t * 0.07) * 3
        elif self.pattern == "diagonal":
            self.vy = self.vx * 0.3
            
        self.x += self.vx
        self.y += self.vy
        self.y = max(60, min(SCREEN_H-120, self.y))
        
        if self.hit:
            self.hit_timer += 1
            self.y += 5
            if self.hit_timer > 30:
                self.alive = False

    def get_rect(self):
        return pygame.Rect(int(self.x - self.size//2), int(self.y - self.size//2), self.size, self.size)

    def is_offscreen(self):
        return self.x < -100 or self.x > SCREEN_W+100
        
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hit = True
            return True # Killed
        return False # Still alive

    def draw(self, surface):
        if not self.alive or not self.visible: return
        c = self.color
        
        if self.type == "Ghost":
            # Make color slightly transparent
            c = (*c, 150)
            
        x, y = int(self.x), int(self.y)
        flip = self.vx < 0
        
        # Bomb ticking
        if self.type == "Bomb" and self.t % 20 < 10:
            c = (255, 100, 100)
            
        # Body
        pygame.draw.ellipse(surface, c, (x-int(18*self.size/40), y-int(12*self.size/40), int(36*self.size/40), int(24*self.size/40)))
        # Head
        pygame.draw.circle(surface, c, (x+int(20*self.size/40) if not flip else x-int(20*self.size/40), y-int(8*self.size/40)), int(12*self.size/40))
        # Bill
        bc = (255, 180, 0)
        bx = x+int(30*self.size/40) if not flip else x-int(30*self.size/40)
        pygame.draw.ellipse(surface, bc, (bx-int(8*self.size/40), y-int(10*self.size/40), int(16*self.size/40), int(7*self.size/40)))
        # Eye
        ex = x+int(22*self.size/40) if not flip else x-int(22*self.size/40)
        pygame.draw.circle(surface, BLACK, (ex, y-int(11*self.size/40)), int(3*self.size/40))
        pygame.draw.circle(surface, WHITE, (ex+1, y-int(12*self.size/40)), max(1, int(1*self.size/40)))
        # Wing
        wing_y = y-int(18*self.size/40) if self.wing_up else y-int(6*self.size/40)
        pygame.draw.ellipse(surface, tuple(min(255,cc+40) for cc in c[:3]), (x-int(14*self.size/40), wing_y, int(28*self.size/40), int(14*self.size/40)))
        # Tail
        tx = x-int(22*self.size/40) if not flip else x+int(22*self.size/40)
        pygame.draw.ellipse(surface, (30,100,30), (tx-int(8*self.size/40), y-int(6*self.size/40), int(16*self.size/40), int(12*self.size/40)))
        
        if self.hit:
            pygame.draw.line(surface, RED, (x-15, y-15), (x+15, y+15), 3)
            pygame.draw.line(surface, RED, (x+15, y-15), (x-15, y+15), 3)

class BossDuck:
    def __init__(self):
        self.x = SCREEN_W//2; self.y = 200
        self.vx = 4; self.vy = 2
        self.hp = 10; self.max_hp = 10
        self.alive = True
        self.t = 0; self.anim = 0
        self.size = 80
        self.hit_flash = 0
        self.dir_timer = 0
        self.type = "Boss"

    def update(self):
        self.t += 1; self.anim += 1
        self.dir_timer += 1
        if self.dir_timer > random.randint(40,80):
            self.vx = random.uniform(-6,6)
            self.vy = random.uniform(-4,4)
            self.dir_timer = 0
        self.x += self.vx; self.y += self.vy
        if self.x < 80 or self.x > SCREEN_W-80: self.vx *= -1
        if self.y < 60 or self.y > SCREEN_H-180: self.vy *= -1
        if self.hit_flash > 0: self.hit_flash -= 1

    def get_rect(self):
        return pygame.Rect(int(self.x-self.size//2), int(self.y-self.size//2), self.size, self.size)

    def draw(self, surface):
        if not self.alive: return
        c = (200, 50, 50) if self.hit_flash > 0 else (180, 30, 30)
        x, y = int(self.x), int(self.y)
        pygame.draw.ellipse(surface, c, (x-36, y-24, 72, 48))
        pygame.draw.circle(surface, c, (x+40, y-16), 24)
        pygame.draw.ellipse(surface, GOLD, (x+55, y-20, 24, 10))
        pygame.draw.circle(surface, WHITE, (x+44, y-20), 6)
        pygame.draw.circle(surface, BLACK, (x+45, y-20), 4)
        pygame.draw.ellipse(surface, (80,30,200), (x-28, y-44, 56, 24))
        pygame.draw.ellipse(surface, (100,50,220), (x-28, y+8, 56, 24))
        
        # HP bar
        bw = 100
        pygame.draw.rect(surface, RED, (x-50, y-60, bw, 10))
        pygame.draw.rect(surface, (50, 200, 80), (x-50, y-60, int(bw*(self.hp/self.max_hp)), 10))
        pygame.draw.rect(surface, WHITE, (x-50, y-60, bw, 10), 2)
        font = pygame.font.Font(None, 16)
        txt = font.render(f"BOSS HP: {self.hp}", True, WHITE)
        surface.blit(txt, (x-50, y-78))

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 8
        if self.hp <= 0:
            self.alive = False
            return True
        return False
