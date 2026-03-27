import pygame
import random

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.radius = 8
        self.lifetime = 30.0

        if item_type == 'health':
            self.color = (0, 255, 0)
            self.value = 30
        elif item_type == 'damage':
            self.color = (255, 0, 0)
            self.value = 5
        elif item_type == 'speed':
            self.color = (0, 0, 255)
            self.value = 50

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class ItemManager:
    def __init__(self):
        self.items = []

    def spawn_items(self, room):
        if len(room.enemies) == 0:
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                x = room.x + random.randint(50, room.width - 50)
                y = room.y + random.randint(50, room.height - 50)
                item_type = random.choice(['health', 'damage', 'speed'])
                item = Item(x, y, item_type)
                self.items.append(item)

    def clear_items(self):
        self.items = []

    def update(self, dt):
        for item in self.items[:]:
            item.lifetime -= dt
            if item.lifetime <= 0:
                self.items.remove(item)

    def check_player_collision(self, player):
        for item in self.items[:]:
            if player.get_rect().colliderect(item.get_rect()):
                if item.item_type == 'health':
                    player.heal(item.value)
                elif item.item_type == 'damage':
                    player.damage += item.value
                elif item.item_type == 'speed':
                    player.speed += item.value
                self.items.remove(item)

    def draw(self, surface):
        for item in self.items:
            item.draw(surface)