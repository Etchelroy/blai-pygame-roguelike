import pygame
import math

class Projectile:
    def __init__(self, x, y, dx, dy, speed, damage, color, size=6, owner='player'):
        self.x = x
        self.y = y
        norm = math.sqrt(dx*dx + dy*dy) or 1
        self.dx = dx / norm * speed
        self.dy = dy / norm * speed
        self.damage = damage
        self.color = color
        self.size = size
        self.active = True
        self.owner = owner

    def update(self, dt, dungeon):
        self.x += self.dx * dt
        self.y += self.dy * dt
        ts = dungeon.tile_size
        tx, ty = int(self.x // ts), int(self.y // ts)
        if dungeon.is_wall(tx, ty):
            self.active = False

    def check_collision(self, entity):
        ex, ey = entity.x + entity.size//2, entity.y + entity.size//2
        px, py = self.x, self.y
        dist = math.sqrt((ex-px)**2 + (ey-py)**2)
        return dist < (entity.size//2 + self.size)

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        pygame.draw.circle(surface, self.color, (sx, sy), self.size)


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.size = 24
        self.speed = 220
        self.max_hp = 100
        self.hp = 100
        self.damage = 25
        self.projectiles = []
        self.shoot_cooldown = 0
        self.shoot_rate = 0.25
        self.alive = True
        self.dash_cooldown = 0
        self.dash_duration = 0
        self.dash_dx = 0
        self.dash_dy = 0
        self.dash_speed = 600
        self.dash_time = 0.15
        self.dash_cd_max = 0.8
        self.invincible = 0
        self.color = (80, 160, 255)

    def dash(self):
        if self.dash_cooldown <= 0 and self.dash_duration <= 0:
            self.dash_duration = self.dash_time
            self.dash_cooldown = self.dash_cd_max
            self.invincible = self.dash_time

    def shoot(self, target_x, target_y):
        if self.shoot_cooldown <= 0:
            cx = self.x + self.size // 2
            cy = self.y + self.size // 2
            dx = target_x - cx
            dy = target_y - cy
            p = Projectile(cx, cy, dx, dy, 600, self.damage, (255, 220, 50), 6, 'player')
            self.projectiles.append(p)
            self.shoot_cooldown = self.shoot_rate

    def take_damage(self, amount):
        if self.invincible > 0:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        self.invincible = 0.3

    def update(self, dt, dx, dy, dungeon):
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.dash_cooldown = max(0, self.dash_cooldown - dt)
        self.invincible = max(0, self.invincible - dt)

        if self.dash_duration > 0:
            self.dash_duration -= dt
            move_dx = self.dash_dx * self.dash_speed * dt
            move_dy = self.dash_dy * self.dash_speed * dt
        else:
            if dx != 0 or dy != 0:
                norm = math.sqrt(dx*dx + dy*dy)
                self.dash_dx = dx / norm
                self.dash_dy = dy / norm
            move_dx = dx * self.speed * dt if (dx != 0 or dy != 0) else 0
            move_dy = dy * self.speed * dt if (dx != 0 or dy != 0) else 0
            if dx != 0 and dy != 0:
                norm = math.sqrt(2)
                move_dx /= norm
                move_dy /= norm

        ts = dungeon.tile_size
        new_x = self.x + move_dx
        new_y = self.y + move_dy

        if not self._collides(new_x, self.y, dungeon, ts):
            self.x = new_x
        if not self._collides(self.x, new_y, dungeon, ts):
            self.y = new_y

    def _collides(self, x, y, dungeon, ts):
        margin = 2
        corners = [
            (x + margin, y + margin),
            (x + self.size - margin, y + margin),
            (x + margin, y + self.size - margin),
            (x + self.size - margin, y + self.size - margin),
        ]
        for cx, cy in corners:
            tx, ty = int(cx // ts), int(cy // ts)
            if dungeon.is_wall(tx, ty):
                return True
        return False

    def update_projectiles(self, dt, dungeon):
        for p in self.projectiles:
            if p.active:
                p.update(dt, dungeon)
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        color = (200, 200, 255) if self.invincible > 0 else self.color
        pygame.draw.rect(surface, color, (sx, sy, self.size, self.size))
        pygame.draw.rect(surface, (255, 255, 255), (sx, sy, self.size, self.size), 2)
        
        bar_w = self.size
        bar_h = 5
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (180, 30, 30), (sx, sy - 8, bar_w, bar_h))
        pygame.draw.rect(surface, (50, 220, 50), (sx, sy - 8, int(bar_w * ratio), bar_h))
        
        for p in self.projectiles:
            p.draw(surface, camera_x, camera_y)