# games/mario/mario_game.py
import pygame
import random
from core.constants import SCREEN_W, SCREEN_H, RED, GREEN, CYAN, GOLD, WHITE, GRAY, YELLOW, BLACK
from core.assets import font_lg, font_md, font_sm, font_xs, snd_coin, snd_die, snd_hit
from ui.button import Button
from ui.particles import Particle
from ui.hud import draw_hud
from characters.character_data import CHARACTERS
from games.mario.player import Player
from games.mario.enemies import Enemy, BossMonster
from games.mario.platforms import Platform, MovingPlatform
from games.mario.collectibles import Collectible
from games.mario.levels import LEVELS

class MarioPlatformerGame:
    def __init__(self, game_ref):
        self.game = game_ref
        self.level_idx = 0
        self.lives = 3
        self.deaths = 0
        self.paused = False
        self.pause_btn = Button(SCREEN_W//2-80, SCREEN_H//2-30, 160, 50, "RESUME", GREEN)
        self.quit_btn  = Button(SCREEN_W//2-80, SCREEN_H//2+40, 160, 50, "QUIT", RED)
        self.particles = []
        self.shake = 0
        
        self.player = Player(CHARACTERS[self.game.selected_char])
        self.last_checkpoint_x = 100
        self.load_level()

    def load_level(self):
        ld = LEVELS[min(self.level_idx, len(LEVELS)-1)]
        self.platforms = []
        for pd in ld.get("platforms", []):
            if len(pd) == 3: self.platforms.append(Platform(pd[0], pd[1], pd[2]))
            else: self.platforms.append(Platform(pd[0], pd[1], pd[2], pd[3]))
            
        for pd in ld.get("moving_platforms", []):
            self.platforms.append(MovingPlatform(*pd))
            
        self.enemies = [Enemy(ex, ey, t) for ex, ey, t in ld.get("enemies", [])]
        self.collectibles = [Collectible(cx, cy, t) for cx, cy, t in ld.get("collectibles", [])]
        
        self.flag_x  = ld.get("flag_x")
        self.is_boss = ld.get("boss", False)
        self.checkpoints = ld.get("checkpoints", [])
        
        self.boss    = BossMonster() if self.is_boss else None
        
        # Reset player to last checkpoint
        self.player.reset(self.last_checkpoint_x, 400)
        self.offset_x = 0
        self.result  = None
        self.result_timer = 0
        self.stomp_tracker = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
        if self.paused:
            if self.pause_btn.is_clicked(event): self.paused = False
            if self.quit_btn.is_clicked(event):  self.game.state = "menu"
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                self.player.jump()

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.pause_btn.update(mx, my)
        self.quit_btn.update(mx, my)
        
        if self.paused or self.result is not None: return
        
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(self.platforms)
        
        # Update moving platforms
        for p in self.platforms:
            p.update()
            
        # Camera logic
        self.offset_x = max(0, self.player.rect.centerx - SCREEN_W//3)
        
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        if self.shake > 0: self.shake -= 1
        
        # Checkpoints
        for cp in self.checkpoints:
            if self.player.rect.x > cp and self.last_checkpoint_x < cp:
                self.last_checkpoint_x = cp
                self.particles += [Particle(cp, 400, GOLD) for _ in range(10)]
                snd_coin.play()
                
        # Collectibles
        for c in self.collectibles:
            if c.alive:
                c.update()
                if self.player.rect.colliderect(c.rect):
                    c.alive = False
                    snd_coin.play()
                    self.particles += [Particle(c.rect.centerx, c.rect.centery, YELLOW) for _ in range(5)]
                    if c.type == 'coin':
                        self.game.coins += 1
                    elif c.type == 'mushroom':
                        self.lives += 1
                    elif c.type == 'star':
                        self.player.powerup_timers['star'] = 600
                    elif c.type == 'lightning':
                        self.player.powerup_timers['lightning'] = 900
        
        # Enemy update & collision
        for e in self.enemies:
            e.update(self.platforms, self.offset_x)
            if e.alive and not e.stomped and self.player.invincible == 0:
                if self.player.powerup_timers['star'] > 0:
                    e.stomped = True
                    self.particles += [Particle(e.rect.centerx, e.rect.y, YELLOW) for _ in range(6)]
                    snd_hit.play()
                elif self.player.rect.colliderect(e.rect):
                    if self.player.vy > 0 and self.player.rect.bottom < e.rect.centery + 10 and e.type != "Spiky":
                        e.stomped = True; self.player.vy = -8
                        self.particles += [Particle(e.rect.centerx, e.rect.y, YELLOW) for _ in range(6)]
                        snd_hit.play()
                    else:
                        self._player_hurt()
        
        self.enemies = [e for e in self.enemies if e.alive]
        
        # Boss
        if self.boss and self.boss.alive:
            self.boss.update(self.platforms)
            pr = self.player.rect
            if pr.colliderect(self.boss.rect) and self.player.invincible == 0:
                if self.player.powerup_timers['star'] > 0:
                    self.boss.stomp()
                elif self.player.vy > 0 and pr.bottom < self.boss.rect.centery + 12:
                    self.boss.stomp(); self.player.vy = -10
                    self.stomp_tracker += 1
                    self.particles += [Particle(self.boss.rect.centerx, self.boss.rect.y, RED) for _ in range(10)]
                else:
                    self._player_hurt()
                    
            for proj in self.boss.projectiles:
                pr2 = pygame.Rect(proj["x"]-8, proj["y"]-8, 16, 16)
                if pr.colliderect(pr2) and self.player.invincible == 0:
                    if self.player.powerup_timers['star'] <= 0:
                        self._player_hurt()
                        
            if not self.boss.alive:
                won_clean = self.deaths == 0
                coins = 150 if won_clean else 50
                self.game.coins += coins
                snd_coin.play()
                from core.save_system import SaveSystem
                SaveSystem.save(self.game)
                self.result = "boss_win" if won_clean else "win"
                self.result_timer = 180
                
        # Pit death
        if self.player.rect.top > SCREEN_H + 60:
            self._player_hurt(pit=True)
            
        # Flag
        if self.flag_x and self.player.rect.right >= self.flag_x:
            self._finish_level()

    def _player_hurt(self, pit=False):
        if self.player.invincible > 0: return
        
        if self.player.has_shield and not pit:
            self.player.has_shield = False
            self.player.invincible = 60
            snd_hit.play()
            return

        self.lives -= 1; self.deaths += 1
        self.shake = 12; snd_die.play()
        self.particles += [Particle(self.player.rect.centerx, self.player.rect.centery, RED) for _ in range(15)]
        if self.lives <= 0:
            self.game.coins += 10
            snd_coin.play()
            from core.save_system import SaveSystem
            SaveSystem.save(self.game)
            self.result = "gameover"; self.result_timer = 200
        else:
            self.player.reset(self.last_checkpoint_x, 400)

    def _finish_level(self):
        if self.deaths == 0:
            coins = 100
        elif self.deaths <= 2:
            coins = 50
        else:
            coins = 20
        self.game.coins += coins
        snd_coin.play()
        from core.save_system import SaveSystem
        SaveSystem.save(self.game)
        self.result = "win"; self.result_timer = 200

    def draw(self, surface):
        ox = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        
        # Sky gradient
        for i in range(SCREEN_H):
            ratio = i / SCREEN_H
            r = int(50+ratio*20); g = int(120+ratio*40); b = int(220-ratio*100)
            pygame.draw.line(surface, (r,g,b), (0+ox,i), (SCREEN_W+ox,i))
            
        # Clouds
        for cxb, cyb in [(100,100),(350,140),(650,100),(900,130),(1150,110)]:
            cx2 = (cxb - self.offset_x//4) % SCREEN_W
            pygame.draw.ellipse(surface, (240,240,255), (cx2+ox, cyb, 120, 50))
            pygame.draw.ellipse(surface, (240,240,255), (cx2+40+ox, cyb-25, 90, 50))
            
        # Platforms
        for plat in self.platforms: plat.draw(surface, self.offset_x)
        
        # Checkpoints visually
        for cp in self.checkpoints:
            cx = cp - self.offset_x
            color = GOLD if self.last_checkpoint_x >= cp else GRAY
            pygame.draw.rect(surface, color, (cx, 400, 10, 40))
            pygame.draw.circle(surface, color, (cx+5, 400), 10)
            
        # Flag
        if self.flag_x:
            fx = self.flag_x - self.offset_x
            pygame.draw.rect(surface, (180,140,80), (fx-4, 300, 8, 280))
            pygame.draw.polygon(surface, RED, [(fx, 300),(fx+50, 320),(fx, 340)])
            
        # Collectibles
        for c in self.collectibles: c.draw(surface, self.offset_x)
            
        # Enemies
        for e in self.enemies: e.draw(surface, self.offset_x)
        
        # Boss
        if self.boss: self.boss.draw(surface, self.offset_x)
        
        # Player
        self.player.draw(surface, self.offset_x)
        
        # Particles
        for p in self.particles: p.draw(surface)
        
        # HUD
        extra = f"LIVES: {'♥'*self.lives}"
        if self.player.powerup_timers['star'] > 0: extra += " [STAR]"
        if self.player.powerup_timers['lightning'] > 0: extra += " [DOUBLE JUMP]"
        draw_hud(surface, self.game.coins, self.level_idx+1, extra)
        
        # Result overlay
        if self.result:
            msgs = {"boss_win":("BOSS DEFEATED! +150","LEGENDARY!",GOLD),
                    "win":     ("LEVEL CLEAR!","Continue...",GREEN),
                    "gameover":("GAME OVER +10","You lost all lives",RED)}
            title, sub, col = msgs.get(self.result, ("...","",WHITE))
            pygame.draw.rect(surface, (0,0,0), (SCREEN_W//2-220, SCREEN_H//2-80, 440, 160), border_radius=12)
            pygame.draw.rect(surface, col, (SCREEN_W//2-220, SCREEN_H//2-80, 440, 160), 3, border_radius=12)
            t1 = font_md.render(title, True, col)
            t2 = font_sm.render(sub, True, WHITE)
            t3 = font_xs.render("Press SPACE to continue", True, GRAY)
            surface.blit(t1, t1.get_rect(center=(SCREEN_W//2, SCREEN_H//2-44)))
            surface.blit(t2, t2.get_rect(center=(SCREEN_W//2, SCREEN_H//2+2)))
            surface.blit(t3, t3.get_rect(center=(SCREEN_W//2, SCREEN_H//2+44)))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.result_timer -= 1
                if self.result_timer <= 0:
                    if self.result == "gameover":
                        self.lives = 3; self.deaths = 0; self.last_checkpoint_x = 100
                        self.load_level()
                    else:
                        self.level_idx = min(self.level_idx+1, len(LEVELS)-1)
                        self.last_checkpoint_x = 100
                        self.load_level()
                        
        # Pause
        if self.paused:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surface.blit(overlay, (0,0))
            pt = font_lg.render("PAUSED", True, WHITE)
            surface.blit(pt, pt.get_rect(center=(SCREEN_W//2, SCREEN_H//2-90)))
            self.pause_btn.draw(surface)
            self.quit_btn.draw(surface)
