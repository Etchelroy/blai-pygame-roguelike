import pygame
import random

class Dungeon:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = self.generate_walls()
    
    def generate_walls(self):
        """Generate dungeon walls"""
        walls = []
        
        # Border walls
        walls.append(pygame.Rect(0, 0, self.width, 20))  # top
        walls.append(pygame.Rect(0, self.height - 20, self.width, 20))  # bottom
        walls.append(pygame.Rect(0, 0, 20, self.height))  # left
        walls.append(pygame.Rect(self.width - 20, 0, 20, self.height))  # right
        
        # Random obstacles
        for _ in range(8):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            walls.append(pygame.Rect(x, y, 60, 60))
        
        return walls
    
    def collides_with_walls(self, x, y, radius):
        """Check if circle collides with any wall"""
        for wall in self.walls:
            closest_x = max(wall.left, min(x, wall.right))
            closest_y = max(wall.top, min(y, wall.bottom))
            dist = ((x - closest_x)**2 + (y - closest_y)**2)**0.5
            if dist < radius:
                return True
        return False
    
    def render(self, surface):
        """Draw dungeon"""
        for wall in self.walls:
            pygame.draw.rect(surface, (100, 100, 100), wall)