import pygame

ITEM_COLORS = {
    'health': (50, 220, 80),
    'damage': (220, 80, 50),
    'speed':  (80, 150, 220),
}

ITEM_LABELS = {
    'health': 'HP+',
    'damage': 'DMG+',
    'speed':  'SPD+',
}

class Item:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.collected = False
        self.pulse = 0.0

    def apply(self, player):
        self.collected = True
        if self.kind == 'health':
            player.hp = min(player.max_hp, player.hp + 30)
        elif self.kind == 'damage':
            player.damage = int(player.damage * 1.25)
        elif self.kind == 'speed':
            player.speed = min(300, int(player.speed * 1.15))

    def draw(self, surf, sx, sy):
        import math
        self.pulse += 0.05
        r = int(10 + math.sin(self.pulse) * 2)
        color = ITEM_COLORS.get(self.kind, (200, 200, 200))
        pygame.draw.circle(surf, color, (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx, sy), r, 2)
        font = pygame.font.SysFont(None, 16)
        label = font.render(ITEM_LABELS.get(self.kind, '?'), True, (255, 255, 255))
        surf.blit(label, (sx - label.get_width() // 2, sy - label.get_height() // 2))