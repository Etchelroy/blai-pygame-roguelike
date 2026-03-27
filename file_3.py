import pygame
import math
import random

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.velocity_x = 0
        self.velocity_y = 0
        self.health = 0
        self.max_health = 0
        self.speed = 0
        self.width = 0
        self.height = 0
        self.damage = 0
        self.attack_cooldown = 0
        self.attack_time = 0
        self.projectiles = []

        if enemy_type == 'rusher':
            self.health = 20
            self.max_health = 20
            self.speed = 150
            self.width = 18
            self.height = 18
            self.damage = 10
            self.attack_cooldown = 1.0
        elif enemy_type == 'ranged':
            self.health = 30
            self.max_health = 30
            self.speed = 80
            self.width = 16
            self.height = 16
            self.damage = 5
            self.attack_cooldown = 1.5
        elif enemy_type == 'boss':
            self.health = 100
            self.max_health = 100
            self.speed = 120
            self.width = 40
            self.height = 40
            self.damage = 20
            self.attack_cooldown = 0.8

    def update(self, dt, player):
        self.attack_time = max(0, self.attack_time - dt)

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist > 0:
            dir_x = dx / dist
            dir_y = dy / dist
        else:
            dir_x = dir_y = 0

        if self.enemy_type == 'rusher':
            self.velocity_x = dir_x * self.speed
            self.velocity_y = dir_y * self.speed
            if dist < 50 and self.attack_time <= 0:
                self.attack_time = self.attack_cooldown
        elif self.enemy_type == 'ranged':
            if dist > 300:
                self.velocity_x = dir_x * self.speed
                self.velocity_y = dir_y * self.speed
            else:
                self.velocity_x *= 0.9
                self.velocity_y *= 0.9

            if dist < 400 and self.attack_time <= 0:
                projectile = {
                    'x': self.x,
                    'y': self.y,
                    'vx': dir_x * 250,
                    'vy': dir_y * 250,
                    'lifetime': 5.0,
                    'radius': 4,
                    'damage': self.damage
                }
                self.projectiles.append(projectile)
                self.attack_time = self.attack_cooldown
        elif self.enemy_type == 'boss':
            if dist > 150:
                self.velocity_x = dir_x * self.speed
                self.velocity_y = dir_y * self.speed
            else:
                self.velocity_x *= 0.8
                self.velocity_y *= 0.8

            if dist < 350 and self.attack_time <= 0:
                for angle_offset in [-0.3, 0, 0.3]:
                    angle = math.atan2(dy, dx) + angle_offset
                    projectile = {
                        'x': self.x,
                        'y': self.y,
                        'vx': math.cos(angle) * 300,
                        'vy': math.sin(angle) * 300,
                        'lifetime': 5.0,
                        'radius': 4,
                        'damage': self.damage
                    }
                    self.projectiles.append(projectile)
                self.attack_time = self.attack_cooldown

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        for projectile in self.projectiles[:]:
            projectile['x'] += projectile['vx'] * dt
            projectile['y'] += projectile['vy'] * dt
            projectile['lifetime'] -= dt
            if projectile['lifetime'] <= 0:
                self.projectiles.remove(projectile)

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    def draw(self, surface):
        if self.enemy_type == 'rusher':
            color = (255, 0, 0)
        elif self.enemy_type == 'ranged':
            color = (0, 0, 255)
        else:
            color = (255, 100, 0)

        pygame.draw.rect(surface, color, self.get_rect())

        for projectile in self.projectiles:
            pygame.draw.circle(surface, (255, 0, 255), (int(projectile['x']), int(projectile['y'])), projectile['radius'])