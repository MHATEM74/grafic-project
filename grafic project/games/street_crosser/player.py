# games/street_crosser/player.py
import pygame
from core.constants import SCREEN_W, SCREEN_H
from characters.renderer import draw_character_sprite
from core.assets import snd_jump

class StreetPlayer:
    def __init__(self, char_data):
        self.char = char_data
        self.rect = pygame.Rect(SCREEN_W//2 - 16, SCREEN_H - 60, 32, 32)
        self.vx = 0
        self.vy = 0
        self.anim = 0
        self.target_y = self.rect.y
        self.target_x = self.rect.x
        self.moving = False
        self.speed = 8
        self.alive = True

    def reset(self):
        self.rect.x = SCREEN_W//2 - 16
        self.rect.y = SCREEN_H - 60
        self.target_x = self.rect.x
        self.target_y = self.rect.y
        self.moving = False
        self.alive = True

    def handle_input(self, event):
        if not self.alive or self.moving: return
        
        step_x = 40
        step_y = 40
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                if self.rect.x - step_x >= 0:
                    self.target_x -= step_x
                    self.moving = True
                    snd_jump.play()
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                if self.rect.x + step_x <= SCREEN_W - 32:
                    self.target_x += step_x
                    self.moving = True
                    snd_jump.play()
            elif event.key in [pygame.K_UP, pygame.K_w]:
                if self.rect.y - step_y >= 0:
                    self.target_y -= step_y
                    self.moving = True
                    snd_jump.play()
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                if self.rect.y + step_y <= SCREEN_H - 32:
                    self.target_y += step_y
                    self.moving = True
                    snd_jump.play()

    def update(self):
        if not self.alive: return
        self.anim += 1
        
        if self.moving:
            dx = self.target_x - self.rect.x
            dy = self.target_y - self.rect.y
            
            if dx != 0:
                self.rect.x += self.speed if dx > 0 else -self.speed
                if abs(self.target_x - self.rect.x) < self.speed:
                    self.rect.x = self.target_x
            if dy != 0:
                self.rect.y += self.speed if dy > 0 else -self.speed
                if abs(self.target_y - self.rect.y) < self.speed:
                    self.rect.y = self.target_y
                    
            if self.rect.x == self.target_x and self.rect.y == self.target_y:
                self.moving = False

    def draw(self, surface):
        if not self.alive: return
        
        jump_offset = -10 if self.moving else 0
        draw_character_sprite(surface, self.char, self.rect.centerx, self.rect.centery + 10 + jump_offset, 0.8, self.anim)
