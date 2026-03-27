import pygame
import random

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.radius = 5
        self.item_type = item_type  # "health", "damage", "speed"
        self.lifetime = 30.0
        self.color_map = {
            "health": (100, 255, 100),
            "damage": (255, 100, 100),
            "speed": (100, 100, 255)
        }
        self.color = self.color_map.get(item_type, (255, 255, 100))
    
    def update(self, delta_time):
        """Update item lifetime"""
        self.lifetime -= delta_time
    
    def is_alive(self):
        """Check if item still exists"""
        return self.lifetime > 0
    
    def apply(self, player):
        """Apply item effect to player"""
        if self.item_type == "health":
            player.heal(30)
        elif self.item_type == "damage":
            player.boost_damage(5)
        elif self.item_type == "speed":
            player.boost_speed(50)
    
    def render(self, surface):
        """Draw item"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class ItemManager:
    def __init__(self):
        self.items = []
    
    def spawn_item(self, x, y):
        """Spawn random item at position"""
        item_type = random.choices(
            ["health", "damage", "speed"],
            weights=[50, 25, 25]
        )[0]
        self.items.append(Item(x, y, item_type))
    
    def remove(self, item):
        """Remove item"""
        if item in self.items:
            self.items.remove(item)
    
    def update(self, delta_time):
        """Update all items"""
        for item in list(self.items):
            item.update(delta_time)
            if not item.is_alive():
                self.remove(item)
    
    def render(self, surface):
        """Render all items"""
        for item in self.items:
            item.render(surface)