import pygame
import math

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 200
        self.dash_speed = 500
        self.dash_duration = 0.15
        self.dash_cooldown = 0.5
        self.dash_time = 0
        self.dash_cooldown_time = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.health = 100
        self.max_health = 100
        self.damage = 10
        self.projectiles = []
        self.shoot_cooldown = 0.1
        self.shoot_time = 0
        self.dashing = False
        self.dash_dir_x = 0
        self.dash_dir_y = 0

    def update(self, dt, keys, mouse_pos):
        self.shoot_time = max(0, self.shoot_time - dt)
        self.dash_time = max(0, self.dash_time - dt)
        self.dash_cooldown_time = max(0, self.dash_cooldown_time - dt)

        vel_x = vel_y = 0
        if keys[pygame.K_w]:
            vel_y -= 1
        if keys[pygame.K_s]:
            vel_y += 1
        if keys[pygame.K_a]:
            vel_x -= 1
        if keys[pygame.K_d]:
            vel_x += 1

        if vel_x != 0 or vel_y != 0:
            length = math.sqrt(vel_x**2 + vel_y**2)
            vel_x /= length
            vel_y /= length

        if self.dashing:
            self.velocity_x = self.dash_dir_x * self.dash_speed
            self.velocity_y = self.dash_dir_y * self.dash_speed
            if self.dash_time <= 0:
                self.dashing = False
                self.velocity_x = vel_x * self.speed
                self.velocity_y = vel_y * self.speed
        else:
            self.velocity_x = vel_x * self.speed
            self.velocity_y = vel_y * self.speed

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.aim_x = dx / dist
            self.aim_y = dy / dist
        else:
            self.aim_x = 1
            self.aim_y = 0

        for projectile in self.projectiles[:]:
            projectile['x'] += projectile['vx'] * dt
            projectile['y'] += projectile['vy'] * dt
            projectile['lifetime'] -= dt
            if projectile['lifetime'] <= 0:
                self.projectiles.remove(projectile)

    def shoot(self):
        if self.shoot_time <= 0:
            projectile = {
                'x': self.x,
                'y': self.y,
                'vx': self.aim_x * 400,
                'vy': self.aim_y * 400,
                'lifetime': 5.0,
                'radius': 5,
                'damage': self.damage
            }
            self.projectiles.append(projectile)
            self.shoot_time = self.shoot_cooldown

    def dash(self):
        if self.dash_cooldown_time <= 0 and not self.dashing:
            vel_x = vel_y = 0
            if pygame.key.get_pressed()[pygame.K_w]:
                vel_y -= 1
            if pygame.key.get_pressed()[pygame.K_s]:
                vel_y += 1
            if pygame.key.get_pressed()[pygame.K_a]:
                vel_x -= 1
            if pygame.key.get_pressed()[pygame.K_d]:
                vel_x += 1

            if vel_x == 0 and vel_y == 0:
                vel_x = 1

            length = math.sqrt(vel_x**2 + vel_y**2)
            self.dash_dir_x = vel_x / length
            self.dash_dir_y = vel_y / length

            self.dashing = True
            self.dash_time = self.dash_duration
            self.dash_cooldown_time = self.dash_cooldown

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    def draw(self, surface):
        color = (0, 255, 0) if not self.dashing else (100, 255, 100)
        pygame.draw.rect(surface, color, self.get_rect())
        end_x = self.x + self.aim_x * 30
        end_y = self.y + self.aim_y * 30
        pygame.draw.line(surface, (255, 255, 0), (self.x, self.y), (end_x, end_y), 2)

        for projectile in self.projectiles:
            pygame.draw.circle(surface, (255, 255, 0), (int(projectile['x']), int(projectile['y'])), projectile['radius'])