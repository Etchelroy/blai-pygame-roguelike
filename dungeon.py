import pygame
import random

TILE_FLOOR = 0
TILE_WALL = 1
TILE_DOOR = 2

class Room:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.center_x = x + w // 2
        self.center_y = y + h // 2
        self.enemies = []
        self.cleared = False
        self.visited = False

    def intersects(self, other, padding=2):
        return (self.x - padding < other.x + other.w and
                self.x + self.w + padding > other.x and
                self.y - padding < other.y + other.h and
                self.y + self.h + padding > other.y)


class Dungeon:
    def __init__(self, screen_w=1280, screen_h=720, floor=0):
        self.tile_size = 40
        self.floor = floor
        self.map_w = 80
        self.map_h = 60
        self.grid = [[TILE_WALL] * self.map_w for _ in range(self.map_h)]
        self.rooms = []
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._generate(floor)

    def _generate(self, floor):
        from enemies import MeleeEnemy, RangedEnemy, BossEnemy
        num_rooms = 6 + floor * 2
        num_rooms = min(num_rooms, 14)
        max_attempts = 200

        for _ in range(max_attempts):
            if len(self.rooms) >= num_rooms:
                break
            w = random.randint(5, 10)
            h = random.randint(5, 8)
            x = random.randint(1, self.map_w - w - 2)
            y = random.randint(1, self.map_h - h - 2)
            room = Room(x, y, w, h)
            if any(room.intersects(r) for r in self.rooms):
                continue
            self._carve_room(room)
            if self.rooms:
                prev = self.rooms[-1]
                self._carve_corridor(prev.center_x, prev.center_y, room.center_x, room.center_y)
            self.rooms.append(room)

        for i, room in enumerate(self.rooms):
            if i == 0:
                room.visited = True
                continue
            count = 1 + floor // 2
            is_boss_room = (i == len(self.rooms) - 1)
            if is_boss_room:
                boss = BossEnemy(
                    room.center_x * self.tile_size - 20,
                    room.center_y * self.tile_size - 20,
                    floor
                )
                room.enemies.append(boss)
            else:
                for _ in range(count + random.randint(0, 2)):
                    ex = random.randint(room.x + 1, room.x + room.w - 2) * self.tile_size
                    ey = random.randint(room.y + 1, room.y + room.h - 2) * self.tile_size
                    if random.random() < 0.4:
                        room.enemies.append(RangedEnemy(ex, ey, floor))
                    else:
                        room.enemies.append(MeleeEnemy(ex, ey, floor))

    def _carve_room(self, room):
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                self.grid[y][x] = TILE_FLOOR

    def _carve_corridor(self, x1, y1, x2, y2):
        x, y = x1, y1
        while x != x2:
            self.grid[y][x] = TILE_FLOOR
            x += 1 if x2 > x else -1
        while y != y2:
            self.grid[y][x] = TILE_FLOOR
            y += 1 if y2 > y else -1

    def is_wall(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= self.map_w or ty >= self.map_h:
            return True
        return self.grid[ty][tx] == TILE_WALL

    def get_room_at(self, wx, wy):
        tx = int(wx // self.tile_size)
        ty = int(wy // self.tile_size)
        for room in self.rooms:
            if room.x <= tx < room.x + room.w and room.y <= ty < room.y + room.h:
                if not room.visited:
                    room.visited = True
                return room
        return None

    def is_room_cleared(self, room):
        return all(not e.alive for e in room.enemies)

    def get_active_enemies(self):
        result = []
        for room in self.rooms:
            if room.visited:
                for e in room.enemies:
                    if e.alive:
                        result.append(e)
        return result

    def all_rooms_cleared(self):
        return all(r.cleared for r in self.rooms)

    def draw(self, surface, camera_x, camera_y):
        ts = self.tile_size
        start_tx = max(0, camera_x // ts)
        start_ty = max(0, camera_y // ts)
        end_tx = min(self.map_w, (camera_x + self.screen_w) // ts + 2)
        end_ty = min(self.map_h, (camera_y + self.screen_h) // ts + 2)

        floor_color = (50, 50, 60)
        wall_color = (25, 25, 35)
        wall_top = (40, 40, 55)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                sx = tx * ts - camera_x
                sy = ty * ts - camera_y
                if self.grid[ty][tx] == TILE_WALL:
                    pygame.draw.rect(surface, wall_color, (sx, sy, ts, ts))
                    pygame.draw.rect(surface, wall_top, (sx, sy, ts, 3))
                else:
                    pygame.draw.rect(surface, floor_color, (sx, sy, ts, ts))
                    pygame.draw.rect(surface, (45, 45, 55), (sx, sy, ts, ts), 1)