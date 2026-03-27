import pygame

class ItemPickup:
    def __init__(self, x, y, item_type):
        self.x = float(x - 12)
        self.y = float(y - 12)
        self.size = 24
        self.item_type = item_type
        self.collected = False
        self.bob = 0.0
        self.bob_speed = 2.0

        if item_type == 'health':
            self.color = (60, 220, 80)
            self.label = 'HP'
        elif item_type == 'damage':
            self.color = (220, 80, 60)
            self.label = 'DMG'
        else:
            self.color = (80, 160, 255)
            self.label = 'SPD'

    def apply(self, player):
        if self.item_type == 'health':
            player.hp = min(player.max_hp, player.hp + 40)
        elif self.item_type == 'damage':
            player.damage = int(player.damage * 1.25)
        elif self.item_type == 'speed':
            player.speed = int(player.speed * 1.15)

    def draw(self, surface, camera_x, camera_y):
        import math
        self.bob += 0.05
        bob_offset = int(math.sin(self.bob * self.bob_speed * 3) * 4)
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y + bob_offset)
        
        pygame.draw.rect(surface, (30, 30, 40), (sx - 2, sy - 2, self.size + 4, self.size + 4))
        pygame.draw.rect(surface, self.color, (sx, sy, self.size, self.size))
        pygame.draw.rect(surface, (255, 255, 255), (sx, sy, self.size, self.size), 2)
        
        font = pygame.font.SysFont('Arial', 9, bold=True)
        text = font.render(self.label, True, (255, 255, 255))
        surface.blit(text, (sx + self.size//2 - text.get_width()//2, sy + self.size//2 - text.get_height()//2))