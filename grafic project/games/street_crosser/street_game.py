# games/street_crosser/street_game.py
import pygame
import random
from core.constants import SCREEN_W, SCREEN_H, RED, GREEN, GOLD, WHITE, GRAY
from core.assets import font_lg, font_md, font_sm, font_xs, snd_coin, snd_die, snd_hit
from ui.button import Button
from ui.particles import Particle
from ui.hud import draw_hud
from characters.character_data import CHARACTERS
from games.street_crosser.background import StreetBackground
from games.street_crosser.player import StreetPlayer
from games.street_crosser.vehicles import Vehicle
from games.street_crosser.lanes import generate_level

class StreetCrosserGame:
    def __init__(self, game_ref):
        self.game = game_ref
        self.paused = False
        self.pause_btn = Button(SCREEN_W//2-80, SCREEN_H//2-30, 160, 50, "RESUME", GREEN)
        self.quit_btn  = Button(SCREEN_W//2-80, SCREEN_H//2+40, 160, 50, "QUIT", RED)
        
        self.bg = StreetBackground()
        self.player = StreetPlayer(CHARACTERS[self.game.selected_char])
        self.level_idx = 0
        self.lives = 3
        
        self.vehicles = []
        self.particles = []
        self.shake = 0
        self.result = None
        self.result_timer = 0
        self.score = 0
        
        self.load_level()

    def load_level(self):
        self.lanes, self.safe_zones, self.goal_y = generate_level(self.level_idx)
        self.vehicles = []
        self.player.reset()
        self.spawn_timers = [0] * len(self.lanes)
        
        # Pre-spawn some vehicles so the roads aren't empty initially
        for i, lane in enumerate(self.lanes):
            for _ in range(3):
                x = random.randint(0, SCREEN_W)
                type_ = random.choice(lane["types"])
                self.vehicles.append(Vehicle(x, lane["y"] + 5, type_, lane["dir"], lane["speed"]))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
        if self.paused:
            if self.pause_btn.is_clicked(event): self.paused = False
            if self.quit_btn.is_clicked(event):  self.game.state = "menu"
            return
            
        self.player.handle_input(event)

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.pause_btn.update(mx, my)
        self.quit_btn.update(mx, my)
        
        if self.paused or self.result is not None: return
        
        if self.shake > 0: self.shake -= 1
        
        self.player.update()
        
        # Spawn vehicles
        for i, lane in enumerate(self.lanes):
            self.spawn_timers[i] += 1
            if self.spawn_timers[i] >= lane["spawn_rate"]:
                self.spawn_timers[i] = 0
                x = -100 if lane["dir"] == 1 else SCREEN_W + 100
                type_ = random.choice(lane["types"])
                self.vehicles.append(Vehicle(x, lane["y"] + 5, type_, lane["dir"], lane["speed"]))
                
        # Update vehicles
        for v in self.vehicles:
            v.update()
        self.vehicles = [v for v in self.vehicles if v.alive]
        
        # Collision
        if self.player.alive:
            # We inflate the player rect slightly smaller for forgiving collision
            pr = self.player.rect.inflate(-8, -8)
            for v in self.vehicles:
                if v.alive and pr.colliderect(v.rect):
                    self._die()
                    break
                    
        # Win condition
        if self.player.alive and self.player.rect.y <= self.goal_y:
            self._win()

        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def _die(self):
        self.player.alive = False
        self.lives -= 1
        self.particles += [Particle(self.player.rect.centerx, self.player.rect.centery, RED) for _ in range(30)]
        snd_die.play()
        self.shake = 15
        
        if self.lives <= 0:
            self.game.coins += self.score
            self.result = "gameover"
            self.result_timer = 180
            from core.save_system import SaveSystem
            SaveSystem.save(self.game)
        else:
            self.result = "died"
            self.result_timer = 60

    def _win(self):
        coins_earned = 20 + self.level_idx * 10
        self.score += coins_earned
        self.particles += [Particle(self.player.rect.centerx, self.player.rect.centery, GOLD) for _ in range(30)]
        snd_coin.play()
        self.result = "win"
        self.result_timer = 120

    def draw(self, surface):
        ox = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        oy = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        
        temp = pygame.Surface((SCREEN_W, SCREEN_H))
        
        self.bg.draw(temp, self.safe_zones, self.lanes)
        
        # Adjust camera so player is somewhat visible if map goes higher
        # Map is fixed screen size for now based on generator limit
        
        for v in self.vehicles:
            v.draw(temp)
            
        self.player.draw(temp)
        
        for p in self.particles:
            p.draw(temp)
            
        surface.blit(temp, (ox, oy))
        
        extra = f"LIVES: {'♥'*self.lives}   SCORE: {self.score}"
        draw_hud(surface, self.game.coins, self.level_idx+1, extra)
        
        # Overlays
        if self.result:
            if self.result == "gameover":
                pygame.draw.rect(surface, (0,0,0), (SCREEN_W//2-220, SCREEN_H//2-80, 440, 160), border_radius=12)
                pygame.draw.rect(surface, RED, (SCREEN_W//2-220, SCREEN_H//2-80, 440, 160), 3, border_radius=12)
                t1 = font_md.render("SPLAT! GAME OVER", True, RED)
                t2 = font_sm.render(f"Total Score: {self.score}", True, WHITE)
                t3 = font_xs.render("Press SPACE to return", True, GRAY)
                surface.blit(t1, t1.get_rect(center=(SCREEN_W//2, SCREEN_H//2-44)))
                surface.blit(t2, t2.get_rect(center=(SCREEN_W//2, SCREEN_H//2+2)))
                surface.blit(t3, t3.get_rect(center=(SCREEN_W//2, SCREEN_H//2+44)))
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.result_timer -= 1
                    if self.result_timer <= 0:
                        self.game.state = "menu"
                        
            elif self.result == "win":
                pygame.draw.rect(surface, (0,0,0), (SCREEN_W//2-220, SCREEN_H//2-80, 440, 160), border_radius=12)
                pygame.draw.rect(surface, GOLD, (SCREEN_W//2-220, SCREEN_H//2-80, 440, 160), 3, border_radius=12)
                t1 = font_md.render("STREET CROSSED!", True, GOLD)
                t2 = font_sm.render(f"Earned {20 + self.level_idx * 10} coins", True, WHITE)
                surface.blit(t1, t1.get_rect(center=(SCREEN_W//2, SCREEN_H//2-20)))
                surface.blit(t2, t2.get_rect(center=(SCREEN_W//2, SCREEN_H//2+20)))
                
                self.result_timer -= 1
                if self.result_timer <= 0:
                    self.level_idx += 1
                    self.load_level()
                    self.result = None
                    
            elif self.result == "died":
                self.result_timer -= 1
                if self.result_timer <= 0:
                    self.player.reset()
                    self.result = None

        if self.paused:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surface.blit(overlay, (0,0))
            pt = font_lg.render("PAUSED", True, WHITE)
            surface.blit(pt, pt.get_rect(center=(SCREEN_W//2, SCREEN_H//2-90)))
            self.pause_btn.draw(surface)
            self.quit_btn.draw(surface)
