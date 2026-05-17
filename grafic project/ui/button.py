# ui/button.py
import pygame
from core.constants import WHITE, BLUE, BLACK
from core.assets import font_sm, snd_select

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
        
        # Glow effect
        if self.hovered:
            glow_surf = pygame.Surface((r.w + 20, r.h + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*shade, 100), glow_surf.get_rect(), border_radius=10)
            surface.blit(glow_surf, (r.x - 10, r.y - 10))

        # Shadow
        pygame.draw.rect(surface, (0,0,0), r.move(3,3), border_radius=6)
        # Main body
        pygame.draw.rect(surface, shade, r, border_radius=6)
        # Border
        pygame.draw.rect(surface, WHITE, r, 2, border_radius=6)
        
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=r.center))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                snd_select.play()
                return True
        return False
