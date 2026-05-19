import pygame
from constants import (
    TILE_WIDTH, TILE_HEIGHT,
    COLOR_TILE_BG, COLOR_TILE_SIDE, COLOR_TILE_BORDER,
    COLOR_TILE_HOVER_BG, COLOR_TILE_HOVER_BORDER,
    COLOR_TILE_SELECTED_BG, COLOR_TILE_SELECTED_SIDE, COLOR_TILE_SELECTED_BORDER,
    COLOR_GLOW_FREE,
    FRUIT_LABELS,
)
from fruit_draw import draw_fruit

SIDE_H = 6


class Tile:
    def __init__(self, value, fruit, row, col, x, y):
        self.value = value
        self.fruit = fruit
        self.row = row
        self.col = col
        self.rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        self.is_removed = False
        self.is_selected = False
        self._font = None

    def _get_font(self):
        if self._font is None:
            self._font = pygame.font.SysFont("segoeui,dejavusans,arial", 11, bold=True)
        return self._font

    def draw(self, surface, mouse_pos, is_free):
        if self.is_removed:
            return

        hovered = self.rect.collidepoint(mouse_pos) and is_free and not self.is_selected

        if self.is_selected:
            face_col   = COLOR_TILE_SELECTED_BG
            side_col   = COLOR_TILE_SELECTED_SIDE
            border_col = COLOR_TILE_SELECTED_BORDER
        elif hovered:
            face_col   = COLOR_TILE_HOVER_BG
            side_col   = COLOR_TILE_SIDE
            border_col = COLOR_TILE_HOVER_BORDER
        else:
            face_col   = COLOR_TILE_BG
            side_col   = COLOR_TILE_SIDE
            border_col = COLOR_TILE_BORDER

        shadow_surf = pygame.Surface((TILE_WIDTH + 6, TILE_HEIGHT + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 90),
                         (0, 0, TILE_WIDTH + 6, TILE_HEIGHT + 6), border_radius=12)
        surface.blit(shadow_surf, (self.rect.x + 5, self.rect.y + 6))

        side_rect = pygame.Rect(self.rect.x, self.rect.y + SIDE_H, TILE_WIDTH, TILE_HEIGHT)
        pygame.draw.rect(surface, side_col, side_rect, border_radius=12)

        pygame.draw.rect(surface, face_col, self.rect, border_radius=12)
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=12)

        if is_free and not self.is_selected:
            glow = self.rect.inflate(5, 5)
            pygame.draw.rect(surface, COLOR_GLOW_FREE, glow, width=2, border_radius=14)

        fruit_size = int(TILE_HEIGHT * 0.46)
        draw_fruit(surface, self.fruit,
                   self.rect.centerx,
                   self.rect.y + int(TILE_HEIGHT * 0.42),
                   fruit_size)

        label = FRUIT_LABELS.get(self.fruit, self.fruit)
        font = self._get_font()
        label_surf = font.render(label, True, (80, 40, 120))
        label_rect = label_surf.get_rect(centerx=self.rect.centerx,
                                         bottom=self.rect.bottom - 5)
        surface.blit(label_surf, label_rect)

    def is_clicked(self, mouse_pos):
        if self.is_removed:
            return False
        return self.rect.collidepoint(mouse_pos)

    def set_selected(self, state):
        self.is_selected = state
