# screens/shop.py
import pygame
from core.constants import SCREEN_W, SCREEN_H, DARKER, GOLD, GRAY, WHITE, GREEN, PURPLE, BLACK, YELLOW
from core.assets import font_lg, font_md, font_sm, font_xs, snd_select, snd_buy, snd_die
from ui.button import Button
from characters.renderer import draw_character_sprite
from characters.character_data import CHARACTERS, RARITY

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
                        from core.save_system import SaveSystem
                        SaveSystem.save(self.game)
                    else:
                        if self.game.coins >= ch["cost"]:
                            self.game.coins -= ch["cost"]
                            ch["owned"] = True
                            snd_buy.play()
                            self.msg = f"Bought {ch['name']}! -{ch['cost']} coins"
                            self.msg_timer = 150
                            from core.save_system import SaveSystem
                            SaveSystem.save(self.game)
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
        title = font_lg.render("★  CHARACTER SHOP  ★", True, GOLD)
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
            rarity_color = RARITY.get(ch.get("rarity", "Common"), WHITE)
            border_c = GOLD if is_sel else rarity_color
            
            pygame.draw.rect(clip, (25,25,45), card_r, border_radius=10)
            pygame.draw.rect(clip, border_c, card_r, 3, border_radius=10)
            
            # Sprite preview
            draw_character_sprite(clip, ch, cx+96, cy+90, 1.4, pygame.time.get_ticks()//20)
            
            # Name/gender/rarity
            name_t = font_sm.render(ch["name"], True, ch["accent"])
            clip.blit(name_t, name_t.get_rect(center=(cx+96, cy+150)))
            
            gen_t = font_xs.render(f"{ch['gender']} | {ch.get('rarity','Common')}", True, rarity_color)
            clip.blit(gen_t, gen_t.get_rect(center=(cx+96, cy+170)))
            
            # Lock / own indicator
            if not ch["owned"]:
                price_t = font_xs.render(f"🔒 {ch['cost']} coins", True, YELLOW)
                clip.blit(price_t, price_t.get_rect(center=(cx+96, cy+196)))
            else:
                own_t = font_xs.render("✓ OWNED", True, GREEN)
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
