import pygame
import math
import random
from projectiles import Projectile

class BaseEnemy:
    def __init__(self, x, y, radius, health, damage, speed, color):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.color = color
        self.vx = 0.0
        self.vy = 0.0
        self._melee_timer = 0.0
        self.melee_cooldown = 1.0

    def melee_attack_ready(self):
        if self._melee_timer <= 0:
            self._melee_timer = self.melee_cooldown
            return True
        return False

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def move_toward(self, tx, ty, dt):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = 0
            self.vy = 0
        self.x += self.vx * dt
        self.y += self.vy * dt

    def update(self, dt, player, projectiles, walls):
        if self._melee_timer > 0:
            self._melee_timer -= dt

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        bar_w = self.radius * 2
        bar_h = 5
        bx = int(self.x) - self.radius
        by = int(self.y) - self.radius - 10
        pygame.draw.rect(screen, (80, 0, 0), (bx, by, bar_w, bar_h))
        hp_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (0, 200, 0), (bx, by, int(bar_w * hp_ratio), bar_h))


class MeleeEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, radius=20, health=60, damage=15, speed=130, color=(200, 80, 80))

    def update(self, dt, player, projectiles, walls):
        super().update(dt, player, projectiles, walls)
        self.move_toward(player.x, player.y, dt)

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.circle(screen, (240, 120, 120), (int(self.x), int(self.y)), self.radius, 2)


class RangedEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, radius=18, health=40, damage=10, speed=80, color=(150, 80, 200))
        self.shoot_cooldown = 2.0
        self.shoot_timer = random.uniform(0.5, 2.0)
        self.preferred_dist = 250

    def update(self, dt, player, projectiles, walls):
        super().update(dt, player, projectiles, walls)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.preferred_dist - 30:
            if dist > 0:
                self.x -= (dx / dist) * self.speed * dt
                self.y -= (dy / dist) * self.speed * dt
        elif dist > self.preferred_dist + 30:
            self.move_toward(player.x, player.y, dt)
        
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_cooldown
            if dist > 0:
                proj = Projectile(self.x, self.y, dx / dist, dy / dist,
                                  owner="enemy", damage=self.damage, speed=280, color=(220, 80, 220))
                projectiles.append(proj)

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.circle(screen, (190, 120, 240), (int(self.x), int(self.y)), self.radius, 2)


class BossEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, radius=40, health=400, damage=25, speed=70, color=(180, 30, 30))
        self.shoot_cooldown = 1.0
        self.shoot_timer = 1.0
        self.phase = 1
        self.melee_cooldown = 0.8

    def update(self, dt, player, projectiles, walls):
        super().update(dt, player, projectiles, walls)
        
        if self.health < self.max_health * 0.5:
            self.phase = 2
            self.speed = 110
            self.shoot_cooldown = 0.5

        self.move_toward(player.x, player.y, dt)
        
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_cooldown
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                if self.phase == 1:
                    proj = Projectile(self.x, self.y, dx / dist, dy / dist,
                                      owner="enemy", damage=20, speed=320, color=(255, 60, 60))
                    projectiles.append(proj)
                else:
                    spread = [-0.3, 0, 0.3]
                    angle = math.atan2(dy, dx)
                    for off in spread:
                        a = angle + off
                        proj = Projectile(self.x, self.y, math.cos(a), math.sin(a),
                                          owner="enemy", damage=20, speed=320, color=(255, 100, 30))
                        projectiles.append(proj)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 80, 80), (int(self.x), int(self.y)), self.radius, 3)
        bar_w = self.radius * 2
        bar_h = 8
        bx = int(self.x) - self.radius
        by = int(self.y) - self.radius - 14
        pygame.draw.rect(screen, (80, 0, 0), (bx, by, bar_w, bar_h))
        hp_ratio = max(0, self.health / self.max_health)
        color = (200, 0, 0) if self.phase == 2 else (0, 200, 0)
        pygame.draw.rect(screen, color, (bx, by, int(bar_w * hp_ratio), bar_h))
        font = pygame.font.SysFont("Arial", 14)
        label = font.render("BOSS", True, (255, 200, 200))
        screen.blit(label, (bx, by - 16))