import pygame
import math
from projectiles import Projectile

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 18
        self.speed = 220.0
        self.health = 100
        self.max_health = 100
        self.damage = 25
        self.vx = 0.0
        self.vy = 0.0
        
        self.dash_speed = 600.0
        self.dash_duration = 0.15
        self.dash_cooldown = 0.8
        self.dash_timer = 0.0
        self.dash_cd_timer = 0.0
        self.dashing = False
        self.dash_dx = 0.0
        self.dash_dy = 0.0
        
        self.shoot_cooldown = 0.25
        self.shoot_timer = 0.0
        
        self.invincible_timer = 0.0

    def handle_movement(self, keys, dt):
        if self.dashing:
            return
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length
        self.vx = dx * self.speed
        self.vy = dy * self.speed

    def dash(self):
        if self.dash_cd_timer <= 0 and not self.dashing:
            length = math.hypot(self.vx, self.vy)
            if length > 0:
                self.dash_dx = self.vx / length
                self.dash_dy = self.vy / length
            else:
                self.dash_dx = 0
                self.dash_dy = -1
            self.dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cd_timer = self.dash_cooldown
            self.invincible_timer = self.dash_duration

    def update(self, dt):
        if self.dashing:
            self.x += self.dash_dx * self.dash_speed * dt
            self.y += self.dash_dy * self.dash_speed * dt
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dashing = False
        else:
            self.x += self.vx * dt
            self.y += self.vy * dt
        
        if self.dash_cd_timer > 0:
            self.dash_cd_timer -= dt
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

    def shoot(self, target_pos):
        if self.shoot_timer > 0:
            return None
        self.shoot_timer = self.shoot_cooldown
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        length = math.hypot(dx, dy)
        if length == 0:
            return None
        dx /= length
        dy /= length
        return Projectile(self.x, self.y, dx, dy, owner="player", damage=self.damage, speed=500, color=(255, 220, 50))

    def take_damage(self, amount):
        if self.invincible_timer > 0:
            return
        self.health -= amount
        self.invincible_timer = 0.5
        if self.health < 0:
            self.health = 0

    def draw(self, screen):
        color = (50, 200, 255)
        if self.invincible_timer > 0:
            color = (255, 255, 100)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (200, 240, 255), (int(self.x), int(self.y)), self.radius, 2)
        if self.dashing:
            pygame.draw.circle(screen, (100, 200, 255), (int(self.x), int(self.y)), self.radius + 6, 2)