# games/duck_hunt/duck_hunt.py
import pygame
import random
from core.constants import SCREEN_W, SCREEN_H, RED, GREEN, CYAN, GOLD, WHITE, GRAY, YELLOW, BLACK
from core.assets import font_lg, font_md, font_sm, font_xs, snd_shoot, snd_hit, snd_coin, snd_die
from ui.button import Button
from ui.particles import Particle
from ui.hud import draw_hud
from games.duck_hunt.duck import Duck, BossDuck
from games.duck_hunt.background import DuckHuntBackground
from games.duck_hunt.powerups import PowerUp

class DuckHuntGame:
    LEVEL_DATA = [
        {"ducks":5,  "ammo":12, "time":40, "boss":False},
        {"ducks":8,  "ammo":15, "time":45, "boss":False},
        {"ducks":10, "ammo":18, "time":50, "boss":False},
        {"ducks":1,  "ammo":25, "time":60, "boss":True},
        {"ducks":12, "ammo":20, "time":50, "boss":False},
        {"ducks":14, "ammo":22, "time":55, "boss":False},
        {"ducks":1,  "ammo":30, "time":70, "boss":True},
    ]

    def __init__(self, game_ref):
        self.game = game_ref
        self.level = 0
        self.reset_level()
        self.bg = DuckHuntBackground()
        self.particles = []
        self.powerups = []
        self.shake = 0
        self.paused = False
        
        self.pause_btn = Button(SCREEN_W//2-80, SCREEN_H//2-30, 160, 50, "RESUME", GREEN)
        self.quit_btn  = Button(SCREEN_W//2-80, SCREEN_H//2+40, 160, 50, "QUIT", RED)
        
        self.combo = 0
        self.double_damage_timer = 0
        self.freeze_timer = 0

    def reset_level(self):
        ld = self.LEVEL_DATA[min(self.level, len(self.LEVEL_DATA)-1)]
        self.is_boss = ld["boss"]
        self.ammo = ld["ammo"]
        self.max_ammo = ld["ammo"]
        self.time_left = ld["time"] * 60 # FPS
        self.ducks = []
        self.boss = None
        self.shots_fired = 0
        self.ducks_hit = 0
        self.ducks_missed = 0
        self.total_ducks = ld["ducks"]
        self.spawn_timer = 0
        self.spawn_interval = 90
        self.spawned = 0
        self.result = None
        self.result_timer = 0
        self.combo = 0
        self.powerups = []
        
        if self.is_boss:
            self.boss = BossDuck()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
            
        if self.paused:
            if self.pause_btn.is_clicked(event): self.paused = False
            if self.quit_btn.is_clicked(event):  self.game.state = "menu"
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ammo > 0 and self.result is None:
                self.ammo -= 1
                self.shots_fired += 1
                snd_shoot.play()
                mx, my = event.pos
                hit_any = False
                damage = 2 if self.double_damage_timer > 0 else 1
                
                # Check Powerups
                for p in self.powerups:
                    if p.alive and p.get_rect().collidepoint(mx, my):
                        p.alive = False
                        self.activate_powerup(p.type)
                        self.particles += [Particle(mx, my, YELLOW) for _ in range(8)]
                        hit_any = True
                
                if self.is_boss and self.boss and self.boss.alive:
                    if self.boss.get_rect().collidepoint(mx, my):
                        killed = self.boss.take_damage(damage)
                        hit_any = True
                        self.particles += [Particle(mx, my, GOLD) for _ in range(12)]
                        snd_hit.play()
                        if killed:
                            self.ducks_hit += 1
                            snd_coin.play()
                else:
                    for d in self.ducks:
                        if d.alive and not d.hit and d.get_rect().collidepoint(mx, my) and d.visible:
                            killed = d.take_damage(damage)
                            hit_any = True
                            snd_hit.play()
                            self.particles += [Particle(mx, my, d.color) for _ in range(8)]
                            if killed:
                                self.ducks_hit += 1
                                self.combo += 1
                                
                                # Combo multiplier
                                mult = 1
                                if self.combo >= 7: mult = 3
                                elif self.combo >= 4: mult = 2
                                elif self.combo >= 2: mult = 1.5
                                
                                gained = int(d.coin_value * mult)
                                self.game.coins += gained
                                
                                if d.type == "Fat":
                                    self.ammo += 2
                                elif d.type == "Bomb":
                                    self.ammo = max(0, self.ammo - 1)
                                    
                            break
                            
                if not hit_any:
                    self.shake = 6
                    self.combo = 0

    def activate_powerup(self, p_type):
        if p_type == "DoubleDamage":
            self.double_damage_timer = 600 # 10 seconds
        elif p_type == "ExtraAmmo":
            self.ammo += 5
        elif p_type == "TimeFreeze":
            self.freeze_timer = 300 # 5 seconds
        elif p_type == "Bomb":
            for d in self.ducks:
                if d.alive and not d.hit:
                    d.take_damage(10)
                    self.ducks_hit += 1
                    self.particles += [Particle(d.x, d.y, ORANGE) for _ in range(10)]
            snd_hit.play()

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.pause_btn.update(mx, my)
        self.quit_btn.update(mx, my)
        
        if self.paused or self.result is not None: return
        
        self.time_left -= 1
        if self.double_damage_timer > 0: self.double_damage_timer -= 1
        if self.freeze_timer > 0: self.freeze_timer -= 1
        
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        for p in self.powerups: p.update()
        self.powerups = [p for p in self.powerups if p.alive]
        
        if self.shake > 0: self.shake -= 1

        if self.is_boss:
            if self.boss and self.boss.alive:
                if self.freeze_timer <= 0:
                    self.boss.update()
            elif self.boss and not self.boss.alive:
                self._finish("boss_win")
        else:
            if self.freeze_timer <= 0:
                self.spawn_timer += 1
                if self.spawn_timer >= self.spawn_interval and self.spawned < self.total_ducks:
                    self.ducks.append(Duck(self.level))
                    self.spawned += 1
                    self.spawn_timer = 0
                    self.spawn_interval = max(40, 90 - self.level*10)
                    
                    # Random powerup spawn
                    if random.random() < 0.1:
                        self.powerups.append(PowerUp())
                        
                for d in self.ducks:
                    d.update()
                    if not d.hit and d.is_offscreen():
                        self.ducks_missed += 1
                        d.alive = False
                        self.combo = 0
            
            self.ducks = [d for d in self.ducks if d.alive]
            all_spawned = self.spawned >= self.total_ducks
            all_gone   = len(self.ducks) == 0 and all_spawned
            
            if all_gone:
                if self.ducks_hit >= self.total_ducks:
                    self._finish("win_perfect" if self.shots_fired == self.ducks_hit else "win")
                else:
                    self._finish("lose")
                    
        if self.ammo <= 0 and not self.is_boss:
            all_spawned = self.spawned >= self.total_ducks
            if all_spawned and len(self.ducks)==0: pass
            else:
                self._finish("lose")
                
        if self.time_left <= 0:
            self._finish("lose")

    def _finish(self, result):
        self.result = result
        self.result_timer = 180
        if result == "boss_win":
            coins = 150
        elif result == "win_perfect":
            coins = 100
        elif result == "win":
            coins = 50
        else:
            coins = 10
        self.game.coins += coins
        snd_coin.play()
        from core.save_system import SaveSystem
        SaveSystem.save(self.game)

    def draw(self, surface):
        ox = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        oy = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        
        # We draw bg to a temp surface to apply shake easily or just pass offset
        temp_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        self.bg.draw(temp_surface)
        
        # Ducks
        for d in self.ducks: d.draw(temp_surface)
        if self.boss: self.boss.draw(temp_surface)
        
        # Powerups
        for p in self.powerups: p.draw(temp_surface)
        
        # Particles
        for p in self.particles: p.draw(temp_surface)
        
        surface.blit(temp_surface, (ox, oy))
        
        # Crosshair
        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(surface, RED, (mx-20, my), (mx+20, my), 2)
        pygame.draw.line(surface, RED, (mx, my-20), (mx, my+20), 2)
        pygame.draw.circle(surface, RED, (mx, my), 10, 2)
        pygame.draw.circle(surface, WHITE, (mx, my), 4, 1)
        
        # HUD
        extra = f"AMMO:{self.ammo}/{self.max_ammo}  TIME:{self.time_left//60}"
        if self.combo > 1:
            extra += f"  COMBO x{self.combo}"
        draw_hud(surface, self.game.coins, self.level+1, extra)
        
        # Ammo bar
        for i in range(self.max_ammo):
            bx = 20 + i*22
            bc = YELLOW if i < self.ammo else GRAY
            pygame.draw.rect(surface, bc, (bx, 52, 16, 8))
            
        # Buff indicators
        if self.double_damage_timer > 0:
            txt = font_sm.render(f"2X DAMAGE: {self.double_damage_timer//60}s", True, RED)
            surface.blit(txt, (20, 70))
        if self.freeze_timer > 0:
            txt = font_sm.render(f"FROZEN: {self.freeze_timer//60}s", True, CYAN)
            surface.blit(txt, (20, 100))
            
        # Result overlay
        if self.result:
            msgs = {"boss_win":("BOSS DEFEATED! +150","You are LEGENDARY!",GOLD),
                    "win_perfect":("PERFECT ROUND! +100","All ducks, no misses!",GREEN),
                    "win":("LEVEL CLEAR! +50","Ducks defeated!",CYAN),
                    "lose":("LEVEL FAILED +10","Better luck next time",RED)}
            title, sub, col = msgs.get(self.result, ("..","",WHITE))
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
                    self.level = min(self.level+1, len(self.LEVEL_DATA)-1)
                    self.reset_level()
                    
        # Pause
        if self.paused:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surface.blit(overlay, (0,0))
            pt = font_lg.render("PAUSED", True, WHITE)
            surface.blit(pt, pt.get_rect(center=(SCREEN_W//2, SCREEN_H//2-90)))
            self.pause_btn.draw(surface)
            self.quit_btn.draw(surface)
