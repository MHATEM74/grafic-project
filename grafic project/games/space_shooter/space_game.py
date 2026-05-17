# games/space_shooter/space_game.py
import pygame
import random
from core.constants import SCREEN_W, SCREEN_H, RED, GREEN, CYAN, GOLD, WHITE, GRAY, YELLOW, BLACK
from core.assets import font_lg, font_md, font_sm, font_xs, snd_coin, snd_die, snd_hit
from ui.button import Button
from ui.particles import Particle
from ui.hud import draw_hud
from characters.character_data import CHARACTERS
from games.space_shooter.ship import Ship
from games.space_shooter.enemies import SpaceEnemy, SpaceBoss
from games.space_shooter.powerups import SpacePowerUp
from games.space_shooter.background import StarfieldBackground

class SpaceShooterGame:
    def __init__(self, game_ref):
        self.game = game_ref
        self.paused = False
        self.pause_btn = Button(SCREEN_W//2-80, SCREEN_H//2-30, 160, 50, "RESUME", GREEN)
        self.quit_btn  = Button(SCREEN_W//2-80, SCREEN_H//2+40, 160, 50, "QUIT", RED)
        
        self.bg = StarfieldBackground()
        self.particles = []
        self.bullets = []
        self.enemies = []
        self.powerups = []
        
        self.ship = Ship(CHARACTERS[self.game.selected_char])
        
        self.wave = 1
        self.spawn_timer = 0
        self.enemies_to_spawn = 10
        self.enemies_spawned = 0
        self.boss = None
        
        self.score = 0
        self.shake = 0
        
        self.result = None
        self.result_timer = 0

    def start_wave(self):
        self.enemies_spawned = 0
        self.enemies_to_spawn = 5 + self.wave * 5
        self.spawn_timer = 60
        self.boss = None
        if self.wave % 5 == 0:
            self.boss = SpaceBoss()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
        if self.paused:
            if self.pause_btn.is_clicked(event): self.paused = False
            if self.quit_btn.is_clicked(event):  self.game.state = "menu"
            return

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.pause_btn.update(mx, my)
        self.quit_btn.update(mx, my)
        
        if self.paused or self.result is not None: return
        
        if self.shake > 0: self.shake -= 1
        
        keys = pygame.key.get_pressed()
        self.ship.handle_input(keys, self.bullets)
        self.ship.update()
        
        # Spawning
        if not self.boss:
            if self.enemies_spawned < self.enemies_to_spawn:
                self.spawn_timer -= 1
                if self.spawn_timer <= 0:
                    self.spawn_timer = max(30, 90 - self.wave * 5)
                    self.enemies_spawned += 1
                    
                    types = ["Drone"]
                    if self.wave > 1: types.append("Fighter")
                    if self.wave > 3: types.append("Carrier")
                    
                    self.enemies.append(SpaceEnemy(random.randint(50, SCREEN_W-50), -50, random.choice(types)))
            elif len(self.enemies) == 0:
                self.wave += 1
                self.start_wave()
                
        # Boss logic
        if self.boss:
            if self.boss.alive:
                self.boss.update(self.bullets)
            else:
                self.score += 500
                self.wave += 1
                self.start_wave()
                self.particles += [Particle(self.boss.rect.centerx, self.boss.rect.centery, GOLD) for _ in range(30)]
                snd_coin.play()
                
        # Bullets
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]
        
        # Powerups
        for p in self.powerups:
            p.update()
            if self.ship.alive and p.rect.colliderect(self.ship.rect):
                p.alive = False
                snd_coin.play()
                self.particles += [Particle(p.rect.centerx, p.rect.centery, YELLOW) for _ in range(10)]
                if p.type == 'Laser':
                    self.ship.laser_timer = 600
                elif p.type == 'Triple':
                    self.ship.weapon_level = min(3, self.ship.weapon_level + 1)
                elif p.type == 'Shield':
                    self.ship.shield_hp += 1
                elif p.type == 'Nuke':
                    # Damage all enemies
                    for e in self.enemies: e.take_damage(10)
                    if self.boss: self.boss.take_damage(10)
                    snd_hit.play()
                    self.shake = 10
                    self.particles += [Particle(random.randint(0, SCREEN_W), random.randint(0, SCREEN_H), ORANGE) for _ in range(20)]
        self.powerups = [p for p in self.powerups if p.alive]
        
        # Enemies
        for e in self.enemies:
            e.update(self.bullets)
        self.enemies = [e for e in self.enemies if e.alive]
        
        # Collisions
        if self.ship.alive:
            player_rect = self.ship.rect
            for b in self.bullets:
                if b.alive:
                    if b.is_enemy and b.get_rect().colliderect(player_rect):
                        b.alive = False
                        if self.ship.take_damage():
                            self._die()
                    elif not b.is_enemy:
                        # Player bullet hits enemy
                        hit_something = False
                        if self.boss and self.boss.alive and b.get_rect().colliderect(self.boss.rect):
                            if self.boss.take_damage(b.damage):
                                pass
                            hit_something = True
                        else:
                            for e in self.enemies:
                                if e.alive and b.get_rect().colliderect(e.rect):
                                    if e.take_damage(b.damage):
                                        self.score += e.score_val
                                        if random.random() < 0.1: # 10% drop rate
                                            p_types = ['Laser', 'Shield', 'Triple', 'Nuke']
                                            self.powerups.append(SpacePowerUp(e.rect.centerx, e.rect.centery, random.choice(p_types)))
                                    hit_something = True
                                    break
                                    
                        if hit_something:
                            if b.type != "Laser": # Laser pierces
                                b.alive = False
                            self.particles += [Particle(b.x, b.y, YELLOW) for _ in range(5)]
                            snd_hit.play()
                            
            # Ship collision with enemies
            if self.boss and self.boss.alive and player_rect.colliderect(self.boss.rect):
                if self.ship.take_damage(): self._die()
            for e in self.enemies:
                if e.alive and player_rect.colliderect(e.rect):
                    e.take_damage(5)
                    if self.ship.take_damage(): self._die()

        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def _die(self):
        self.particles += [Particle(self.ship.rect.centerx, self.ship.rect.centery, RED) for _ in range(30)]
        snd_die.play()
        self.shake = 20
        # Coins based on score
        earned_coins = self.score // 10
        self.game.coins += earned_coins
        self.result = "gameover"
        self.result_timer = 200
        from core.save_system import SaveSystem
        SaveSystem.save(self.game)

    def draw(self, surface):
        ox = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        oy = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        
        temp_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        
        self.bg.draw(temp_surface)
        
        for p in self.powerups: p.draw(temp_surface)
        for b in self.bullets: b.draw(temp_surface)
        for e in self.enemies: e.draw(temp_surface)
        if self.boss: self.boss.draw(temp_surface)
        
        self.ship.draw(temp_surface)
        
        for p in self.particles: p.draw(temp_surface)
        
        surface.blit(temp_surface, (ox, oy))
        
        extra = f"WAVE: {self.wave}   SCORE: {self.score}"
        draw_hud(surface, self.game.coins, self.wave, extra)
        
        # Result overlay
        if self.result:
            pygame.draw.rect(surface, (0,0,0), (SCREEN_W//2-220, SCREEN_H//2-80, 440, 160), border_radius=12)
            pygame.draw.rect(surface, RED, (SCREEN_W//2-220, SCREEN_H//2-80, 440, 160), 3, border_radius=12)
            t1 = font_md.render(f"GAME OVER", True, RED)
            t2 = font_sm.render(f"Score: {self.score} | Earned: {self.score//10} coins", True, WHITE)
            t3 = font_xs.render("Press SPACE to return to Menu", True, GRAY)
            surface.blit(t1, t1.get_rect(center=(SCREEN_W//2, SCREEN_H//2-44)))
            surface.blit(t2, t2.get_rect(center=(SCREEN_W//2, SCREEN_H//2+2)))
            surface.blit(t3, t3.get_rect(center=(SCREEN_W//2, SCREEN_H//2+44)))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.result_timer -= 1
                if self.result_timer <= 0:
                    self.game.state = "menu"
                    
        # Pause
        if self.paused:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surface.blit(overlay, (0,0))
            pt = font_lg.render("PAUSED", True, WHITE)
            surface.blit(pt, pt.get_rect(center=(SCREEN_W//2, SCREEN_H//2-90)))
            self.pause_btn.draw(surface)
            self.quit_btn.draw(surface)
