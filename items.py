import pygame
import random

TILE_SIZE = 32

ITEM_CONFIGS = {
    "health": {
        "name": "Health Potion",
        "color": (220, 60, 60),
        "description": "Restores 40 HP",
    },
    "damage": {
        "name": "Damage Crystal",
        "color": (255, 140, 0),
        "description": "+15 Damage for 20s",
    },
    "speed": {
        "name": "Swift Boots",
        "color": (60, 220, 120),
        "description": "+50 Speed for 20s",
    },
}

class Item:
    def __init__(self, x, y, item_type):
        self.x = float(x)
        self.y = float(y)
        self.item_type = item_type
        cfg = ITEM_CONFIGS.get(item_type, ITEM_CONFIGS["health"])
        self.name = cfg["name"]
        self.color = cfg["color"]
        self.description = cfg["description"]
        self.w = 20
        self.h = 20
        self.bob_timer = random.uniform(0, math.pi * 2)

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w // 2), int(self.y - self.h // 2), self.w, self.h)

    def apply(self, player):
        if self.item_type == "health":
            player.hp = min(player.max_hp, player.hp + 40)
        elif self.item_type == "damage":
            player.damage = player.base_damage + 15
            player.damage_boost_timer = 20.0
        elif self.item_type == "speed":
            player.speed = player.base_speed + 50
            player.speed_boost_timer = 20.0

    def render(self, screen, cam_x, cam_y):
        import math
        self.bob_timer += 0.05
        bob = int(math.sin(self.bob_timer) * 3)
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y) + bob

        # shadow
        pygame.draw.ellipse(screen, (20, 20, 20),
                            (sx - 10, sy + 8, 20, 6))
        # gem shape
        points = [
            (sx, sy - 12),
            (sx + 9, sy - 3),
            (sx + 9, sy + 5),
            (sx, sy + 12),
            (sx - 9, sy + 5),
            (sx - 9, sy - 3),
        ]
        pygame.draw.polygon(screen, self.color, points)
        highlight = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.polygon(screen, highlight, [
            (sx, sy - 12),
            (sx + 9, sy - 3),
            (sx, sy - 2),
        ])
        pygame.draw.polygon(screen, (255, 255, 255, 120), points, 1)

import math