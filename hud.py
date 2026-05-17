# ui/hud.py
import pygame
from core.constants import SCREEN_W, GOLD, CYAN, WHITE, DARKER
from core.assets import font_sm

def draw_hud(surface, coins, level, extra=""):
    pygame.draw.rect(surface, (0,0,0,180), (0, 0, SCREEN_W, 44))
    pygame.draw.rect(surface, GOLD, (0, 44, SCREEN_W, 2))
    coin_txt = font_sm.render(f"COINS: {coins}", True, GOLD)
    lvl_txt  = font_sm.render(f"LEVEL: {level}", True, CYAN)
    ext_txt  = font_sm.render(extra, True, WHITE)
    surface.blit(coin_txt, (12, 10))
    surface.blit(lvl_txt,  (SCREEN_W//2 - lvl_txt.get_width()//2, 10))
    surface.blit(ext_txt,  (SCREEN_W - ext_txt.get_width() - 12, 10))

def draw_stars_bg(surface, stars, scroll=0):
    surface.fill(DARKER)
    for sx, sy, sz in stars:
        bright = int(150 + sz * 35)
        c = (bright, bright, bright)
        pygame.draw.rect(surface, c, ((sx + scroll*sz*0.01) % SCREEN_W, sy, sz, sz))
