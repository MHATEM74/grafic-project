# games/mario/enemies.py
import pygame
import math
from core.constants import BLACK, WHITE, RED, GREEN, ORANGE, YELLOW
from core.assets import snd_hit

class Enemy:
    def __init__(self, x, y, type_="Goomba"):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.type = type_
        self.vx = -2 if type_ != "Jumper" else -1.5
        self.vy = 0
        self.alive = True
        self.stomped = False
        self.stomp_timer = 0
        self.anim = 0

    def update(self, platforms, offset_x):
        if self.stomped:
            self.stomp_timer += 1
            if self.stomp_timer > 40: self.alive = False
            return
            
        self.anim += 1
        self.vy = min(self.vy + 0.5, 12)
        
        if self.type == "Jumper" and self.vy == 0.5 and self.anim % 60 == 0:
            self.vy = -10
            
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        
        on_ground = False
        for plat in platforms:
            pr = plat.rect
            er = self.rect
            if er.colliderect(pr):
                if self.vy > 0 and er.bottom <= pr.bottom + 10:
                    er.bottom = pr.top
                    self.vy = 0
                    on_ground = True
                elif er.right >= pr.left and er.left < pr.left:
                    self.vx = abs(self.vx); er.right = pr.left
                elif er.left <= pr.right and er.right > pr.right:
                    self.vx = -abs(self.vx); er.left = pr.right

    def draw(self, surface, offset_x):
        if not self.alive: return
        r = self.rect.move(-offset_x, 0)
        
        if self.stomped:
            if self.type == "Goomba":
                pygame.draw.rect(surface, (140,80,20), (r.x, r.y+20, 32, 12))
            return
            
        body_y = r.y + int(math.sin(self.anim*0.2)*2)
        
        if self.type == "Goomba":
            pygame.draw.rect(surface, (140,80,20), (r.x+4, r.y+10, 24, 22))
            pygame.draw.circle(surface, (140,80,20), (r.x+16, r.y+16), 16)
            pygame.draw.circle(surface, BLACK, (r.x+10, r.y+12), 4)
            pygame.draw.circle(surface, BLACK, (r.x+22, r.y+12), 4)
            leg_off = int(math.sin(self.anim*0.2)*4)
            pygame.draw.rect(surface, (100,60,10), (r.x+4, r.y+30, 10, 8+leg_off))
            pygame.draw.rect(surface, (100,60,10), (r.x+18, r.y+30, 10, 8-leg_off))
            
        elif self.type == "Spiky":
            pygame.draw.circle(surface, RED, (r.centerx, r.centery), 12)
            pygame.draw.circle(surface, BLACK, (r.centerx-4, r.centery-4), 3)
            pygame.draw.circle(surface, BLACK, (r.centerx+4, r.centery-4), 3)
            # Spikes
            for i in range(5):
                ang = math.radians(180 + i * 45)
                sx = r.centerx + math.cos(ang) * 12
                sy = r.centery + math.sin(ang) * 12
                pygame.draw.polygon(surface, WHITE, [(sx, sy), (sx-4, sy+4), (sx+math.cos(ang)*8, sy+math.sin(ang)*8)])
                
        elif self.type == "Jumper":
            pygame.draw.rect(surface, GREEN, (r.x+4, r.y+8, 24, 24), border_radius=8)
            pygame.draw.rect(surface, WHITE, (r.x+8, r.y+12, 6, 8))
            pygame.draw.rect(surface, WHITE, (r.x+18, r.y+12, 6, 8))


class BossMonster:
    def __init__(self, x=700, y=400):
        self.rect = pygame.Rect(x, y, 72, 72)
        self.vx = -3; self.vy = 0
        self.hp = 3; self.max_hp = 3
        self.alive = True
        self.projectiles = []
        self.shoot_timer = 0
        self.hit_flash = 0
        self.anim = 0

    def update(self, platforms):
        self.anim += 1
        self.hit_flash = max(0, self.hit_flash - 1)
        self.vy = min(self.vy + 0.5, 12)
        self.rect.x += self.vx
        self.rect.y += int(self.vy)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vy > 0:
                    self.rect.bottom = plat.rect.top
                    self.vy = 0
                if self.rect.right >= plat.rect.left and self.rect.centerx < plat.rect.centerx:
                    self.rect.right = plat.rect.left; self.vx *= -1
                if self.rect.left <= plat.rect.right and self.rect.centerx > plat.rect.centerx:
                    self.rect.left = plat.rect.right; self.vx *= -1
                    
        # Hardcoded bounds for boss arena roughly
        if self.rect.left < 200: self.vx = abs(self.vx)
        if self.rect.right > 2000: self.vx = -abs(self.vx)
        
        self.shoot_timer += 1
        if self.shoot_timer > 90:
            self.shoot_timer = 0
            self.projectiles.append({"x": float(self.rect.centerx), "y": float(self.rect.centery),
                                     "vx": self.vx*2, "vy": -4})
                                     
        for proj in self.projectiles:
            proj["x"] += proj["vx"]; proj["y"] += proj["vy"]; proj["vy"] += 0.3
        self.projectiles = [p for p in self.projectiles if 0 < p["x"] < 3000 and p["y"] < 1000]

    def stomp(self):
        self.hp -= 1
        self.hit_flash = 10
        snd_hit.play()
        if self.hp <= 0: self.alive = False

    def draw(self, surface, offset_x):
        if not self.alive: return
        r = self.rect.move(-offset_x, 0)
        c = (200,50,50) if self.hit_flash > 0 else (160,30,30)
        
        pygame.draw.rect(surface, c, r, border_radius=8)
        pygame.draw.circle(surface, (200,160,100), (r.x+36, r.y+24), 24)
        pygame.draw.circle(surface, (255,50,50), (r.x+26, r.y+18), 8)
        pygame.draw.circle(surface, (255,50,50), (r.x+46, r.y+18), 8)
        pygame.draw.circle(surface, BLACK, (r.x+26, r.y+18), 5)
        pygame.draw.circle(surface, BLACK, (r.x+46, r.y+18), 5)
        pygame.draw.polygon(surface, (150,20,20),
            [(r.x+16,r.y+32),(r.x+28,r.y+24),(r.x+44,r.y+24),(r.x+56,r.y+32)])
            
        bw = 80
        pygame.draw.rect(surface, RED, (r.x-4, r.y-18, bw, 8))
        pygame.draw.rect(surface, GREEN, (r.x-4, r.y-18, int(bw*(self.hp/self.max_hp)), 8))
        pygame.draw.rect(surface, WHITE, (r.x-4, r.y-18, bw, 8), 1)
        
        for proj in self.projectiles:
            px = int(proj["x"]) - offset_x
            py = int(proj["y"])
            pygame.draw.circle(surface, ORANGE, (px, py), 8)
            pygame.draw.circle(surface, YELLOW, (px, py), 4)
