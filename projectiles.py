import pygame
import math

class Projectile:
    def __init__(self, x, y, dx, dy, owner, damage, speed=400, color=(255, 220, 50)):
        self.x = float(x)
        self.y = float(y)
        self.dx = dx
        self.dy = dy
        self.owner = owner
        self.damage = damage
        self.speed = speed
        self.color = color
        self.radius = 7
        self.lifetime = 3.0
        self.timer = 0.0

    def update(self, dt):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        self.timer += dt

    def is_expired(self):
        return self.timer >= self.lifetime

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        core = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.circle(screen, core, (int(self.x), int(self.y)), max(2, self.radius - 3))