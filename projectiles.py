import pygame
import math

class Projectile:
    def __init__(self, x, y, dx, dy, speed, damage, color, radius=5):
        self.x = float(x)
        self.y = float(y)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.color = color
        self.radius = radius
        self.lifetime = 3.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           self.radius * 2, self.radius * 2)

    def update(self, dt, collision):
        self.lifetime -= dt
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt

    def is_dead(self, collision):
        if self.lifetime <= 0:
            return True
        if collision.collides_with_wall(self.rect):
            return True
        return False

    def render(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        # glow
        glow_color = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.circle(screen, glow_color, (sx, sy), self.radius - 2)

class ProjectileManager:
    def __init__(self):
        self.player_projectiles = []
        self.enemy_projectiles = []

    def spawn_player_projectile(self, x, y, dx, dy, damage):
        p = Projectile(x, y, dx, dy, 400, damage, (100, 220, 255), radius=6)
        self.player_projectiles.append(p)

    def spawn_enemy_projectile(self, x, y, dx, dy, damage):
        p = Projectile(x, y, dx, dy, 220, damage, (255, 80, 80), radius=5)
        self.enemy_projectiles.append(p)

    def update(self, dt, collision):
        self.player_projectiles = [
            p for p in self.player_projectiles
            if not self._update_and_check(p, dt, collision)
        ]
        self.enemy_projectiles = [
            p for p in self.enemy_projectiles
            if not self._update_and_check(p, dt, collision)
        ]

    def _update_and_check(self, proj, dt, collision):
        proj.update(dt, collision)
        return proj.is_dead(collision)

    def render(self, screen, cam_x, cam_y):
        for p in self.player_projectiles:
            p.render(screen, cam_x, cam_y)
        for p in self.enemy_projectiles:
            p.render(screen, cam_x, cam_y)