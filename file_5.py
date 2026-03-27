import pygame
import math

class Projectile:
    def __init__(self, x, y, vx, vy, damage, hostile=False, radius=4):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.hostile = hostile
        self.radius = radius
        self.lifetime = 10.0
    
    def update(self, delta_time):
        """Update projectile position"""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.lifetime -= delta_time
    
    def is_alive(self):
        """Check if projectile is still active"""
        return self.lifetime > 0
    
    def render(self, surface):
        """Draw projectile"""
        color = (255, 100, 100) if self.hostile else (100, 255, 100)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)

class ProjectileManager:
    def __init__(self):
        self.projectiles = []
    
    def add(self, projectile):
        """Add projectile"""
        self.projectiles.append(projectile)
    
    def remove(self, projectile):
        """Remove projectile"""
        if projectile in self.projectiles:
            self.projectiles.remove(projectile)
    
    def update(self, delta_time, dungeon):
        """Update all projectiles"""
        for proj in list(self.projectiles):
            proj.update(delta_time)
            if not proj.is_alive():
                self.remove(proj)
    
    def render(self, surface):
        """Render all projectiles"""
        for proj in self.projectiles:
            proj.render(surface)