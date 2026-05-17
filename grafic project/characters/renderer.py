# characters/renderer.py
import pygame
import math
from core.constants import BLACK

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
    pygame.draw.rect(surface, c, (int(cx-10*s), int(body_y+14*s), int(8*s), int(18*s)))
    pygame.draw.rect(surface, c, (int(cx+2*s),  int(body_y+14*s), int(8*s), int(18*s)))
    # Shoes
    shoe_c = (30,30,30) if cid not in [7,4] else (180,180,200)
    pygame.draw.rect(surface, shoe_c, (int(cx-12*s), int(body_y+30*s), int(12*s), int(5*s)))
    pygame.draw.rect(surface, shoe_c, (int(cx+2*s),  int(body_y+30*s), int(12*s), int(5*s)))
    # Torso
    pygame.draw.rect(surface, c, (int(cx-13*s), int(body_y), int(26*s), int(18*s)))
    # Arms
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
