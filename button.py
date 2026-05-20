import pygame
from constants import COLOR_BTN_TEXT, COLOR_BTN_SHADOW


class Button:
    def __init__(self, x, y, width, height, text, color_bg, color_hover, color_border):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color_bg = color_bg
        self.color_hover = color_hover
        self.color_border = color_border
        self._font = None

    def _get_font(self):
        if self._font is None:
            self._font = pygame.font.SysFont("segoeui,dejavusans,arial", 15, bold=True)
        return self._font

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        face = self.color_hover if hovered else self.color_bg

        shadow = self.rect.move(3, 4)
        pygame.draw.rect(surface, COLOR_BTN_SHADOW, shadow, border_radius=12)

        pygame.draw.rect(surface, face, self.rect, border_radius=12)
        pygame.draw.rect(surface, self.color_border, self.rect, width=2, border_radius=12)

        font = self._get_font()
        text_surf = font.render(self.text, True, COLOR_BTN_TEXT)
        tr = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, tr)

    def is_clicked(self, mouse_pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(mouse_pos)
        return False
