# main.py
import pygame
from core.constants import SCREEN_W, SCREEN_H
from core.game_manager import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Pixel Game Hub v3.0")
    clock = pygame.time.Clock()
    
    game = Game(screen, clock)
    game.run()

if __name__ == "__main__":
    main()
