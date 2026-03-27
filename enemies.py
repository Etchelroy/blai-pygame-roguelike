import pygame
import math
import random

TILE = 32

class BaseEnemy:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        self.hp = 40
        self.max_hp = 40
        self.damage = 10
        self.speed = 80
        self.alive = True
        self.vx = 0
        self.vy = 0
        self.melee_timer = 0
        self.melee_cd = 0.8

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def move_towards_player(self, dt, player):
        px, py = player.rect.centerx, player.rect.centery
        ex, ey = self.rect.centerx, self.rect.centery
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        else:
            self.vx = 0
            self.vy = 0

    def draw_hp_bar(self, surf, sx, sy, bar_w=30):
        frac = self.hp / self.max_hp
        pygame.draw.rect(surf, (100, 10, 10), (sx - bar_w // 2, sy - self.rect.h // 2 - 8, bar_w, 4))
        pygame.draw.rect(surf, (200, 40, 40), (sx - bar_w // 2, sy - self.rect.h // 2 - 8, int(bar_w * frac), 4))

    def update(self, dt, player, dungeon, enemy_projectiles):
        pass

class MeleeEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, 22, 22)
        self.hp = 50
        self.max_hp = 50
        self.speed = 110
        self.damage = 12
        self.melee_cd = 0.7
        self.melee_timer = 0

    def update(self, dt, player, dungeon, enemy_projectiles):
        if self.melee_timer > 0:
            self.melee_timer -= dt
        self.move_towards_player(dt, player)

    def draw(self, surf, sx, sy):
        pygame.draw.rect(surf, (200, 60, 60), (sx - 11, sy - 11, 22, 22))
        pygame.draw.rect(surf, (240, 100, 100), (sx - 11, sy - 11, 22, 22), 2)
        self.draw_hp_bar(surf, sx, sy)

class RangedEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)
        self.hp = 35
        self.max_hp = 35
        self.speed = 65
        self.damage = 8
        self.shoot_cd = 0
        self.shoot_rate = 2.0
        self.preferred_dist = 200
        self.melee_cd = 1.2
        self.melee_timer = 0

    def update(self, dt, player, dungeon, enemy_projectiles):
        if self.melee_timer > 0:
            self.melee_timer -= dt
        px, py = player.rect.centerx, player.rect.centery
        ex, ey = self.rect.centerx, self.rect.centery
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)
        if dist < self.preferred_dist - 20:
            if dist > 0:
                self.vx = -dx / dist * self.speed
                self.vy = -dy / dist * self.speed
        elif dist > self.preferred_dist + 20:
            if dist > 0:
                self.vx = dx / dist * self.speed
                self.vy = dy / dist * self.speed
        else:
            self.vx = 0
            self.vy = 0

        self.shoot_cd -= dt
        if self.shoot_cd <= 0 and dist < 350:
            self.shoot_cd = self.shoot_rate
            if dist > 0:
                spd = 220
                enemy_projectiles.append({
                    'x': float(ex), 'y': float(ey),
                    'vx': dx / dist * spd,
                    'vy': dy / dist * spd,
                    'life': 2.5,
                    'dmg': self.damage
                })

    def draw(self, surf, sx, sy):
        pygame.draw.polygon(surf, (180, 80, 200),
            [(sx, sy - 12), (sx + 10, sy + 8), (sx - 10, sy + 8)])
        pygame.draw.polygon(surf, (220, 140, 240),
            [(sx, sy - 12), (sx + 10, sy + 8), (sx - 10, sy + 8)], 2)
        self.draw_hp_bar(surf, sx, sy)

class BossEnemy(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.hp = 300
        self.max_hp = 300
        self.speed = 70
        self.damage = 20
        self.melee_cd = 0.5
        self.melee_timer = 0
        self.shoot_cd = 0
        self.shoot_rate = 1.0
        self.phase = 1
        self.charge_cd = 0
        self.charge_timer = 0
        self.charge_vx = 0
        self.charge_vy = 0

    def update(self, dt, player, dungeon, enemy_projectiles):
        if self.melee_timer > 0:
            self.melee_timer -= dt
        if self.hp < self.max_hp * 0.5:
            self.phase = 2

        px, py = player.rect.centerx, player.rect.centery
        ex, ey = self.rect.centerx, self.rect.centery
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)

        if self.charge_timer > 0:
            self.charge_timer -= dt
            self.vx = self.charge_vx
            self.vy = self.charge_vy
        else:
            self.charge_cd -= dt
            if self.charge_cd <= 0:
                self.charge_cd = 3.0 if self.phase == 1 else 1.8
                self.charge_timer = 0.4
                if dist > 0:
                    spd = 320
                    self.charge_vx = dx / dist * spd
                    self.charge_vy = dy / dist * spd
            else:
                if dist > 0:
                    self.vx = dx / dist * self.speed
                    self.vy = dy / dist * self.speed

        self.shoot_cd -= dt
        rate = self.shoot_rate if self.phase == 1 else 0.5
        if self.shoot_cd <= 0:
            self.shoot_cd = rate
            angles = [0, 60, 120, 180, 240, 300] if self.phase == 2 else [0, 90, 180, 270]
            import math as _math
            base_angle = _math.atan2(dy, dx) if dist > 0 else 0
            for a in angles:
                rad = base_angle + _math.radians(a)
                spd = 160
                enemy_projectiles.append({
                    'x': float(ex), 'y': float(ey),
                    'vx': _math.cos(rad) * spd,
                    'vy': _math.sin(rad) * spd,
                    'life': 3.0,
                    'dmg': 15
                })

    def draw(self, surf, sx, sy):
        color = (220, 40, 40) if self.phase == 1 else (255, 80, 0)
        pygame.draw.rect(surf, color, (sx - 20, sy - 20, 40, 40))
        pygame.draw.rect(surf, (255, 200, 50), (sx - 20, sy - 20, 40, 40), 3)
        # Crown spikes
        for i in range(5):
            spike_x = sx - 16 + i * 8
            pygame.draw.polygon(surf, (255, 200, 50),
                [(spike_x, sy - 20), (spike_x + 4, sy - 28), (spike_x + 8, sy - 20)])
        self.draw_hp_bar(surf, sx, sy, bar_w=50)
        # Boss label
        font = pygame.font.SysFont(None, 18)
        label = font.render("BOSS", True, (255, 200, 50))
        surf.blit(label, (sx - label.get_width() // 2, sy - 38))