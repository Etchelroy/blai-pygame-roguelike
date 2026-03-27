import pygame
import math

TILE = 32

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.max_hp = 100
        self.hp = 100
        self.max_mana = 60
        self.mana = 60
        self.speed = 180
        self.damage = 25
        self.alive = True
        self.shoot_cd = 0
        self.shoot_rate = 0.3
        self.dash_cd = 0
        self.dash_duration = 0
        self.dash_vx = 0
        self.dash_vy = 0
        self.mana_regen_timer = 0
        self.invincible = 0
        self.angle = 0

    def update(self, dt):
        if self.shoot_cd > 0:
            self.shoot_cd -= dt
        if self.dash_cd > 0:
            self.dash_cd -= dt
        if self.dash_duration > 0:
            self.dash_duration -= dt
            self.rect.x += int(self.dash_vx * dt)
            self.rect.y += int(self.dash_vy * dt)
        if self.invincible > 0:
            self.invincible -= dt
        self.mana_regen_timer += dt
        if self.mana_regen_timer >= 0.5:
            self.mana_regen_timer = 0
            self.mana = min(self.max_mana, self.mana + 3)

    def shoot(self, target_world):
        if self.shoot_cd > 0 or self.mana < 5:
            return None
        self.shoot_cd = self.shoot_rate
        self.mana -= 5
        cx, cy = self.rect.centerx, self.rect.centery
        tx, ty = target_world
        dx, dy = tx - cx, ty - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return None
        speed = 400
        return {
            'x': float(cx), 'y': float(cy),
            'vx': dx / dist * speed,
            'vy': dy / dist * speed,
            'life': 2.0
        }

    def dash(self, target_world):
        if self.dash_cd > 0:
            return
        self.dash_cd = 1.5
        self.dash_duration = 0.15
        self.invincible = 0.2
        cx, cy = self.rect.centerx, self.rect.centery
        tx, ty = target_world
        dx, dy = tx - cx, ty - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            dx, dy = 1, 0
            dist = 1
        spd = 600
        self.dash_vx = dx / dist * spd
        self.dash_vy = dy / dist * spd

    def take_damage(self, amount):
        if self.invincible > 0:
            return
        self.hp -= amount
        self.invincible = 0.3
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw(self, surf, sx, sy):
        # Body
        col = (80, 160, 220) if self.dash_duration <= 0 else (180, 220, 255)
        pygame.draw.circle(surf, col, (sx, sy), 12)
        pygame.draw.circle(surf, (200, 230, 255), (sx, sy), 12, 2)
        # Direction indicator
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - sy, mx - sx)
        ex = int(sx + math.cos(angle) * 14)
        ey = int(sy + math.sin(angle) * 14)
        pygame.draw.line(surf, (255, 255, 100), (sx, sy), (ex, ey), 3)
        # HP bar above
        bar_w = 28
        hp_frac = self.hp / self.max_hp
        pygame.draw.rect(surf, (100, 20, 20), (sx - bar_w // 2, sy - 20, bar_w, 5))
        pygame.draw.rect(surf, (50, 200, 50), (sx - bar_w // 2, sy - 20, int(bar_w * hp_frac), 5))