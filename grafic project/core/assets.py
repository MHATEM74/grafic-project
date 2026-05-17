# core/assets.py
import pygame
import math

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

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
