import pygame
import sys
import math
import time
from dungeon import Dungeon, TILE_WALL, TILE_FLOOR, TILE_DOOR
from player import Player
from enemies import MeleeEnemy, RangedEnemy, BossEnemy
from items import Item
from ui import UI

SCREEN_W, SCREEN_H = 1280, 720
VIEWPORT_W, VIEWPORT_H = 960, 720
PANEL_W = 320
FPS = 60
TILE = 32

STATE_MENU = "menu"
STATE_GAME = "game"
STATE_DEATH = "death"
STATE_LEVELUP = "levelup"

def world_to_screen(wx, wy, cam_x, cam_y):
    return int(wx - cam_x + VIEWPORT_W // 2), int(wy - cam_y + VIEWPORT_H // 2)

def screen_to_world(sx, sy, cam_x, cam_y):
    return sx + cam_x - VIEWPORT_W // 2, sy + cam_y - VIEWPORT_H // 2

def rect_collide_tiles(rect, dungeon):
    tile_x0 = int(rect.left // TILE)
    tile_x1 = int(rect.right // TILE)
    tile_y0 = int(rect.top // TILE)
    tile_y1 = int(rect.bottom // TILE)
    for ty in range(tile_y0, tile_y1 + 1):
        for tx in range(tile_x0, tile_x1 + 1):
            tile = dungeon.get_tile(tx, ty)
            if tile == TILE_WALL:
                return True
    return False

def move_entity_with_collision(entity, dx, dy, dungeon):
    entity.rect.x += dx
    if rect_collide_tiles(entity.rect, dungeon):
        entity.rect.x -= dx
    entity.rect.y += dy
    if rect_collide_tiles(entity.rect, dungeon):
        entity.rect.y -= dy

def spawn_enemies_for_room(room, floor_num):
    enemies = []
    cx = (room['x'] + room['w'] // 2) * TILE
    cy = (room['y'] + room['h'] // 2) * TILE
    count_melee = 2 + floor_num
    count_ranged = 1 + floor_num // 2
    import random
    for i in range(count_melee):
        ex = room['x'] * TILE + random.randint(1, room['w'] - 2) * TILE
        ey = room['y'] * TILE + random.randint(1, room['h'] - 2) * TILE
        enemies.append(MeleeEnemy(ex, ey))
    for i in range(count_ranged):
        ex = room['x'] * TILE + random.randint(1, room['w'] - 2) * TILE
        ey = room['y'] * TILE + random.randint(1, room['h'] - 2) * TILE
        enemies.append(RangedEnemy(ex, ey))
    return enemies

def spawn_boss_for_room(room):
    cx = (room['x'] + room['w'] // 2) * TILE
    cy = (room['y'] + room['h'] // 2) * TILE
    return [BossEnemy(cx, cy)]

def spawn_item_in_room(room):
    import random
    ix = room['x'] * TILE + random.randint(1, room['w'] - 2) * TILE + TILE // 2
    iy = room['y'] * TILE + random.randint(1, room['h'] - 2) * TILE + TILE // 2
    kind = random.choice(['health', 'damage', 'speed'])
    return Item(ix, iy, kind)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Darkstone Roguelike")
        self.clock = pygame.time.Clock()
        self.state = STATE_MENU
        self.ui = UI(SCREEN_W, SCREEN_H, VIEWPORT_W, PANEL_W, TILE)
        self.reset()

    def reset(self):
        self.floor_num = 1
        self.enemies_killed = 0
        self.start_time = time.time()
        self.projectiles = []
        self.enemy_projectiles = []
        self.items = []
        self.load_floor()

    def load_floor(self):
        self.dungeon = Dungeon(80, 60, self.floor_num)
        self.dungeon.generate()
        sr = self.dungeon.rooms[0]
        px = (sr['x'] + sr['w'] // 2) * TILE
        py = (sr['y'] + sr['h'] // 2) * TILE
        if not hasattr(self, 'player') or self.player is None:
            self.player = Player(px, py)
        else:
            self.player.rect.centerx = px
            self.player.rect.centery = py
        self.projectiles = []
        self.enemy_projectiles = []
        self.items = []
        self.room_enemies = {}
        self.room_cleared = {}
        self.room_items_spawned = {}
        boss_room_idx = len(self.dungeon.rooms) - 1
        for i, room in enumerate(self.dungeon.rooms):
            if i == 0:
                self.room_cleared[i] = True
                self.room_enemies[i] = []
                continue
            if i == boss_room_idx:
                self.room_enemies[i] = spawn_boss_for_room(room)
            else:
                self.room_enemies[i] = spawn_enemies_for_room(room, self.floor_num)
            self.room_cleared[i] = False
            self.room_items_spawned[i] = False
        self.current_room_idx = 0
        self.all_enemies = []
        for enlist in self.room_enemies.values():
            self.all_enemies.extend(enlist)
        self.cam_x = float(px)
        self.cam_y = float(py)
        self.damage_flash = 0
        self.level_up_pending = False

    def get_current_room(self):
        px, py = self.player.rect.centerx, self.player.rect.centery
        for i, room in enumerate(self.dungeon.rooms):
            rx = room['x'] * TILE
            ry = room['y'] * TILE
            rw = room['w'] * TILE
            rh = room['h'] * TILE
            if rx <= px <= rx + rw and ry <= py <= ry + rh:
                return i
        return self.current_room_idx

    def check_room_cleared(self, room_idx):
        enemies = self.room_enemies.get(room_idx, [])
        alive = [e for e in enemies if e.alive]
        return len(alive) == 0

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(event)
            self.update(dt)
            self.draw()

    def handle_event(self, event):
        if self.state == STATE_MENU:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = STATE_GAME
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                btn = self.ui.get_menu_button()
                if btn and btn.collidepoint(mx, my):
                    self.reset()
                    self.state = STATE_GAME
        elif self.state == STATE_DEATH:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.player = None
                self.reset()
                self.state = STATE_MENU
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                btn = self.ui.get_death_button()
                if btn and btn.collidepoint(mx, my):
                    self.player = None
                    self.reset()
                    self.state = STATE_MENU
        elif self.state == STATE_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if mx < VIEWPORT_W:
                    wpos = screen_to_world(mx, my, self.cam_x, self.cam_y)
                    proj = self.player.shoot(wpos)
                    if proj:
                        self.projectiles.append(proj)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                mx, my = pygame.mouse.get_pos()
                wpos = screen_to_world(mx, my, self.cam_x, self.cam_y)
                self.player.dash(wpos)

    def update(self, dt):
        if self.state != STATE_GAME:
            return
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        spd = self.player.speed * dt
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= spd
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += spd
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= spd
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += spd
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.player.update(dt)
        move_entity_with_collision(self.player, int(dx), int(dy), self.dungeon)

        self.cam_x += (self.player.rect.centerx - self.cam_x) * 8 * dt
        self.cam_y += (self.player.rect.centery - self.cam_y) * 8 * dt

        self.current_room_idx = self.get_current_room()
        room_idx = self.current_room_idx
        active_enemies = self.room_enemies.get(room_idx, [])

        for e in active_enemies:
            if not e.alive:
                continue
            e.update(dt, self.player, self.dungeon, self.enemy_projectiles)
            move_entity_with_collision(e, int(e.vx * dt), int(e.vy * dt), self.dungeon)

        if not self.room_cleared.get(room_idx, True):
            if self.check_room_cleared(room_idx):
                self.room_cleared[room_idx] = True
                if not self.room_items_spawned.get(room_idx, False):
                    room = self.dungeon.rooms[room_idx]
                    self.items.append(spawn_item_in_room(room))
                    self.room_items_spawned[room_idx] = True
                if all(self.room_cleared.values()):
                    self.advance_floor()
                    return

        for proj in self.projectiles[:]:
            proj['x'] += proj['vx'] * dt
            proj['y'] += proj['vy'] * dt
            proj['life'] -= dt
            tx, ty = int(proj['x'] // TILE), int(proj['y'] // TILE)
            if self.dungeon.get_tile(tx, ty) == TILE_WALL or proj['life'] <= 0:
                self.projectiles.remove(proj)
                continue
            hit = False
            for e in active_enemies:
                if not e.alive:
                    continue
                if e.rect.collidepoint(proj['x'], proj['y']):
                    e.take_damage(self.player.damage)
                    if not e.alive:
                        self.enemies_killed += 1
                    self.projectiles.remove(proj)
                    hit = True
                    break
            if hit:
                continue

        for proj in self.enemy_projectiles[:]:
            proj['x'] += proj['vx'] * dt
            proj['y'] += proj['vy'] * dt
            proj['life'] -= dt
            tx, ty = int(proj['x'] // TILE), int(proj['y'] // TILE)
            if self.dungeon.get_tile(tx, ty) == TILE_WALL or proj['life'] <= 0:
                self.enemy_projectiles.remove(proj)
                continue
            if self.player.rect.collidepoint(proj['x'], proj['y']):
                self.player.take_damage(proj.get('dmg', 10))
                self.damage_flash = 0.2
                self.enemy_projectiles.remove(proj)
                continue

        for e in active_enemies:
            if e.alive and e.rect.colliderect(self.player.rect):
                if hasattr(e, 'melee_timer') and e.melee_timer <= 0:
                    self.player.take_damage(e.damage)
                    self.damage_flash = 0.2
                    e.melee_timer = e.melee_cd

        for item in self.items[:]:
            if not item.collected and self.player.rect.collidepoint(item.x, item.y):
                item.apply(self.player)
                self.items.remove(item)

        if self.damage_flash > 0:
            self.damage_flash -= dt

        if not self.player.alive:
            self.state = STATE_DEATH

    def advance_floor(self):
        self.floor_num += 1
        self.load_floor()

    def draw(self):
        self.screen.fill((10, 10, 20))
        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen)
        elif self.state == STATE_DEATH:
            elapsed = time.time() - self.start_time
            self.ui.draw_death(self.screen, self.floor_num - 1, self.enemies_killed, elapsed)
        elif self.state == STATE_GAME:
            self.draw_game()
        pygame.display.flip()

    def draw_game(self):
        surf = self.screen
        cam_x, cam_y = self.cam_x, self.cam_y

        # Dungeon tiles
        tile_x0 = max(0, int((cam_x - VIEWPORT_W // 2) // TILE) - 1)
        tile_y0 = max(0, int((cam_y - VIEWPORT_H // 2) // TILE) - 1)
        tile_x1 = min(self.dungeon.width, tile_x0 + VIEWPORT_W // TILE + 3)
        tile_y1 = min(self.dungeon.height, tile_y0 + VIEWPORT_H // TILE + 3)

        for ty in range(tile_y0, tile_y1):
            for tx in range(tile_x0, tile_x1):
                tile = self.dungeon.get_tile(tx, ty)
                sx, sy = world_to_screen(tx * TILE, ty * TILE, cam_x, cam_y)
                if sx > VIEWPORT_W or sy > VIEWPORT_H or sx < -TILE or sy < -TILE:
                    continue
                if tile == TILE_WALL:
                    pygame.draw.rect(surf, (60, 50, 80), (sx, sy, TILE, TILE))
                    pygame.draw.rect(surf, (40, 30, 55), (sx, sy, TILE, TILE), 1)
                elif tile == TILE_FLOOR:
                    pygame.draw.rect(surf, (30, 25, 40), (sx, sy, TILE, TILE))
                    pygame.draw.rect(surf, (35, 30, 45), (sx, sy, TILE, TILE), 1)
                elif tile == TILE_DOOR:
                    col = (180, 140, 60) if self.room_cleared.get(self.current_room_idx, False) else (100, 60, 20)
                    pygame.draw.rect(surf, col, (sx, sy, TILE, TILE))

        # Items
        for item in self.items:
            sx, sy = world_to_screen(item.x, item.y, cam_x, cam_y)
            item.draw(surf, sx, sy)

        # Player
        px, py = world_to_screen(self.player.rect.centerx, self.player.rect.centery, cam_x, cam_y)
        self.player.draw(surf, px, py)

        # Enemies
        room_idx = self.current_room_idx
        for e in self.room_enemies.get(room_idx, []):
            if not e.alive:
                continue
            ex, ey = world_to_screen(e.rect.centerx, e.rect.centery, cam_x, cam_y)
            if 0 <= ex <= VIEWPORT_W and 0 <= ey <= VIEWPORT_H:
                e.draw(surf, ex, ey)

        # Player projectiles
        for proj in self.projectiles:
            sx, sy = world_to_screen(proj['x'], proj['y'], cam_x, cam_y)
            pygame.draw.circle(surf, (255, 220, 50), (int(sx), int(sy)), 5)

        # Enemy projectiles
        for proj in self.enemy_projectiles:
            sx, sy = world_to_screen(proj['x'], proj['y'], cam_x, cam_y)
            pygame.draw.circle(surf, (255, 60, 60), (int(sx), int(sy)), 4)

        # Damage flash overlay
        if self.damage_flash > 0:
            flash_surf = pygame.Surface((VIEWPORT_W, VIEWPORT_H), pygame.SRCALPHA)
            alpha = int(min(self.damage_flash / 0.2, 1.0) * 80)
            flash_surf.fill((200, 0, 0, alpha))
            surf.blit(flash_surf, (0, 0))

        # Viewport border
        pygame.draw.rect(surf, (80, 70, 100), (0, 0, VIEWPORT_W, VIEWPORT_H), 2)

        # Right panel
        elapsed = time.time() - self.start_time
        room_idx = self.current_room_idx
        total_rooms = len(self.dungeon.rooms)
        cleared = sum(1 for v in self.room_cleared.values() if v)
        self.ui.draw_panel(surf, self.player, self.floor_num, self.enemies_killed, elapsed,
                           self.dungeon, cam_x, cam_y, room_idx, cleared, total_rooms)

if __name__ == '__main__':
    game = Game()
    game.run()