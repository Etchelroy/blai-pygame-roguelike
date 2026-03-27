import pygame
import math
import random

TILE_SIZE = 32

class BaseEnemy:
    def __init__(self, x, y, hp, speed, damage, xp_value, color, floor):
        self.x = float(x)
        self.y = float(y)
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.damage = damage
        self.xp_value = xp_value
        self.color = color
        self.w = 24
        self.h = 24
        self.floor = floor
        self.attack_cooldown = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w // 2), int(self.y - self.h // 2), self.w, self.h)

    def take_damage(self, amount):
        self.hp -= amount

    def _move_towards(self, tx, ty, dt, collision):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 2:
            return
        dx /= dist
        dy /= dist
        new_x = self.x + dx * self.speed * dt
        new_y = self.y + dy * self.speed * dt
        # X move
        self.x = new_x
        if collision.collides_with_wall(self.rect):
            self.x -= dx * self.speed * dt
        # Y move
        self.y = new_y
        if collision.collides_with_wall(self.rect):
            self.y -= dy * self.speed * dt

    def _draw_health_bar(self, screen, sx, sy):
        bar_w = 30
        bar_h = 4
        bx = sx - bar_w // 2
        by = sy - 20
        pygame.draw.rect(screen, (80, 0, 0), (bx, by, bar_w, bar_h))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, (200, 50, 50), (bx, by, int(bar_w * ratio), bar_h))

class MeleeEnemy(BaseEnemy):
    def __init__(self, x, y, floor=1):
        hp = 40 + floor * 10
        speed = 90 + floor * 5
        damage = 10 + floor * 2
        super().__init__(x, y, hp, speed, damage, 10 + floor * 2, (200, 60, 60), floor)
        self.melee_timer = 0.0
        self.melee_rate = 0.8

    def update(self, dt, player, proj_manager, collision):
        self.melee_timer -= dt
        dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if dist > 30:
            self._move_towards(player.x, player.y, dt, collision)

    def melee_attack(self, player, dt):
        if self.melee_timer <= 0:
            player.take_damage(self.damage)
            self.melee_timer = self.melee_rate

    def render(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        pygame.draw.rect(screen, self.color, (sx - 12, sy - 12, 24, 24))
        pygame.draw.rect(screen, (255, 100, 100), (sx - 12, sy - 12, 24, 24), 2)
        self._draw_health_bar(screen, sx, sy)

class RangedEnemy(BaseEnemy):
    def __init__(self, x, y, floor=1):
        hp = 25 + floor * 8
        speed = 70 + floor * 4
        damage = 8 + floor * 2
        super().__init__(x, y, hp, speed, damage, 15 + floor * 2, (100, 60, 200), floor)
        self.shoot_cooldown = 0.0
        self.shoot_rate = 2.0
        self.preferred_dist = 200

    def update(self, dt, player, proj_manager, collision):
        self.shoot_cooldown -= dt
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.preferred_dist - 30:
            # move away
            if dist > 0:
                self.x -= (dx / dist) * self.speed * dt
                self.y -= (dy / dist) * self.speed * dt
        elif dist > self.preferred_dist + 30:
            self._move_towards(player.x, player.y, dt, collision)

        if self.shoot_cooldown <= 0 and dist < 350:
            if dist > 0:
                ndx = dx / dist
                ndy = dy / dist
                proj_manager.spawn_enemy_projectile(self.x, self.y, ndx, ndy, self.damage)
                self.shoot_cooldown = self.shoot_rate

    def render(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        points = [
            (sx, sy - 14),
            (sx + 12, sy + 10),
            (sx - 12, sy + 10),
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (180, 130, 255), points, 2)
        self._draw_health_bar(screen, sx, sy)

class BossEnemy(BaseEnemy):
    def __init__(self, x, y, floor=1):
        hp = 200 + floor * 40
        speed = 60 + floor * 3
        damage = 20 + floor * 5
        super().__init__(x, y, hp, speed, damage, 80 + floor * 20, (200, 150, 30), floor)
        self.shoot_cooldown = 0.0
        self.shoot_rate = 1.0
        self.phase = 1
        self.melee_timer = 0.0
        self.melee_rate = 1.2
        self.w = 40
        self.h = 40

    def update(self, dt, player, proj_manager, collision):
        self.shoot_cooldown -= dt
        self.melee_timer -= dt

        if self.hp < self.max_hp * 0.5:
            self.phase = 2

        dist = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)

        if dist > 60:
            self._move_towards(player.x, player.y, dt, collision)

        if self.shoot_cooldown <= 0 and dist < 450:
            dx = player.x - self.x
            dy = player.y - self.y
            d = math.sqrt(dx * dx + dy * dy)
            if d > 0:
                proj_manager.spawn_enemy_projectile(self.x, self.y, dx / d, dy / d, self.damage)
                if self.phase == 2:
                    angle = math.pi / 8
                    for a in [-angle, angle]:
                        ca = math.cos(a)
                        sa = math.sin(a)
                        ndx = ca * (dx / d) - sa * (dy / d)
                        ndy = sa * (dx / d) + ca * (dy / d)
                        proj_manager.spawn_enemy_projectile(self.x, self.y, ndx, ndy, self.damage * 0.7)
            self.shoot_cooldown = self.shoot_rate if self.phase == 1 else 0.6

    def melee_attack(self, player, dt):
        if self.melee_timer <= 0:
            player.take_damage(self.damage)
            self.melee_timer = self.melee_rate

    def render(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        pygame.draw.rect(screen, self.color, (sx - 20, sy - 20, 40, 40))
        pygame.draw.rect(screen, (255, 220, 80), (sx - 20, sy - 20, 40, 40), 3)
        # crown
        points = [
            (sx - 18, sy - 20),
            (sx - 14, sy - 28),
            (sx - 10, sy - 22),
            (sx, sy - 30),
            (sx + 10, sy - 22),
            (sx + 14, sy - 28),
            (sx + 18, sy - 20),
        ]
        pygame.draw.lines(screen, (255, 220, 80), False, points, 2)
        # health bar (wider for boss)
        bar_w = 50
        bx = sx - bar_w // 2
        by = sy - 30
        pygame.draw.rect(screen, (80, 0, 0), (bx, by, bar_w, 6))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, (220, 180, 30), (bx, by, int(bar_w * ratio), 6))
        # phase indicator
        if self.phase == 2:
            pygame.draw.circle(screen, (255, 80, 0), (sx, sy), 22, 2)