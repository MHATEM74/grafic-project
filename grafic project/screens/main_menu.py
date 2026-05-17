# screens/main_menu.py
import pygame
import sys
import random
import math
from core.constants import SCREEN_W, SCREEN_H, GOLD, CYAN, PINK, GRAY, WHITE
from core.assets import font_lg, font_sm, font_xs
from ui.button import Button
from ui.particles import Particle
from ui.hud import draw_stars_bg
from characters.renderer import draw_character_sprite
from characters.character_data import CHARACTERS

class MainMenu:
    def __init__(self, game_ref):
        self.game = game_ref
        self.t = 0
        self.stars = [(random.randint(0,SCREEN_W), random.randint(0,SCREEN_H), random.randint(1,3)) for _ in range(120)]
        bx = SCREEN_W//2 - 150
        
        self.btn_duck   = Button(bx, 280, 300, 56, "🦆 DUCK HUNT",   (60,140,60))
        self.btn_mario  = Button(bx, 350, 300, 56, "🎮 MARIO RUN",   (180,60,30))
        self.btn_space  = Button(bx, 420, 300, 56, "🚀 SPACE SHOOT", (50,100,220))
        self.btn_street = Button(bx, 490, 300, 56, "🐸 STREET HOP",  (100,150,100))
        self.btn_shop   = Button(bx, 560, 300, 56, "★ SHOP",         (150,50,220))
        self.btn_quit   = Button(bx, 630, 300, 56, "✕ QUIT",         (100,30,30))
        
        self.particles = []
        self.sparkle_timer = 0

    def handle_event(self, event):
        if self.btn_duck.is_clicked(event):
            self.game.state = "duck"
            from games.duck_hunt.duck_hunt import DuckHuntGame
            self.game.duck_game = DuckHuntGame(self.game)
        if self.btn_mario.is_clicked(event):
            self.game.state = "mario"
            from games.mario.mario_game import MarioPlatformerGame
            self.game.mario_game = MarioPlatformerGame(self.game)
        if self.btn_space.is_clicked(event):
            self.game.state = "space"
            from games.space_shooter.space_game import SpaceShooterGame
            self.game.space_game = SpaceShooterGame(self.game)
        if self.btn_street.is_clicked(event):
            self.game.state = "street"
            from games.street_crosser.street_game import StreetCrosserGame
            self.game.street_game = StreetCrosserGame(self.game)
        if self.btn_shop.is_clicked(event):
            self.game.state = "shop"
        if self.btn_quit.is_clicked(event):
            from core.save_system import SaveSystem
            SaveSystem.save(self.game)
            pygame.quit()
            sys.exit()

    def update(self):
        self.t += 1
        mx, my = pygame.mouse.get_pos()
        for b in [self.btn_duck, self.btn_mario, self.btn_space, self.btn_street, self.btn_shop, self.btn_quit]:
            b.update(mx, my)
            
        self.sparkle_timer += 1
        if self.sparkle_timer > 12:
            self.sparkle_timer = 0
            px = random.randint(50, SCREEN_W-50)
            py = random.randint(50, SCREEN_H-50)
            self.particles.append(Particle(px, py, random.choice([GOLD, CYAN, PINK, WHITE]), 0, random.uniform(-2,0)))
        
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        # Starfield
        draw_stars_bg(surface, self.stars, self.t)
        # Particles
        for p in self.particles: p.draw(surface)
        
        # Title wobble & Color Shift
        title_y = 80 + int(math.sin(self.t * 0.04) * 8)
        
        # Dynamic color for logo
        color_phase = (self.t * 2) % 360
        r = int(127 * math.sin(math.radians(color_phase)) + 128)
        g = int(127 * math.sin(math.radians(color_phase + 120)) + 128)
        b = int(127 * math.sin(math.radians(color_phase + 240)) + 128)
        dynamic_color = (r, g, b)
        
        title1 = font_lg.render("PIXEL", True, GOLD)
        title2 = font_lg.render("GAME HUB", True, dynamic_color)
        shadow1 = font_lg.render("PIXEL", True, (80,60,0))
        shadow2 = font_lg.render("GAME HUB", True, (r//3, g//3, b//3))
        
        surface.blit(shadow1, shadow1.get_rect(center=(SCREEN_W//2+3, title_y+3)))
        surface.blit(shadow2, shadow2.get_rect(center=(SCREEN_W//2+3, title_y+60+3)))
        surface.blit(title1, title1.get_rect(center=(SCREEN_W//2, title_y)))
        surface.blit(title2, title2.get_rect(center=(SCREEN_W//2, title_y+60)))
        
        # Decorative line
        pygame.draw.line(surface, GOLD, (SCREEN_W//2-200, title_y+110), (SCREEN_W//2+200, title_y+110), 2)
        
        # Selected character preview
        ch = CHARACTERS[self.game.selected_char]
        draw_character_sprite(surface, ch, SCREEN_W//2, 270, 1.6, self.t)
        name_t = font_sm.render(f"Playing as: {ch['name']}", True, ch["accent"])
        surface.blit(name_t, name_t.get_rect(center=(SCREEN_W//2, 310)))
        
        # Buttons
        for b in [self.btn_duck, self.btn_mario, self.btn_space, self.btn_street, self.btn_shop, self.btn_quit]:
            b.draw(surface)
            
        # Coin display
        coin_surf = pygame.Surface((220, 44), pygame.SRCALPHA)
        coin_surf.fill((0,0,0,140))
        surface.blit(coin_surf, (SCREEN_W//2-110, 8))
        ct = font_sm.render(f"★ {self.game.coins} COINS", True, GOLD)
        surface.blit(ct, ct.get_rect(center=(SCREEN_W//2, 30)))
        
        # Version
        vt = font_xs.render("v2.0  |  ESC = Pause in game", True, GRAY)
        surface.blit(vt, vt.get_rect(center=(SCREEN_W//2, SCREEN_H-16)))
