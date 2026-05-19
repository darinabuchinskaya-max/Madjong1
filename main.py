import pygame
import sys

from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    PANEL_HEIGHT,
    COLOR_BG_TOP, COLOR_BG_MID, COLOR_BG_BOT,
    COLOR_PANEL_BG, COLOR_PANEL_LINE,
    COLOR_TITLE, COLOR_STATUS, COLOR_COUNTER,
    COLOR_WIN, COLOR_LOSE,
    COLOR_BTN_NEW_BG, COLOR_BTN_NEW_HOVER, COLOR_BTN_NEW_BORDER,
    COLOR_BTN_SHUF_BG, COLOR_BTN_SHUF_HOVER, COLOR_BTN_SHUF_BORDER,
    COLOR_BTN_HINT_BG, COLOR_BTN_HINT_HOVER, COLOR_BTN_HINT_BORDER,
)
from board import Board
from button import Button


def build_bg(width, height):
    surf = pygame.Surface((width, height))
    half = height // 2
    for y in range(half):
        t = y / half
        r = int(COLOR_BG_TOP[0] + (COLOR_BG_MID[0] - COLOR_BG_TOP[0]) * t)
        g = int(COLOR_BG_TOP[1] + (COLOR_BG_MID[1] - COLOR_BG_TOP[1]) * t)
        b = int(COLOR_BG_TOP[2] + (COLOR_BG_MID[2] - COLOR_BG_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    for y in range(half, height):
        t = (y - half) / (height - half)
        r = int(COLOR_BG_MID[0] + (COLOR_BG_BOT[0] - COLOR_BG_MID[0]) * t)
        g = int(COLOR_BG_MID[1] + (COLOR_BG_BOT[1] - COLOR_BG_MID[1]) * t)
        b = int(COLOR_BG_MID[2] + (COLOR_BG_BOT[2] - COLOR_BG_MID[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    return surf


def draw_panel(surface, board, buttons, mouse_pos, font_title, font_status, font_counter):
    pygame.draw.rect(surface, COLOR_PANEL_BG, (0, 0, WINDOW_WIDTH, PANEL_HEIGHT))

    for i in range(PANEL_HEIGHT):
        alpha_ratio = 1 - i / PANEL_HEIGHT
        overlay_r = int(COLOR_PANEL_LINE[0] * alpha_ratio * 0.08)
        overlay_g = int(COLOR_PANEL_LINE[1] * alpha_ratio * 0.08)
        overlay_b = int(COLOR_PANEL_LINE[2] * alpha_ratio * 0.08)
        pygame.draw.line(surface, (overlay_r, overlay_g, overlay_b), (0, i), (WINDOW_WIDTH, i))

    pygame.draw.line(surface, COLOR_PANEL_LINE,
                     (0, PANEL_HEIGHT - 1), (WINDOW_WIDTH, PANEL_HEIGHT - 1), 2)

    title_surf = font_title.render("МАДЖОНГ  ФРУКТЫ", True, COLOR_TITLE)
    surface.blit(title_surf, (28, 14))

    counter_text = f"Плиток: {board.remaining_count()}"
    counter_surf = font_counter.render(counter_text, True, COLOR_COUNTER)
    surface.blit(counter_surf, (28, 58))

    status = board.status
    if "ПОБЕДА" in status:
        sc = COLOR_WIN
    elif any(w in status.lower() for w in ("нет", "заблокир")):
        sc = COLOR_LOSE
    else:
        sc = COLOR_STATUS

    status_surf = font_status.render(status, True, sc)
    sx = 220
    sy = PANEL_HEIGHT // 2 - status_surf.get_height() // 2
    surface.blit(status_surf, (sx, sy))

    for btn in buttons:
        btn.draw(surface, mouse_pos)


def draw_win_overlay(surface, font_big, font_sub):
    ov = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    ov.fill((15, 5, 35, 200))
    surface.blit(ov, (0, 0))

    msg = font_big.render("ПОБЕДА!", True, (100, 255, 160))
    sub = font_sub.render("Все плитки убраны  —  нажми «Новая игра»", True, (200, 230, 255))
    surface.blit(msg, msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 32)))
    surface.blit(sub, sub.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 32)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Маджонг — Фруктовый Солитёр")
    clock = pygame.time.Clock()

    font_title   = pygame.font.SysFont("segoeui,dejavusans,arial", 24, bold=True)
    font_status  = pygame.font.SysFont("segoeui,dejavusans,arial", 15)
    font_counter = pygame.font.SysFont("segoeui,dejavusans,arial", 14)
    font_big     = pygame.font.SysFont("segoeui,dejavusans,arial", 72, bold=True)
    font_sub     = pygame.font.SysFont("segoeui,dejavusans,arial", 22)

    btn_w   = 130
    btn_h   = 44
    btn_gap = 10
    btn_y   = (PANEL_HEIGHT - btn_h) // 2

    btn_right = WINDOW_WIDTH - 18
    btn_hint    = Button(btn_right - btn_w,               btn_y, btn_w, btn_h,
                         "Подсказка",
                         COLOR_BTN_HINT_BG, COLOR_BTN_HINT_HOVER, COLOR_BTN_HINT_BORDER)
    btn_shuffle = Button(btn_right - btn_w * 2 - btn_gap, btn_y, btn_w, btn_h,
                         "Перемешать",
                         COLOR_BTN_SHUF_BG, COLOR_BTN_SHUF_HOVER, COLOR_BTN_SHUF_BORDER)
    btn_new     = Button(btn_right - btn_w * 3 - btn_gap * 2, btn_y, btn_w, btn_h,
                         "Новая игра",
                         COLOR_BTN_NEW_BG, COLOR_BTN_NEW_HOVER, COLOR_BTN_NEW_BORDER)

    buttons = [btn_new, btn_shuffle, btn_hint]

    board = Board()
    hint_tiles  = []
    hint_timer  = 0

    bg = build_bg(WINDOW_WIDTH, WINDOW_HEIGHT)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if btn_new.is_clicked(mouse_pos, event):
                board.new_game()
                hint_tiles = []
                hint_timer = 0

            elif btn_shuffle.is_clicked(mouse_pos, event):
                board.shuffle_remaining()
                hint_tiles = []
                hint_timer = 0

            elif btn_hint.is_clicked(mouse_pos, event):
                t1, t2 = board.get_hint()
                if t1 and t2:
                    hint_tiles = [t1, t2]
                    hint_timer = FPS * 3
                    board.status = f"Подсказка: {t1.fruit} + {t2.fruit}"
                else:
                    board.status = "Нет доступных ходов"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not any(b.rect.collidepoint(mouse_pos) for b in buttons):
                    board.handle_click(mouse_pos)
                    hint_tiles = []
                    hint_timer = 0

        if hint_timer > 0:
            hint_timer -= 1
        else:
            hint_tiles = []

        screen.blit(bg, (0, 0))
        board.draw(screen, mouse_pos)

        for t in hint_tiles:
            if not t.is_removed:
                pulse = abs(pygame.time.get_ticks() % 700 - 350) / 350
                gc = (int(100 + 155 * pulse), int(255 * pulse), int(200 * pulse))
                pygame.draw.rect(screen, gc, t.rect.inflate(8, 8), width=3, border_radius=15)

        draw_panel(screen, board, buttons, mouse_pos, font_title, font_status, font_counter)

        if board.game_over and board.remaining_count() == 0:
            draw_win_overlay(screen, font_big, font_sub)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
