import pygame
import random

TILE_SIZE = 32
WALL = 1
FLOOR = 0

class Dungeon:
    def __init__(self, floor_num):
        self.floor_num = floor_num
        self.width = 80
        self.height = 60
        self.tiles = [[WALL] * self.width for _ in range(self.height)]
        self.rooms = []
        self._generate()
        self._prerender()

    def _generate(self):
        random.seed(self.floor_num * 1337 + 42)
        attempts = 0
        num_rooms = 6 + self.floor_num
        while len(self.rooms) < num_rooms and attempts < 500:
            attempts += 1
            w = random.randint(6, 14)
            h = random.randint(6, 12)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            if not self._overlaps(x, y, w, h):
                self._carve_room(x, y, w, h)
                if self.rooms:
                    px, py, pw, ph = self.rooms[-1]
                    cx1 = px + pw // 2
                    cy1 = py + ph // 2
                    cx2 = x + w // 2
                    cy2 = y + h // 2
                    self._carve_corridor(cx1, cy1, cx2, cy2)
                self.rooms.append((x, y, w, h))

    def _overlaps(self, x, y, w, h):
        for rx, ry, rw, rh in self.rooms:
            if x < rx + rw + 2 and x + w + 2 > rx and y < ry + rh + 2 and y + h + 2 > ry:
                return True
        return False

    def _carve_room(self, x, y, w, h):
        for ty in range(y, y + h):
            for tx in range(x, x + w):
                self.tiles[ty][tx] = FLOOR

    def _carve_corridor(self, x1, y1, x2, y2):
        cx, cy = x1, y1
        while cx != x2:
            self.tiles[cy][cx] = FLOOR
            cx += 1 if x2 > cx else -1
        while cy != y2:
            self.tiles[cy][cx] = FLOOR
            cy += 1 if y2 > cy else -1

    def get_player_spawn(self):
        if self.rooms:
            rx, ry, rw, rh = self.rooms[0]
            return ((rx + rw // 2) * TILE_SIZE, (ry + rh // 2) * TILE_SIZE)
        return (100, 100)

    def is_wall(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return True
        return self.tiles[ty][tx] == WALL

    def _prerender(self):
        self.floor_color = (50, 45, 40)
        self.wall_color = (30, 25, 35)
        self.wall_top_color = (60, 50, 70)
        self.floor_detail = (55, 50, 45)

    def render(self, screen, cam_x, cam_y):
        tile_w = TILE_SIZE
        start_tx = max(0, cam_x // tile_w - 1)
        start_ty = max(0, cam_y // tile_w - 1)
        end_tx = min(self.width, (cam_x + 1280) // tile_w + 2)
        end_ty = min(self.height, (cam_y + 720) // tile_w + 2)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                sx = tx * tile_w - cam_x
                sy = ty * tile_w - cam_y
                rect = pygame.Rect(sx, sy, tile_w, tile_w)
                if self.tiles[ty][tx] == FLOOR:
                    pygame.draw.rect(screen, self.floor_color, rect)
                    # subtle grid
                    pygame.draw.rect(screen, self.floor_detail, rect, 1)
                else:
                    pygame.draw.rect(screen, self.wall_color, rect)
                    # top face highlight
                    pygame.draw.rect(screen, self.wall_top_color, pygame.Rect(sx, sy, tile_w, 4))