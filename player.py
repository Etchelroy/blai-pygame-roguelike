import pygame
import math

TILE_SIZE = 32

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.w = 24
        self.h = 24
        self.speed = 180.0
        self.base_speed = 180.0
        self.hp = 100
        self.max_hp = 100
        self.mana = 80
        self.max_mana = 80
        self.damage = 20
        self.base_damage = 20
        self.xp = 0
        self.xp_to_next = 50
        self.level = 1
        self.level_up_ready = False

        self.dash_cooldown = 0.0
        self.dash_duration = 0.0
        self.dash_dx = 0.0
        self.dash_dy = 0.0
        self.dash_speed = 500.0
        self.dash_max_duration = 0.18
        self.dash_max_cooldown = 1.0
        self.is_dashing = False

        self.shoot_cooldown = 0.0
        self.shoot_rate = 0.25

        self.facing_angle = 0.0

        self.speed_boost_timer = 0.0
        self.damage_boost_timer = 0.0

        self.invincible_timer = 0.0

        self.color = (80, 160, 255)

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w // 2), int(self.y - self.h // 2), self.w, self.h)

    def update(self, dt, keys, collision):
        # timers
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed = self.base_speed
        if self.damage_boost_timer > 0:
            self.damage_boost_timer -= dt
            if self.damage_boost_timer <= 0:
                self.damage = self.base_damage

        # dash movement
        if self.is_dashing:
            self.dash_duration -= dt
            if self.dash_duration <= 0:
                self.is_dashing = False
            else:
                dx = self.dash_dx * self.dash_speed * dt
                dy = self.dash_dy * self.dash_speed * dt
                self._move(dx, dy, collision)
                return

        # normal movement
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        spd = self.speed
        self._move(dx * spd * dt, dy * spd * dt, collision)

        # face mouse
        mx, my = pygame.mouse.get_pos()
        screen_px = 480
        screen_py = 360
        angle = math.atan2(my - screen_py, mx - screen_px)
        self.facing_angle = angle

    def _move(self, dx, dy, collision):
        # move X
        self.x += dx
        r = self.rect
        if collision.collides_with_wall(r):
            self.x -= dx
        # move Y
        self.y += dy
        r = self.rect
        if collision.collides_with_wall(r):
            self.y -= dy

    def dash(self):
        if self.dash_cooldown <= 0:
            keys = pygame.key.get_pressed()
            dx, dy = 0.0, 0.0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += 1
            length = math.sqrt(dx * dx + dy * dy)
            if length == 0:
                dx = math.cos(self.facing_angle)
                dy = math.sin(self.facing_angle)
            else:
                dx /= length
                dy /= length
            self.dash_dx = dx
            self.dash_dy = dy
            self.is_dashing = True
            self.dash_duration = self.dash_max_duration
            self.dash_cooldown = self.dash_max_cooldown
            self.invincible_timer = self.dash_max_duration

    def shoot(self, world_x, world_y, proj_manager):
        if self.shoot_cooldown <= 0:
            dx = world_x - self.x
            dy = world_y - self.y
            length = math.sqrt(dx * dx + dy * dy)
            if length == 0:
                return
            dx /= length
            dy /= length
            proj_manager.spawn_player_projectile(self.x, self.y, dx, dy, self.damage)
            self.shoot_cooldown = self.shoot_rate

    def take_damage(self, amount):
        if self.invincible_timer > 0:
            return
        self.hp -= amount
        self.hp = max(0, self.hp)
        self.invincible_timer = 0.3

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.xp_to_next = int(self.xp_to_next * 1.5)
            self.level += 1
            self.level_up_ready = True

    def apply_levelup(self, choice):
        if choice == "hp":
            self.max_hp += 20
            self.hp = min(self.hp + 20, self.max_hp)
        elif choice == "damage":
            self.base_damage += 10
            self.damage += 10
        elif choice == "speed":
            self.base_speed += 20
            self.speed = self.base_speed
        elif choice == "mana":
            self.max_mana += 20
            self.mana = min(self.mana + 20, self.max_mana)

    def render(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)

        # body
        pygame.draw.circle(screen, self.color, (sx, sy), 12)
        pygame.draw.circle(screen, (200, 230, 255), (sx, sy), 12, 2)

        # direction indicator
        ex = sx + int(math.cos(self.facing_angle) * 16)
        ey = sy + int(math.sin(self.facing_angle) * 16)
        pygame.draw.line(screen, (255, 255, 100), (sx, sy), (ex, ey), 3)

        # dash indicator
        if self.is_dashing:
            pygame.draw.circle(screen, (100, 200, 255), (sx, sy), 16, 2)