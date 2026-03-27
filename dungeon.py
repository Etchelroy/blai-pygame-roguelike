import random

TILE_WALL = 0
TILE_FLOOR = 1
TILE_DOOR = 2

class Dungeon:
    def __init__(self, width, height, floor_num=1):
        self.width = width
        self.height = height
        self.floor_num = floor_num
        self.tiles = [[TILE_WALL] * width for _ in range(height)]
        self.rooms = []

    def get_tile(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return TILE_WALL
        return self.tiles[ty][tx]

    def set_tile(self, tx, ty, tile):
        if 0 <= tx < self.width and 0 <= ty < self.height:
            self.tiles[ty][tx] = tile

    def generate(self):
        num_rooms = 6 + self.floor_num * 2
        num_rooms = min(num_rooms, 16)
        attempts = 200
        min_w, max_w = 6, 12
        min_h, max_h = 6, 10

        for _ in range(attempts):
            if len(self.rooms) >= num_rooms:
                break
            rw = random.randint(min_w, max_w)
            rh = random.randint(min_h, max_h)
            rx = random.randint(1, self.width - rw - 1)
            ry = random.randint(1, self.height - rh - 1)
            room = {'x': rx, 'y': ry, 'w': rw, 'h': rh}
            if not self._overlaps(room):
                self.rooms.append(room)
                self._carve_room(room)

        for i in range(1, len(self.rooms)):
            self._connect_rooms(self.rooms[i - 1], self.rooms[i])

        self._place_doors()

    def _overlaps(self, room, margin=2):
        for r in self.rooms:
            if (room['x'] < r['x'] + r['w'] + margin and
                room['x'] + room['w'] + margin > r['x'] and
                room['y'] < r['y'] + r['h'] + margin and
                room['y'] + room['h'] + margin > r['y']):
                return True
        return False

    def _carve_room(self, room):
        for ty in range(room['y'], room['y'] + room['h']):
            for tx in range(room['x'], room['x'] + room['w']):
                self.set_tile(tx, ty, TILE_FLOOR)

    def _connect_rooms(self, r1, r2):
        cx1 = r1['x'] + r1['w'] // 2
        cy1 = r1['y'] + r1['h'] // 2
        cx2 = r2['x'] + r2['w'] // 2
        cy2 = r2['y'] + r2['h'] // 2
        if random.random() < 0.5:
            self._carve_h_corridor(min(cx1, cx2), max(cx1, cx2), cy1)
            self._carve_v_corridor(min(cy1, cy2), max(cy1, cy2), cx2)
        else:
            self._carve_v_corridor(min(cy1, cy2), max(cy1, cy2), cx1)
            self._carve_h_corridor(min(cx1, cx2), max(cx1, cx2), cy2)

    def _carve_h_corridor(self, x0, x1, y):
        for x in range(x0, x1 + 1):
            self.set_tile(x, y, TILE_FLOOR)
            self.set_tile(x, y + 1, TILE_FLOOR)

    def _carve_v_corridor(self, y0, y1, x):
        for y in range(y0, y1 + 1):
            self.set_tile(x, y, TILE_FLOOR)
            self.set_tile(x + 1, y, TILE_FLOOR)

    def _place_doors(self):
        pass  # Doors are handled logically; tiles are floor tiles for corridors