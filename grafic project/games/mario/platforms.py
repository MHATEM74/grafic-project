# games/mario/platforms.py
import pygame

class Platform:
    def __init__(self, x, y, w, h=16, color=(120,80,40)):
        self.rect  = pygame.Rect(x, y, w, h)
        self.color = color
        self.top_color = tuple(min(255,c+40) for c in color)

    def update(self):
        pass # Static platform

    def draw(self, surface, offset_x=0):
        r = self.rect.move(-offset_x, 0)
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, self.top_color, (r.x, r.y, r.w, 6))
        pygame.draw.rect(surface, (60,40,20), r, 2)

class MovingPlatform(Platform):
    def __init__(self, x, y, w, h=16, color=(80, 100, 120), range_x=0, range_y=0, speed=2):
        super().__init__(x, y, w, h, color)
        self.start_x = x
        self.start_y = y
        self.range_x = range_x
        self.range_y = range_y
        self.speed = speed
        self.dir = 1
        
        self.vx = 0
        self.vy = 0

    def update(self):
        if self.range_x > 0:
            self.vx = self.speed * self.dir
            self.rect.x += self.vx
            if self.rect.x > self.start_x + self.range_x or self.rect.x < self.start_x:
                self.dir *= -1
                self.vx = self.speed * self.dir
                self.rect.x += self.vx
                
        if self.range_y > 0:
            self.vy = self.speed * self.dir
            self.rect.y += self.vy
            if self.rect.y > self.start_y + self.range_y or self.rect.y < self.start_y:
                self.dir *= -1
                self.vy = self.speed * self.dir
                self.rect.y += self.vy
