# ui/particles.py
import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, vx=None, vy=None):
        self.x = x; self.y = y; self.color = color
        self.vx = vx if vx is not None else random.uniform(-3,3)
        self.vy = vy if vy is not None else random.uniform(-5,-1)
        self.life = random.randint(30,60)
        self.max_life = self.life
        self.size = random.randint(3,7)

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.15; self.life -= 1

    def draw(self, surface):
        alpha = self.life / self.max_life
        size = int(self.size * alpha)
        if size > 0:
            pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), size, size))
