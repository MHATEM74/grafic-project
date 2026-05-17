import pygame
import sys
import json
import os
import math
import random
import time

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

SCREEN_W, SCREEN_H = 1024, 768
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Pixel Game Hub")
clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK   = (0,0,0)
WHITE   = (255,255,255)
RED     = (220,50,50)
GREEN   = (50,200,80)
BLUE    = (50,100,220)
YELLOW  = (255,220,0)
ORANGE  = (255,140,0)
PURPLE  = (150,50,220)
CYAN    = (0,220,220)
PINK    = (255,100,180)
GOLD    = (255,200,0)
DARK    = (20,20,35)
DARKER  = (12,12,22)
GRAY    = (120,120,140)
LGRAY   = (200,200,220)

# Fonts
try:
    font_lg = pygame.font.SysFont("couriernew", 52, bold=True)
    font_md = pygame.font.SysFont("couriernew", 32, bold=True)
    font_sm = pygame.font.SysFont("couriernew", 22, bold=True)
    font_xs = pygame.font.SysFont("couriernew", 16, bold=True)
except:
    font_lg = pygame.font.Font(None, 52)
    font_md = pygame.font.Font(None, 32)
    font_sm = pygame.font.Font(None, 22)
    font_xs = pygame.font.Font(None, 16)

def make_beep(freq=440, duration=0.1, volume=0.3):
    sample_rate = 22050
    n = int(sample_rate * duration)
    buf = bytearray(n * 2)
    for i in range(n):
        val = int(32767 * volume * math.sin(2 * math.pi * freq * i / sample_rate))
        buf[i*2] = val & 0xFF
        buf[i*2+1] = (val >> 8) & 0xFF
    sound = pygame.mixer.Sound(buffer=bytes(buf))
    return sound

snd_shoot  = make_beep(800, 0.05, 0.4)
snd_hit    = make_beep(300, 0.12, 0.5)
snd_coin   = make_beep(1200, 0.08, 0.4)
snd_jump   = make_beep(600, 0.08, 0.3)
snd_die    = make_beep(200, 0.3, 0.5)
snd_select = make_beep(900, 0.06, 0.3)
snd_buy    = make_beep(1400, 0.15, 0.4)

CHARACTERS = [
    {"id":0,"name":"Alex",   "gender":"Male",   "color":(70,130,220),  "cost":0,   "owned":True,  "accent":(200,220,255)},
    {"id":1,"name":"Mia",    "gender":"Female", "color":(230,80,160),  "cost":0,   "owned":True,  "accent":(255,180,220)},
    {"id":2,"name":"Shadow", "gender":"Male",   "color":(90,30,130),   "cost":200, "owned":False, "accent":(180,100,255)},
    {"id":3,"name":"Blaze",  "gender":"Female", "color":(220,60,20),   "cost":200, "owned":False, "accent":(255,180,80)},
    {"id":4,"name":"Phantom","gender":"Male",   "color":(200,200,220), "cost":350, "owned":False, "accent":(255,255,255)},
    {"id":5,"name":"Aurora", "gender":"Female", "color":(30,180,160),  "cost":350, "owned":False, "accent":(255,210,80)},
    {"id":6,"name":"Titan",  "gender":"Male",   "color":(100,60,30),   "cost":500, "owned":False, "accent":(200,150,80)},
    {"id":7,"name":"Seraph", "gender":"Female", "color":(240,230,200), "cost":500, "owned":False, "accent":(255,255,180)},
    {"id":8,"name":"Void",   "gender":"Male",   "color":(10,10,20),    "cost":750, "owned":False, "accent":(0,255,100)},
    {"id":9,"name":"Nova",   "gender":"Female", "color":(80,20,130),   "cost":750, "owned":False, "accent":(200,150,255)},
]

def draw_character_sprite(surface, char_data, cx, cy, scale=1.0, anim=0):
    c  = char_data["color"]
    ac = char_data["accent"]
    s  = scale
    gender = char_data["gender"]
    cid = char_data["id"]

    # Shadow
    pygame.draw.ellipse(surface, (0,0,0,80), (int(cx-18*s), int(cy+28*s), int(36*s), int(8*s)))

    # Body
    body_y = cy + math.sin(anim*0.05)*3
    # Legs
    lleg_ang = math.sin(anim*0.15)*15
    pygame.draw.rect(surface, c, (int(cx-10*s), int(body_y+14*s), int(8*s), int(18*s)))
    pygame.draw.rect(surface, c, (int(cx+2*s),  int(body_y+14*s), int(8*s), int(18*s)))
    # Shoes
    shoe_c = (30,30,30) if cid not in [7,4] else (180,180,200)
    pygame.draw.rect(surface, shoe_c, (int(cx-12*s), int(body_y+30*s), int(12*s), int(5*s)))
    pygame.draw.rect(surface, shoe_c, (int(cx+2*s),  int(body_y+30*s), int(12*s), int(5*s)))
    # Torso
    pygame.draw.rect(surface, c, (int(cx-13*s), int(body_y), int(26*s), int(18*s)))
    # Arms
    arm_ang = math.sin(anim*0.15+1)*20
    pygame.draw.rect(surface, c, (int(cx-20*s), int(body_y+2*s), int(8*s), int(14*s)))
    pygame.draw.rect(surface, c, (int(cx+12*s), int(body_y+2*s), int(8*s), int(14*s)))
    # Accent stripe
    pygame.draw.rect(surface, ac, (int(cx-13*s), int(body_y+5*s), int(26*s), int(4*s)))
    # Head
    head_c = (255,220,180) if gender=="Male" else (255,200,170)
    if cid == 8: head_c = (20,20,30)
    if cid == 4: head_c = (220,230,240)
    pygame.draw.rect(surface, head_c, (int(cx-12*s), int(body_y-22*s), int(24*s), int(22*s)))
    # Eyes
    pygame.draw.rect(surface, BLACK, (int(cx-7*s), int(body_y-16*s), int(4*s), int(4*s)))
    pygame.draw.rect(surface, BLACK, (int(cx+3*s), int(body_y-16*s), int(4*s), int(4*s)))
    if cid == 8:
        pygame.draw.rect(surface, (0,255,100), (int(cx-7*s), int(body_y-16*s), int(4*s), int(4*s)))
        pygame.draw.rect(surface, (0,255,100), (int(cx+3*s), int(body_y-16*s), int(4*s), int(4*s)))
    # Hair
    hair_c = (50,30,10)
    if cid == 1: hair_c = (200,50,100)
    if cid == 3: hair_c = (180,40,10)
    if cid == 5: hair_c = (20,180,160)
    if cid == 7: hair_c = (255,250,230)
    if cid == 8: hair_c = (0,200,80)
    if cid == 9: hair_c = (120,40,180)
    pygame.draw.rect(surface, hair_c, (int(cx-12*s), int(body_y-26*s), int(24*s), int(8*s)))
    if gender == "Female":
        pygame.draw.rect(surface, hair_c, (int(cx-14*s), int(body_y-22*s), int(4*s), int(16*s)))
        pygame.draw.rect(surface, hair_c, (int(cx+10*s), int(body_y-22*s), int(4*s), int(16*s)))
    # Special features
    if cid == 7:  # Titan - big shoulders
        pygame.draw.rect(surface, c, (int(cx-24*s), int(body_y-4*s), int(12*s), int(10*s)))
        pygame.draw.rect(surface, c, (int(cx+12*s), int(body_y-4*s), int(12*s), int(10*s)))
    if cid == 9:  # Nova - stars
        for sx, sy in [(-18,-10),(16,-5),(-5,-30),(20,-20)]:
            pygame.draw.circle(surface, ac, (int(cx+sx*s), int(body_y+sy*s)), int(2*s))

class SaveSystem:
    PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savegame.json")

    @staticmethod
    def load():
        if os.path.exists(SaveSystem.PATH):
            try:
                with open(SaveSystem.PATH, "r") as f:
                    data = json.load(f)
                for ch in CHARACTERS:
                    cid = str(ch["id"])
                    if cid in data.get("owned", {}):
                        ch["owned"] = data["owned"][cid]
                return data.get("coins", 0), data.get("selected_char", 0)
            except:
                pass
        return 0, 0

    @staticmethod
    def save(coins, selected_char):
        owned = {str(ch["id"]): ch["owned"] for ch in CHARACTERS}
        data = {"coins": coins, "selected_char": selected_char, "owned": owned}
        with open(SaveSystem.PATH, "w") as f:
            json.dump(data, f)

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

class Button:
    def __init__(self, x, y, w, h, text, color=BLUE, text_color=WHITE, font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text; self.color = color
        self.text_color = text_color
        self.font = font or font_sm
        self.hovered = False; self.pressed = False
        self.anim = 0

    def update(self, mx, my):
        self.hovered = self.rect.collidepoint(mx, my)
        self.anim = min(self.anim+1, 10) if self.hovered else max(self.anim-1, 0)

    def draw(self, surface):
        off = int(self.anim * 0.5)
        r = self.rect.inflate(off*2, off*2)
        shade = tuple(min(255, c+40) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(surface, (0,0,0), r.move(3,3), border_radius=6)
        pygame.draw.rect(surface, shade, r, border_radius=6)
        pygame.draw.rect(surface, WHITE, r, 2, border_radius=6)
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=r.center))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                snd_select.play()
                return True
        return False

def draw_hud(surface, coins, level, extra=""):
    pygame.draw.rect(surface, (0,0,0,180), (0, 0, SCREEN_W, 44))
    pygame.draw.rect(surface, GOLD, (0, 44, SCREEN_W, 2))
    coin_txt = font_sm.render(f"COINS: {coins}", True, GOLD)
    lvl_txt  = font_sm.render(f"LEVEL: {level}", True, CYAN)
    ext_txt  = font_sm.render(extra, True, WHITE)
    surface.blit(coin_txt, (12, 10))
    surface.blit(lvl_txt,  (SCREEN_W//2 - lvl_txt.get_width()//2, 10))
    surface.blit(ext_txt,  (SCREEN_W - ext_txt.get_width() - 12, 10))

def fade_transition(surface, color=BLACK, speed=8):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H))
    overlay.fill(color)
    for alpha in range(0, 256, speed):
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0,0))
        pygame.display.flip()
        clock.tick(FPS)
    for alpha in range(255, -1, -speed):
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0,0))
        pygame.display.flip()
        clock.tick(FPS)

def draw_stars_bg(surface, stars, scroll=0):
    surface.fill(DARKER)
    for sx, sy, sz in stars:
        bright = int(150 + sz * 35)
        c = (bright, bright, bright)
        pygame.draw.rect(surface, c, ((sx + scroll*sz*0.01) % SCREEN_W, sy, sz, sz))

def draw_text_shadow(surface, text, font, color, x, y, shadow=(0,0,0)):
    s = font.render(text, True, shadow)
    surface.blit(s, (x+2, y+2))
    t = font.render(text, True, color)
    surface.blit(t, (x, y))

# ---------------------------------------------------------
#  DUCK HUNT MINI-GAME
# ---------------------------------------------------------
class Duck:
    PATTERNS = ["linear","zigzag","diagonal","sine"]
    def __init__(self, level):
        self.level = level
        speed_base = 2 + level * 0.8
        self.speed = random.uniform(speed_base, speed_base+2)
        side = random.choice(["left","right"])
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

    def update(self):
        self.t += 1
        self.anim += 1
        if self.anim % 8 == 0:
            self.wing_up = not self.wing_up
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

    def draw(self, surface):
        if not self.alive: return
        c = self.color
        x, y = int(self.x), int(self.y)
        flip = self.vx < 0
        # Body
        pygame.draw.ellipse(surface, c, (x-18, y-12, 36, 24))
        # Head
        pygame.draw.circle(surface, c, (x+20 if not flip else x-20, y-8), 12)
        # Bill
        bc = (255, 180, 0)
        bx = x+30 if not flip else x-30
        pygame.draw.ellipse(surface, bc, (bx-8, y-10, 16, 7))
        # Eye
        ex = x+22 if not flip else x-22
        pygame.draw.circle(surface, BLACK, (ex, y-11), 3)
        pygame.draw.circle(surface, WHITE, (ex+1, y-12), 1)
        # Wing
        wing_y = y-18 if self.wing_up else y-6
        pygame.draw.ellipse(surface, tuple(min(255,c+40) for c in c), (x-14, wing_y, 28, 14))
        # Tail
        tx = x-22 if not flip else x+22
        pygame.draw.ellipse(surface, (30,100,30), (tx-8, y-6, 16, 12))
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
        pygame.draw.rect(surface, GREEN, (x-50, y-60, int(bw*(self.hp/self.max_hp)), 10))
        pygame.draw.rect(surface, WHITE, (x-50, y-60, bw, 10), 2)
        txt = font_xs.render(f"BOSS HP: {self.hp}", True, WHITE)
        surface.blit(txt, (x-50, y-78))

    def hit_duck(self):
        self.hp -= 1
        self.hit_flash = 8
        snd_hit.play()
        if self.hp <= 0:
            self.alive = False

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
        self.stars = [(random.randint(0,SCREEN_W), random.randint(0,100), random.randint(1,3)) for _ in range(40)]
        self.particles = []
        self.shake = 0
        self.paused = False
        self.pause_btn = Button(SCREEN_W//2-80, SCREEN_H//2-30, 160, 50, "RESUME", GREEN)
        self.quit_btn  = Button(SCREEN_W//2-80, SCREEN_H//2+40, 160, 50, "QUIT", RED)

    def reset_level(self):
        ld = self.LEVEL_DATA[min(self.level, len(self.LEVEL_DATA)-1)]
        self.is_boss = ld["boss"]
        self.ammo = ld["ammo"]
        self.max_ammo = ld["ammo"]
        self.time_left = ld["time"] * FPS
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
                if self.is_boss and self.boss and self.boss.alive:
                    if self.boss.get_rect().collidepoint(mx, my):
                        self.boss.hit_duck()
                        hit_any = True
                        self.particles += [Particle(mx, my, GOLD) for _ in range(12)]
                        if not self.boss.alive:
                            self.ducks_hit += 1
                            snd_coin.play()
                else:
                    for d in self.ducks:
                        if d.alive and not d.hit and d.get_rect().collidepoint(mx, my):
                            d.hit = True
                            self.ducks_hit += 1
                            snd_hit.play()
                            self.particles += [Particle(mx, my, GOLD) for _ in range(8)]
                            hit_any = True
                            break
                if not hit_any:
                    self.shake = 6

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.pause_btn.update(mx, my)
        self.quit_btn.update(mx, my)
        if self.paused or self.result is not None: return
        self.time_left -= 1
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        if self.shake > 0: self.shake -= 1

        if self.is_boss:
            if self.boss and self.boss.alive:
                self.boss.update()
            elif self.boss and not self.boss.alive:
                self._finish("boss_win")
        else:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval and self.spawned < self.total_ducks:
                self.ducks.append(Duck(self.level))
                self.spawned += 1
                self.spawn_timer = 0
                self.spawn_interval = max(40, 90 - self.level*10)
            for d in self.ducks:
                d.update()
                if not d.hit and d.is_offscreen():
                    self.ducks_missed += 1
                    d.alive = False
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
        self.earned_coins = coins
        snd_coin.play()
        SaveSystem.save(self.game.coins, self.game.selected_char)

    def draw(self, surface):
        ox = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        oy = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        # Background
        for i in range(SCREEN_H):
            ratio = i / SCREEN_H
            r = int(100 + ratio*40); g = int(160+ratio*60); b = int(80+ratio*30)
            pygame.draw.line(surface, (r,g,b), (0, i+oy), (SCREEN_W, i+oy))
        # Ground
        pygame.draw.rect(surface, (60,140,40), (0, SCREEN_H-80+oy, SCREEN_W, 80))
        pygame.draw.rect(surface, (50,110,30), (0, SCREEN_H-80+oy, SCREEN_W, 12))
        # Clouds
        for cx2, cy2 in [(200,120),(500,90),(800,140)]:
            pygame.draw.ellipse(surface, (240,240,255), (cx2+ox, cy2+oy, 100, 40))
            pygame.draw.ellipse(surface, (240,240,255), (cx2+30+ox, cy2-20+oy, 80, 40))
        # Ducks
        for d in self.ducks: d.draw(surface)
        if self.boss: self.boss.draw(surface)
        # Particles
        for p in self.particles: p.draw(surface)
        # Crosshair
        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(surface, RED, (mx-20, my), (mx+20, my), 2)
        pygame.draw.line(surface, RED, (mx, my-20), (mx, my+20), 2)
        pygame.draw.circle(surface, RED, (mx, my), 10, 2)
        pygame.draw.circle(surface, WHITE, (mx, my), 4, 1)
        # HUD
        draw_hud(surface, self.game.coins, self.level+1,
                 f"AMMO:{self.ammo}/{self.max_ammo}  TIME:{self.time_left//FPS}")
        # Ammo bar
        for i in range(self.max_ammo):
            bx = 20 + i*22
            bc = YELLOW if i < self.ammo else GRAY
            pygame.draw.rect(surface, bc, (bx, 52, 16, 8))
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

# ---------------------------------------------------------
#  MARIO PLATFORMER
# ---------------------------------------------------------
class Platform:
    def __init__(self, x, y, w, h=16, color=(120,80,40)):
        self.rect  = pygame.Rect(x, y, w, h)
        self.color = color
        self.top_color = tuple(min(255,c+40) for c in color)

    def draw(self, surface, offset_x=0):
        r = self.rect.move(-offset_x, 0)
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, self.top_color, (r.x, r.y, r.w, 6))
        pygame.draw.rect(surface, (60,40,20), r, 2)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vx = -2; self.vy = 0
        self.alive = True; self.stomped = False
        self.stomp_timer = 0; self.anim = 0

    def update(self, platforms, offset_x):
        if self.stomped:
            self.stomp_timer += 1
            if self.stomp_timer > 40: self.alive = False
            return
        self.anim += 1
        self.vy = min(self.vy + 0.5, 12)
        self.rect.x += self.vx
        self.rect.y += int(self.vy)
        on_ground = False
        for plat in platforms:
            pr = plat.rect
            er = self.rect
            if er.colliderect(pr):
                if self.vy > 0 and er.bottom <= pr.bottom + 10:
                    er.bottom = pr.top
                    self.vy = 0; on_ground = True
                elif er.right >= pr.left and er.left < pr.left:
                    self.vx = abs(self.vx); er.right = pr.left
                elif er.left <= pr.right and er.right > pr.right:
                    self.vx = -abs(self.vx); er.left = pr.right
        if not on_ground:
            pass

    def draw(self, surface, offset_x):
        if not self.alive: return
        r = self.rect.move(-offset_x, 0)
        if self.stomped:
            pygame.draw.rect(surface, (140,80,20), (r.x, r.y+20, 32, 12))
            return
        body_y = r.y + int(math.sin(self.anim*0.2)*2)
        pygame.draw.rect(surface, (140,80,20), (r.x+4, r.y+10, 24, 22))
        pygame.draw.circle(surface, (140,80,20), (r.x+16, r.y+16), 16)
        pygame.draw.circle(surface, BLACK, (r.x+10, r.y+12), 4)
        pygame.draw.circle(surface, BLACK, (r.x+22, r.y+12), 4)
        pygame.draw.circle(surface, WHITE, (r.x+11, r.y+11), 2)
        pygame.draw.circle(surface, WHITE, (r.x+23, r.y+11), 2)
        leg_off = int(math.sin(self.anim*0.2)*4)
        pygame.draw.rect(surface, (100,60,10), (r.x+4, r.y+30, 10, 8+leg_off))
        pygame.draw.rect(surface, (100,60,10), (r.x+18, r.y+30, 10, 8-leg_off))

class BossMonster:
    def __init__(self):
        self.rect = pygame.Rect(700, 400, 72, 72)
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
        if self.rect.left < 200: self.vx = abs(self.vx)
        if self.rect.right > 2000: self.vx = -abs(self.vx)
        self.shoot_timer += 1
        if self.shoot_timer > 90:
            self.shoot_timer = 0
            self.projectiles.append({"x": float(self.rect.centerx), "y": float(self.rect.centery),
                                     "vx": self.vx*2, "vy": -4})
        for proj in self.projectiles:
            proj["x"] += proj["vx"]; proj["y"] += proj["vy"]; proj["vy"] += 0.3
        self.projectiles = [p for p in self.projectiles if 0 < p["x"] < 3000 and p["y"] < SCREEN_H]

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

class Player:
    def __init__(self, char_data):
        self.char = char_data
        self.rect = pygame.Rect(100, 400, 28, 48)
        self.vx = 0; self.vy = 0
        self.on_ground = False
        self.facing = 1
        self.anim = 0
        self.dead = False
        self.invincible = 0

    def reset(self, x=100, y=400):
        self.rect.x = x; self.rect.y = y
        self.vx = 0; self.vy = 0
        self.on_ground = False; self.dead = False
        self.invincible = 120

    def handle_input(self, keys):
        if self.dead: return
        speed = 4
        self.vx = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx = -speed; self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx =  speed; self.facing =  1
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = -14; self.on_ground = False; snd_jump.play()

    def update(self, platforms):
        if self.dead: return
        self.anim += 1
        if self.invincible > 0: self.invincible -= 1
        self.vy = min(self.vy + 0.6, 16)
        self.rect.x += int(self.vx)
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vx > 0: self.rect.right = plat.rect.left
                if self.vx < 0: self.rect.left  = plat.rect.right
        self.rect.y += int(self.vy)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vy > 0:
                    self.rect.bottom = plat.rect.top
                    self.vy = 0; self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = plat.rect.bottom; self.vy = 0

    def draw(self, surface, offset_x):
        if self.invincible > 0 and (self.anim // 4) % 2 == 0: return
        rx = self.rect.x - offset_x; ry = self.rect.y
        draw_character_sprite(surface, self.char, rx+14, ry+20, 0.65, self.anim)

class MarioPlatformerGame:
    LEVELS = [
        {"platforms":[(0,580,3000,60),(200,460,200),(500,380,160),(800,460,200),(1100,380,200),
                       (1400,460,160),(1700,380,200),(2000,460,200),(2400,420,240)],
         "enemies":[],"flag_x":2700,"boss":False},
        {"platforms":[(0,580,3000,60),(150,460,180),(400,380,160),(650,460,140),(900,380,200),
                       (1150,460,160),(1400,380,200),(1650,460,180),(1900,380,160),(2200,460,200),(2600,420,200)],
         "enemies":[(500,380-32),(900,380-32),(1400,380-32)],
         "flag_x":2800,"boss":False},
        {"platforms":[(0,580,3000,60),(100,460,140),(320,380,120),(540,460,100),(760,380,140),
                       (980,460,120),(1200,380,100),(1420,460,140),(1640,380,120),(1860,460,100),
                       (2080,380,140),(2300,420,200),(2600,380,180)],
         "enemies":[(320,380-32),(760,380-32),(1200,380-32),(1640,380-32),(2300,420-32)],
         "flag_x":2850,"boss":False},
        {"platforms":[(0,580,3000,60),(200,460,300),(600,380,200),(1000,460,200),(1400,380,200),
                       (1800,460,200),(2200,380,200)],
         "enemies":[],"flag_x":None,"boss":True},
    ]

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
        self.load_level()

    def load_level(self):
        ld = self.LEVELS[min(self.level_idx, len(self.LEVELS)-1)]
        self.platforms = []
        for pd in ld["platforms"]:
            if len(pd) == 3:
                self.platforms.append(Platform(pd[0], pd[1], pd[2]))
            else:
                self.platforms.append(Platform(pd[0], pd[1], pd[2], pd[3]))
        self.enemies = [Enemy(ex, ey) for ex, ey in ld.get("enemies", [])]
        self.flag_x  = ld.get("flag_x")
        self.is_boss = ld.get("boss", False)
        self.boss    = BossMonster() if self.is_boss else None
        self.player  = Player(CHARACTERS[self.game.selected_char])
        self.offset_x= 0
        self.result  = None
        self.result_timer = 0
        self.stomp_tracker = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
        if self.paused:
            if self.pause_btn.is_clicked(event): self.paused = False
            if self.quit_btn.is_clicked(event):  self.game.state = "menu"

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.pause_btn.update(mx, my)
        self.quit_btn.update(mx, my)
        if self.paused or self.result is not None: return
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(self.platforms)
        self.offset_x = max(0, self.player.rect.centerx - SCREEN_W//3)
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        if self.shake > 0: self.shake -= 1
        # Enemy update & collision
        for e in self.enemies:
            e.update(self.platforms, self.offset_x)
            if e.alive and not e.stomped and self.player.invincible == 0:
                if self.player.rect.colliderect(e.rect):
                    if self.player.vy > 0 and self.player.rect.bottom < e.rect.centery + 10:
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
                if self.player.vy > 0 and pr.bottom < self.boss.rect.centery + 12:
                    self.boss.stomp(); self.player.vy = -10
                    self.stomp_tracker += 1
                    self.particles += [Particle(self.boss.rect.centerx, self.boss.rect.y, RED) for _ in range(10)]
                else:
                    self._player_hurt()
            for proj in self.boss.projectiles:
                pr2 = pygame.Rect(proj["x"]-8, proj["y"]-8, 16, 16)
                if pr.colliderect(pr2) and self.player.invincible == 0:
                    self._player_hurt()
            if not self.boss.alive:
                won_clean = self.deaths == 0
                coins = 150 if won_clean else 50
                self.game.coins += coins; self.earned_coins = coins
                snd_coin.play()
                SaveSystem.save(self.game.coins, self.game.selected_char)
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
        self.lives -= 1; self.deaths += 1
        self.shake = 12; snd_die.play()
        self.particles += [Particle(self.player.rect.centerx, self.player.rect.centery, RED) for _ in range(15)]
        if self.lives <= 0:
            self.game.coins += 10; self.earned_coins = 10
            snd_coin.play()
            SaveSystem.save(self.game.coins, self.game.selected_char)
            self.result = "gameover"; self.result_timer = 200
        else:
            self.player.reset()

    def _finish_level(self):
        if self.deaths == 0:
            coins = 100
        elif self.deaths <= 2:
            coins = 50
        else:
            coins = 20
        self.game.coins += coins; self.earned_coins = coins
        snd_coin.play()
        SaveSystem.save(self.game.coins, self.game.selected_char)
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
        # Flag
        if self.flag_x:
            fx = self.flag_x - self.offset_x
            pygame.draw.rect(surface, (180,140,80), (fx-4, 300, 8, 280))
            pygame.draw.polygon(surface, RED, [(fx, 300),(fx+50, 320),(fx, 340)])
        # Enemies
        for e in self.enemies: e.draw(surface, self.offset_x)
        # Boss
        if self.boss: self.boss.draw(surface, self.offset_x)
        # Player
        self.player.draw(surface, self.offset_x)
        # Particles
        for p in self.particles: p.draw(surface)
        # HUD
        draw_hud(surface, self.game.coins, self.level_idx+1, f"LIVES: {'?'*self.lives}")
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
                        self.lives = 3; self.deaths = 0; self.load_level()
                    else:
                        self.level_idx = min(self.level_idx+1, len(self.LEVELS)-1)
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

# ---------------------------------------------------------
#  SHOP
# ---------------------------------------------------------
class Shop:
    def __init__(self, game_ref):
        self.game = game_ref
        self.scroll = 0
        self.back_btn = Button(20, 20, 120, 44, "< BACK", GRAY)
        self.msg = ""; self.msg_timer = 0

    def handle_event(self, event):
        if self.back_btn.is_clicked(event):
            self.game.state = "menu"; return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for idx, ch in enumerate(CHARACTERS):
                col = idx % 5; row = idx // 5
                cx = 40 + col*196; cy = 120 + row*300 - self.scroll
                btn_r = pygame.Rect(cx+18, cy+220, 160, 44)
                if btn_r.collidepoint(mx, my):
                    if ch["owned"]:
                        self.game.selected_char = ch["id"]
                        snd_select.play()
                        self.msg = f"Selected {ch['name']}!"
                        self.msg_timer = 120
                        SaveSystem.save(self.game.coins, self.game.selected_char)
                    else:
                        if self.game.coins >= ch["cost"]:
                            self.game.coins -= ch["cost"]
                            ch["owned"] = True
                            snd_buy.play()
                            self.msg = f"Bought {ch['name']}! -{ch['cost']} coins"
                            self.msg_timer = 150
                            SaveSystem.save(self.game.coins, self.game.selected_char)
                        else:
                            snd_die.play()
                            self.msg = f"Need {ch['cost']-self.game.coins} more coins!"
                            self.msg_timer = 120
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y*30)

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.back_btn.update(mx, my)
        if self.msg_timer > 0: self.msg_timer -= 1

    def draw(self, surface):
        surface.fill(DARKER)
        # Header gradient
        for i in range(80):
            ratio = i/80
            r = int(20+ratio*30); g = int(20+ratio*20); b = int(40+ratio*60)
            pygame.draw.line(surface, (r,g,b), (0,i), (SCREEN_W,i))
        title = font_lg.render("?  CHARACTER SHOP  ?", True, GOLD)
        surface.blit(title, title.get_rect(center=(SCREEN_W//2, 40)))
        pygame.draw.line(surface, GOLD, (0,80), (SCREEN_W,80), 2)
        coins_txt = font_sm.render(f"Your Coins: {self.game.coins}", True, GOLD)
        surface.blit(coins_txt, (SCREEN_W-200, 90))
        # Characters grid
        clip = pygame.Surface((SCREEN_W, SCREEN_H-100))
        clip.fill(DARKER)
        for idx, ch in enumerate(CHARACTERS):
            col = idx % 5; row = idx // 5
            cx = 40 + col*196; cy = 20 + row*300 - self.scroll
            if cy < -280 or cy > SCREEN_H: continue
            # Card
            card_r = pygame.Rect(cx, cy, 192, 280)
            is_sel  = self.game.selected_char == ch["id"]
            border_c = GOLD if is_sel else (ch["color"][0]//2+40, ch["color"][1]//2+40, ch["color"][2]//2+40)
            pygame.draw.rect(clip, (25,25,45), card_r, border_radius=10)
            pygame.draw.rect(clip, border_c, card_r, 3, border_radius=10)
            # Sprite preview
            draw_character_sprite(clip, ch, cx+96, cy+90, 1.4, pygame.time.get_ticks()//20)
            # Name/gender
            name_t = font_sm.render(ch["name"], True, ch["accent"])
            clip.blit(name_t, name_t.get_rect(center=(cx+96, cy+160)))
            gen_t = font_xs.render(ch["gender"], True, GRAY)
            clip.blit(gen_t, gen_t.get_rect(center=(cx+96, cy+178)))
            # Lock / own indicator
            if not ch["owned"]:
                price_t = font_xs.render(f"?? {ch['cost']} coins", True, YELLOW)
                clip.blit(price_t, price_t.get_rect(center=(cx+96, cy+196)))
            else:
                own_t = font_xs.render("? OWNED", True, GREEN)
                clip.blit(own_t, own_t.get_rect(center=(cx+96, cy+196)))
            # Button
            if is_sel:
                btn_c = GOLD; btn_txt = "SELECTED"
            elif ch["owned"]:
                btn_c = GREEN; btn_txt = "SELECT"
            else:
                btn_c = PURPLE; btn_txt = "BUY"
            pygame.draw.rect(clip, btn_c, (cx+18, cy+212, 156, 40), border_radius=6)
            pygame.draw.rect(clip, WHITE, (cx+18, cy+212, 156, 40), 2, border_radius=6)
            bt = font_xs.render(btn_txt, True, BLACK if btn_c == GOLD else WHITE)
            clip.blit(bt, bt.get_rect(center=(cx+96, cy+232)))
        surface.blit(clip, (0, 100))
        # Message banner
        if self.msg_timer > 0:
            alpha = min(255, self.msg_timer*4)
            ms = font_md.render(self.msg, True, GOLD)
            sr = ms.get_rect(center=(SCREEN_W//2, SCREEN_H-50))
            pygame.draw.rect(surface, (0,0,0), sr.inflate(20,12), border_radius=8)
            surface.blit(ms, sr)
        self.back_btn.draw(surface)

# ---------------------------------------------------------
#  MAIN MENU
# ---------------------------------------------------------
class MainMenu:
    def __init__(self, game_ref):
        self.game = game_ref
        self.t = 0
        self.stars = [(random.randint(0,SCREEN_W), random.randint(0,SCREEN_H),
                       random.randint(1,3)) for _ in range(120)]
        bx = SCREEN_W//2 - 150
        self.btn_duck  = Button(bx, 340, 300, 56, "?? DUCK HUNT",   (60,140,60))
        self.btn_mario = Button(bx, 410, 300, 56, "?? MARIO RUN",   (180,60,30))
        self.btn_shop  = Button(bx, 480, 300, 56, "? SHOP",         PURPLE)
        self.btn_quit  = Button(bx, 550, 300, 56, "? QUIT",         (100,30,30))
        self.particles = []
        self.sparkle_timer = 0

    def handle_event(self, event):
        if self.btn_duck.is_clicked(event):
            self.game.state = "duck"
            self.game.duck_game = DuckHuntGame(self.game)
        if self.btn_mario.is_clicked(event):
            self.game.state = "mario"
            self.game.mario_game = MarioPlatformerGame(self.game)
        if self.btn_shop.is_clicked(event):
            self.game.state = "shop"
        if self.btn_quit.is_clicked(event):
            pygame.quit(); sys.exit()

    def update(self):
        self.t += 1
        mx, my = pygame.mouse.get_pos()
        for b in [self.btn_duck, self.btn_mario, self.btn_shop, self.btn_quit]:
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
        # Title wobble
        title_y = 80 + int(math.sin(self.t * 0.04) * 8)
        title_scale = 1.0 + math.sin(self.t * 0.06) * 0.04
        title1 = font_lg.render("PIXEL", True, GOLD)
        title2 = font_lg.render("GAME HUB", True, CYAN)
        shadow1 = font_lg.render("PIXEL", True, (80,60,0))
        shadow2 = font_lg.render("GAME HUB", True, (0,80,80))
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
        for b in [self.btn_duck, self.btn_mario, self.btn_shop, self.btn_quit]:
            b.draw(surface)
        # Coin display
        coin_surf = pygame.Surface((220, 44), pygame.SRCALPHA)
        coin_surf.fill((0,0,0,140))
        surface.blit(coin_surf, (SCREEN_W//2-110, 8))
        ct = font_sm.render(f"? {self.game.coins} COINS", True, GOLD)
        surface.blit(ct, ct.get_rect(center=(SCREEN_W//2, 30)))
        # Version
        vt = font_xs.render("v1.0  |  ESC = Pause in game", True, GRAY)
        surface.blit(vt, vt.get_rect(center=(SCREEN_W//2, SCREEN_H-16)))

# ---------------------------------------------------------
#  MAIN GAME
# ---------------------------------------------------------
class Game:
    def __init__(self):
        self.coins, self.selected_char = SaveSystem.load()
        self.state = "menu"
        self.menu = MainMenu(self)
        self.shop = Shop(self)
        self.duck_game  = None
        self.mario_game = None

    def run(self):
        pygame.mouse.set_visible(False)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    SaveSystem.save(self.coins, self.selected_char)
                    pygame.quit(); sys.exit()
                if self.state == "menu":
                    self.menu.handle_event(event)
                elif self.state == "shop":
                    self.shop.handle_event(event)
                elif self.state == "duck" and self.duck_game:
                    self.duck_game.handle_event(event)
                elif self.state == "mario" and self.mario_game:
                    self.mario_game.handle_event(event)

            if self.state == "menu":
                self.menu.update(); self.menu.draw(screen)
            elif self.state == "shop":
                self.shop.update(); self.shop.draw(screen)
            elif self.state == "duck" and self.duck_game:
                self.duck_game.update(); self.duck_game.draw(screen)
            elif self.state == "mario" and self.mario_game:
                self.mario_game.update(); self.mario_game.draw(screen)

            # Custom cursor (always on top)
            if self.state not in ["duck"]:
                mx, my = pygame.mouse.get_pos()
                pygame.draw.circle(screen, WHITE, (mx, my), 6, 2)
                pygame.draw.line(screen, WHITE, (mx-10, my), (mx-4, my), 2)
                pygame.draw.line(screen, WHITE, (mx+4,  my), (mx+10, my), 2)
                pygame.draw.line(screen, WHITE, (mx, my-10), (mx, my-4), 2)
                pygame.draw.line(screen, WHITE, (mx, my+4),  (mx, my+10), 2)

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
