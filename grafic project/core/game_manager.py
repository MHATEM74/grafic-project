# core/game_manager.py
import pygame
import sys
from core.constants import SCREEN_W, SCREEN_H, FPS, WHITE
from core.save_system import SaveSystem

# We will import screens lazily or set them up here to avoid circular imports.
class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        
        save_data = SaveSystem.load()
        self.coins = save_data["coins"]
        self.selected_char = save_data["selected_char"]
        self.achievements = save_data["achievements"]
        self.stats = save_data["stats"]
        self.daily_streak = save_data["daily_streak"]
        self.last_login = save_data["last_login"]
        
        self.state = "menu"
        
        from screens.main_menu import MainMenu
        from screens.shop import Shop
        
        self.menu = MainMenu(self)
        self.shop = Shop(self)
        self.duck_game  = None
        self.mario_game = None
        self.space_game = None
        self.street_game = None

    def run(self):
        pygame.mouse.set_visible(False)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    SaveSystem.save(self)
                    pygame.quit()
                    sys.exit()
                if self.state == "menu":
                    self.menu.handle_event(event)
                elif self.state == "shop":
                    self.shop.handle_event(event)
                elif self.state == "duck" and self.duck_game:
                    self.duck_game.handle_event(event)
                elif self.state == "mario" and self.mario_game:
                    self.mario_game.handle_event(event)
                elif self.state == "space" and self.space_game:
                    self.space_game.handle_event(event)
                elif self.state == "street" and self.street_game:
                    self.street_game.handle_event(event)

            if self.state == "menu":
                self.menu.update(); self.menu.draw(self.screen)
            elif self.state == "shop":
                self.shop.update(); self.shop.draw(self.screen)
            elif self.state == "duck" and self.duck_game:
                self.duck_game.update(); self.duck_game.draw(self.screen)
            elif self.state == "mario" and self.mario_game:
                self.mario_game.update(); self.mario_game.draw(self.screen)
            elif self.state == "space" and self.space_game:
                self.space_game.update(); self.space_game.draw(self.screen)
            elif self.state == "street" and self.street_game:
                self.street_game.update(); self.street_game.draw(self.screen)

            # Custom cursor (always on top)
            if self.state not in ["duck"]:
                mx, my = pygame.mouse.get_pos()
                pygame.draw.circle(self.screen, WHITE, (mx, my), 6, 2)
                pygame.draw.line(self.screen, WHITE, (mx-10, my), (mx-4, my), 2)
                pygame.draw.line(self.screen, WHITE, (mx+4,  my), (mx+10, my), 2)
                pygame.draw.line(self.screen, WHITE, (mx, my-10), (mx, my-4), 2)
                pygame.draw.line(self.screen, WHITE, (mx, my+4),  (mx, my+10), 2)

            pygame.display.flip()
            self.clock.tick(FPS)
