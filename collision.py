import pygame

TILE_SIZE = 32

class CollisionSystem:
    def __init__(self, dungeon):
        self.dungeon = dungeon

    def collides_with_wall(self, rect):
        # Check all 4 corners and center
        points = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1),
            (rect.centerx, rect.centery),
        ]
        for px, py in points:
            tx = px // TILE_SIZE
            ty = py // TILE_SIZE
            if self.dungeon.is_wall(tx, ty):
                return True
        return False

    def entity_collides(self, rect1, rect2):
        return rect1.colliderect(rect2)

    def get_wall_rect(self, tx, ty):
        return pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)