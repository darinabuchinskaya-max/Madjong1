import random
import pygame
from tile import Tile
from constants import (
    COLS, ROWS,
    TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN,
    FRUITS,
    WINDOW_WIDTH, WINDOW_HEIGHT, PANEL_HEIGHT,
)


class Board:
    def __init__(self):
        self.tiles = []
        self.selected_tile = None
        self.status = ""
        self.game_over = False
        self._setup()

    def _origin(self):
        total_w = COLS * (TILE_WIDTH + TILE_MARGIN) - TILE_MARGIN
        total_h = ROWS * (TILE_HEIGHT + TILE_MARGIN) - TILE_MARGIN
        usable_h = WINDOW_HEIGHT - PANEL_HEIGHT
        ox = (WINDOW_WIDTH - total_w) // 2
        oy = PANEL_HEIGHT + (usable_h - total_h) // 2
        return ox, oy

    def _setup(self):
        self.tiles = []
        self.selected_tile = None
        self.status = "Выбери пару одинаковых фруктов"
        self.game_over = False

        total = COLS * ROWS
        if total % 2 != 0:
            total -= 1

        fruit_pool = (FRUITS * 10)[: total // 2]
        symbol_list = fruit_pool + fruit_pool
        random.shuffle(symbol_list)

        ox, oy = self._origin()
        for i, fruit in enumerate(symbol_list):
            row = i // COLS
            col = i % COLS
            value = FRUITS.index(fruit)
            x = ox + col * (TILE_WIDTH + TILE_MARGIN)
            y = oy + row * (TILE_HEIGHT + TILE_MARGIN)
            self.tiles.append(Tile(value, fruit, row, col, x, y))

    def _active(self):
        return [t for t in self.tiles if not t.is_removed]

    def _is_free(self, tile):
        if tile.is_removed:
            return False
        occupied = {(t.row, t.col) for t in self._active()}
        has_left  = (tile.row, tile.col - 1) in occupied
        has_right = (tile.row, tile.col + 1) in occupied
        return not has_left or not has_right

    def _free_tiles(self):
        return [t for t in self._active() if self._is_free(t)]

    def handle_click(self, mouse_pos):
        if self.game_over:
            return

        clicked = None
        for tile in reversed(self._active()):
            if tile.is_clicked(mouse_pos):
                clicked = tile
                break

        if clicked is None:
            return

        if not self._is_free(clicked):
            self.status = "Плитка заблокирована — нужен свободный край"
            return

        if self.selected_tile is None:
            self.selected_tile = clicked
            clicked.set_selected(True)
            self.status = f"Выбрано: {clicked.fruit}  —  найди пару"
            return

        if self.selected_tile is clicked:
            clicked.set_selected(False)
            self.selected_tile = None
            self.status = "Выбор снят"
            return

        if self.selected_tile.value == clicked.value:
            self.selected_tile.is_removed = True
            clicked.is_removed = True
            self.selected_tile = None
            self.status = f"Пара убрана!  Осталось: {self.remaining_count()}"
            self._check_end()
        else:
            self.selected_tile.set_selected(False)
            self.selected_tile = clicked
            clicked.set_selected(True)
            self.status = "Не совпадают — выбери другую плитку"

    def _check_end(self):
        if self.remaining_count() == 0:
            self.status = "ПОБЕДА!  Все плитки убраны!"
            self.game_over = True
            return
        if not self.has_moves():
            self.status = "Нет ходов — нажми «Перемешать»"
            self.game_over = True

    def has_moves(self):
        groups = {}
        for t in self._free_tiles():
            groups.setdefault(t.value, []).append(t)
        return any(len(v) >= 2 for v in groups.values())

    def get_hint(self):
        groups = {}
        for t in self._free_tiles():
            groups.setdefault(t.value, []).append(t)
        for lst in groups.values():
            if len(lst) >= 2:
                return lst[0], lst[1]
        return None, None

    def shuffle_remaining(self):
        active = self._active()
        if not active:
            return
        if self.selected_tile:
            self.selected_tile.set_selected(False)
            self.selected_tile = None
        data = [(t.fruit, t.value) for t in active]
        random.shuffle(data)
        for tile, (fr, val) in zip(active, data):
            tile.fruit = fr
            tile.value = val
        self.game_over = False
        if not self.has_moves():
            self.shuffle_remaining()
        else:
            self.status = f"Перемешано!  Осталось: {self.remaining_count()}"

    def remaining_count(self):
        return len(self._active())

    def new_game(self):
        self._setup()

    def draw(self, surface, mouse_pos):
        free_ids = {id(t) for t in self._free_tiles()}
        for tile in self.tiles:
            if not tile.is_removed:
                tile.draw(surface, mouse_pos, id(tile) in free_ids)
