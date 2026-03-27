import random
import pygame

class Room:
    def __init__(self, x, y, width=400, height=300):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.enemies = []
        self.cleared = False
        self.doors = {'up': False, 'down': False, 'left': False, 'right': False}

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, (50, 50, 50), self.get_rect(), 2)

        if self.doors['up']:
            pygame.draw.line(surface, (100, 100, 100), (self.x + self.width // 2 - 20, self.y), (self.x + self.width // 2 + 20, self.y), 3)
        if self.doors['down']:
            pygame.draw.line(surface, (100, 100, 100), (self.x + self.width // 2 - 20, self.y + self.height), (self.x + self.width // 2 + 20, self.y + self.height), 3)
        if self.doors['left']:
            pygame.draw.line(surface, (100, 100, 100), (self.x, self.y + self.height // 2 - 20), (self.x, self.y + self.height // 2 + 20), 3)
        if self.doors['right']:
            pygame.draw.line(surface, (100, 100, 100), (self.x + self.width, self.y + self.height // 2 - 20), (self.x + self.width, self.y + self.height // 2 + 20), 3)

class Dungeon:
    def __init__(self, width=1600, height=900, room_width=400, room_height=300):
        self.width = width
        self.height = height
        self.room_width = room_width
        self.room_height = room_height
        self.rooms = []
        self.current_room_idx = 0
        self.floor = 1
        self.generate_floor()

    def generate_floor(self):
        from enemies import Enemy

        self.rooms = []
        cols = self.width // self.room_width
        rows = self.height // self.room_height
        num_rooms = random.randint(4, 7)

        positions = []
        for _ in range(num_rooms):
            x = random.randint(0, cols - 1)
            y = random.randint(0, rows - 1)
            if (x, y) not in positions:
                positions.append((x, y))

        positions.sort(key=lambda p: (p[1], p[0]))

        for x, y in positions:
            room = Room(x * self.room_width, y * self.room_height)
            self.rooms.append(room)

        for i in range(len(self.rooms) - 1):
            current = self.rooms[i]
            next_room = self.rooms[i + 1]

            if next_room.x > current.x:
                current.doors['right'] = True
                next_room.doors['left'] = True
            elif next_room.x < current.x:
                current.doors['left'] = True
                next_room.doors['right'] = True

            if next_room.y > current.y:
                current.doors['down'] = True
                next_room.doors['up'] = True
            elif next_room.y < current.y:
                current.doors['up'] = True
                next_room.doors['down'] = True

        for i, room in enumerate(self.rooms):
            if i == len(self.rooms) - 1:
                enemy = Enemy(room.x + room.width // 2, room.y + room.height // 2, 'boss')
                room.enemies.append(enemy)
            else:
                num_enemies = random.randint(2, 4)
                for _ in range(num_enemies):
                    ex = room.x + random.randint(50, room.width - 50)
                    ey = room.y + random.randint(50, room.height - 50)
                    enemy_type = random.choice(['rusher', 'ranged', 'rusher', 'ranged'])
                    enemy = Enemy(ex, ey, enemy_type)
                    room.enemies.append(enemy)

        self.current_room_idx = 0

    def get_current_room(self):
        if self.current_room_idx < len(self.rooms):
            return self.rooms[self.current_room_idx]
        return None

    def current_room_cleared(self):
        room = self.get_current_room()
        if room:
            room.cleared = len(room.enemies) == 0

    def advance_room(self):
        self.current_room_idx += 1
        if self.current_room_idx >= len(self.rooms):
            self.floor += 1
            self.generate_floor()
            return True
        return False

    def draw(self, surface):
        for room in self.rooms:
            room.draw(surface)