import pygame
import math
import random
from player import Projectile

class BaseEnemy:
    def __init__(self, x, y, size, hp, color):
        self.x = float(x)
        self.y = float(y)
        self.size = size
        self.max_hp = hp
        self.hp = hp
        self.color = color
        self.alive = True
        self.projectiles = []
        self.enemy_type = 'base'
        self.contact_damage = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def _move_toward(self, tx, ty, speed, dt, dungeon):
        dx = tx - (self.x + self.size//2)
        dy = ty - (self.y + self.size//2)
        dist = math.sqrt(dx*dx + dy*dy) or 1
        mx = dx/dist * speed * dt
        my = dy/dist * speed * dt
        ts = dungeon.tile_size

        new_x = self.x + mx
        if not self._collides(new_x, self.y, dungeon, ts):
            self.x = new_x
        new_y = self.y + my
        if not self._collides(self.x, new_y, dungeon, ts):
            self.y = new_y

    def _collides(self, x, y, dungeon, ts):
        m = 2
        for cx, cy in [(x+m, y+m), (x+self.size-m, y+m), (x+m, y+self.size-m), (x+self.size-m, y+self.size-m)]:
            if dungeon.is_wall(int(cx//ts), int(cy//ts)):
                return True
        return False

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        pygame.draw.rect(surface, self.color, (sx, sy, self.size, self.size))
        pygame.draw.rect(surface, (255, 255, 255), (sx, sy, self.size, self.size), 2)
        bar_w = self.size
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (150, 20, 20), (sx, sy - 8, bar_w, 5))
        pygame.draw.rect(surface, (50, 200, 50), (sx, sy - 8, int(bar_w * ratio), 5))
        for p in self.projectiles:
            p.draw(surface, camera_x, camera_y)


class MeleeEnemy(BaseEnemy):
    def __init__(self, x, y, floor=0):
        hp = 40 + floor * 15
        super().__init__(x, y, 24, hp, (220, 80, 60))
        self.speed = 140 + floor * 10
        self.enemy_type = 'melee'
        self.contact_damage = 20

    def update(self, dt, player, dungeon):
        if not self.alive:
            return
        px = player.x + player.size//2 - self.size//2
        py = player.y + player.size//2 - self.size//2
        self._move_toward(px, py, self.speed, dt, dungeon)


class RangedEnemy(BaseEnemy):
    def __init__(self, x, y, floor=0):
        hp = 25 + floor * 10
        super().__init__(x, y, 22, hp, (180, 80, 220))
        self.speed = 80 + floor * 5
        self.enemy_type = 'ranged'
        self.shoot_cooldown = random.uniform(0.5, 1.5)
        self.shoot_rate = 1.8
        self.preferred_dist = 250
        self.damage = 12 + floor * 3
        self.contact_damage = 5

    def update(self, dt, player, dungeon):
        if not self.alive:
            return
        for p in self.projectiles:
            p.update(dt, dungeon)
        self.projectiles = [p for p in self.projectiles if p.active]

        px = player.x + player.size//2
        py = player.y + player.size//2
        ex = self.x + self.size//2
        ey = self.y + self.size//2
        dist = math.sqrt((px-ex)**2 + (py-ey)**2)

        if dist < self.preferred_dist - 20:
            dx = ex - px
            dy = ey - py
            norm = math.sqrt(dx*dx+dy*dy) or 1
            flee_x = self.x + dx/norm * self.speed * dt
            flee_y = self.y + dy/norm * self.speed * dt
            ts = dungeon.tile_size
            if not self._collides(flee_x, self.y, dungeon, ts):
                self.x = flee_x
            if not self._collides(self.x, flee_y, dungeon, ts):
                self.y = flee_y
        elif dist > self.preferred_dist + 20:
            self._move_toward(px - self.size//2, py - self.size//2, self.speed, dt, dungeon)

        self.shoot_cooldown -= dt
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_rate
            dx = px - ex
            dy = py - ey
            proj = Projectile(ex, ey, dx, dy, 280, self.damage, (220, 120, 255), 5, 'enemy')
            self.projectiles.append(proj)


class BossEnemy(BaseEnemy):
    def __init__(self, x, y, floor=0):
        hp = 200 + floor * 80
        super().__init__(x, y, 48, hp, (220, 30, 30))
        self.speed = 90 + floor * 8
        self.enemy_type = 'boss'
        self.shoot_cooldown = 1.0
        self.shoot_rate = 0.8
        self.damage = 20 + floor * 5
        self.contact_damage = 30
        self.phase = 1
        self.burst_timer = 0
        self.burst_interval = 4.0

    def update(self, dt, player, dungeon):
        if not self.alive:
            return
        for p in self.projectiles:
            p.update(dt, dungeon)
        self.projectiles = [p for p in self.projectiles if p.active]

        if self.hp < self.max_hp * 0.5:
            self.phase = 2
            self.shoot_rate = 0.4

        px = player.x + player.size//2
        py = player.y + player.size//2
        self._move_toward(px - self.size//2, py - self.size//2, self.speed, dt, dungeon)

        self.shoot_cooldown -= dt
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_rate
            ex = self.x + self.size//2
            ey = self.y + self.size//2
            dx = px - ex
            dy = py - ey
            proj = Projectile(ex, ey, dx, dy, 320, self.damage, (255, 60, 60), 8, 'enemy')
            self.projectiles.append(proj)

        self.burst_timer -= dt
        if self.burst_timer <= 0 and self.phase == 2:
            self.burst_timer = self.burst_interval
            ex = self.x + self.size//2
            ey = self.y + self.size//2
            for i in range(8):
                angle = i * math.pi / 4
                bx = math.cos(angle)
                by = math.sin(angle)
                proj = Projectile(ex, ey, bx, by, 250, self.damage // 2, (255, 150, 50), 7, 'enemy')
                self.projectiles.append(proj)

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        color = (255, 30, 30) if self.phase == 2 else self.color
        pygame.draw.rect(surface, color, (sx, sy, self.size, self.size))
        pygame.draw.rect(surface, (255, 200, 200), (sx, sy, self.size, self.size), 3)
        bar_w = self.size
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (150, 20, 20), (sx, sy - 10, bar_w, 7))
        pygame.draw.rect(surface, (50, 220, 50), (sx, sy - 10, int(bar_w * ratio), 7))
        label = pygame.font.SysFont('Arial', 11).render('BOSS', True, (255, 255, 0))
        surface.blit(label, (sx + self.size//2 - label.get_width()//2, sy - 22))
        for p in self.projectiles:
            p.draw(surface, camera_x, camera_y)