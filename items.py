import pygame
import math

class Item:
    TYPES = {
        "health": {"color": (80, 220, 80), "label": "HP", "symbol": "+"},
        "damage": {"color": (220, 80, 80), "label": "DMG", "symbol": "D"},
        "speed":  {"color": (80, 160, 220), "label": "SPD", "symbol": "S"},
    }

    def __init__(self, x, y, item_type):
        self.x = float(x)
        self.y = float(y)
        self.item_type = item_type
        self.radius = 14
        self.bob_timer = 0.0
        info = self.TYPES.get(item_type, self.TYPES["health"])
        self.color = info["color"]
        self.label = info["label"]
        self.symbol = info["symbol"]
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

    def apply(self, player):
        if self.item_type == "health":
            player.health = min(player.max_health, player.health + 30)
        elif self.item_type == "damage":
            player.damage = int(player.damage * 1.25)
        elif self.item_type == "speed":
            player.speed = min(400, player.speed + 40)

    def update(self, dt):
        self.bob_timer += dt

    def draw(self, screen):
        bob = math.sin(self.bob_timer * 3) * 4
        cx = int(self.x)
        cy = int(self.y + bob)
        pygame.draw.circle(screen, (30, 30, 30), (cx + 2, cy + 2), self.radius)
        pygame.draw.circle(screen, self.color, (cx, cy), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), self.radius, 2)
        label = self.font.render(self.symbol, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=(cx, cy)))