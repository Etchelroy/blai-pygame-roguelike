import pygame
from player import Player
from dungeon import Dungeon
from enemies import MeleeEnemy, RangedEnemy, BossEnemy
from items import Item
from collision import check_wall_collision, check_entity_collision
from hud import HUD
import random
import time

STATE_PLAYING = "playing"
STATE_DEATH = "death"
STATE_ITEM_PICKUP = "item_pickup"

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.state = STATE_PLAYING
        self.font_large = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 36)
        self.font_small = pygame.font.SysFont("Arial", 24)
        self.reset()

    def reset(self):
        self.dungeon = Dungeon(self.width, self.height)
        self.player = Player(self.width // 2, self.height // 2)
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.floors_cleared = 0
        self.enemies_killed = 0
        self.start_time = time.time()
        self.hud = HUD(self.screen)
        self.pending_items = []
        self.spawn_enemies()
        self.state = STATE_PLAYING
        self.death_time = 0

    def spawn_enemies(self):
        self.enemies = []
        room = self.dungeon.current_room
        cx, cy = room.center()
        count = 3 + self.floors_cleared * 2
        
        if self.floors_cleared > 0 and self.floors_cleared % 3 == 0:
            boss = BossEnemy(cx, cy - 100)
            self.enemies.append(boss)
            count = max(0, count - 3)
        
        for _ in range(count):
            attempts = 0
            while attempts < 20:
                x = random.randint(room.x + 60, room.x + room.w - 60)
                y = random.randint(room.y + 60, room.y + room.h - 60)
                dx = abs(x - self.player.x)
                dy = abs(y - self.player.y)
                if dx > 150 or dy > 150:
                    if random.random() < 0.4:
                        self.enemies.append(RangedEnemy(x, y))
                    else:
                        self.enemies.append(MeleeEnemy(x, y))
                    break
                attempts += 1

    def spawn_items_between_rooms(self):
        room = self.dungeon.current_room
        cx, cy = room.center()
        count = random.randint(1, 3)
        offsets = [(-80, 0), (80, 0), (0, -80)]
        random.shuffle(offsets)
        item_types = ["health", "damage", "speed"]
        for i in range(min(count, 3)):
            ox, oy = offsets[i]
            itype = random.choice(item_types)
            self.items.append(Item(cx + ox, cy + oy, itype))

    def handle_events(self, events):
        if self.state == STATE_DEATH:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    if event.key == pygame.K_ESCAPE:
                        import sys
                        pygame.quit()
                        sys.exit()
            return

        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    proj = self.player.shoot(mouse_pos)
                    if proj:
                        self.projectiles.append(proj)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.dash()

    def update(self, dt):
        if self.state == STATE_DEATH:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_movement(keys, dt)
        self.player.update(dt)

        room = self.dungeon.current_room
        walls = room.get_walls()
        
        # Wall collision for player
        check_wall_collision(self.player, walls)
        
        # Keep player in room
        self.player.x = max(room.x + self.player.radius, min(room.x + room.w - self.player.radius, self.player.x))
        self.player.y = max(room.y + self.player.radius, min(room.y + room.h - self.player.radius, self.player.y))

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, self.player, self.projectiles, walls)
            check_wall_collision(enemy, walls)
            enemy.x = max(room.x + enemy.radius, min(room.x + room.w - enemy.radius, enemy.x))
            enemy.y = max(room.y + enemy.radius, min(room.y + room.h - enemy.radius, enemy.y))
            
            if check_entity_collision(self.player, enemy):
                if enemy.melee_attack_ready():
                    self.player.take_damage(enemy.damage)

        # Update projectiles
        for proj in self.projectiles[:]:
            proj.update(dt)
            
            hit_wall = False
            for wall in walls:
                if wall.collidepoint(proj.x, proj.y):
                    hit_wall = True
                    break
            
            if hit_wall or proj.is_expired():
                self.projectiles.remove(proj)
                continue
            
            if proj.owner == "player":
                for enemy in self.enemies[:]:
                    if check_entity_collision(proj, enemy):
                        enemy.take_damage(self.player.damage)
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.enemies_killed += 1
                        break
            elif proj.owner == "enemy":
                if check_entity_collision(proj, self.player):
                    self.player.take_damage(proj.damage)
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)

        # Check items
        for item in self.items[:]:
            if check_entity_collision(self.player, item):
                item.apply(self.player)
                self.items.remove(item)

        # Check floor clear
        if len(self.enemies) == 0:
            self.floors_cleared += 1
            self.projectiles.clear()
            self.items.clear()
            self.dungeon.next_room()
            room = self.dungeon.current_room
            cx, cy = room.center()
            self.player.x = cx
            self.player.y = cy
            self.spawn_enemies()
            self.spawn_items_between_rooms()

        # Check death
        if self.player.health <= 0:
            self.state = STATE_DEATH
            self.death_time = time.time()

    def draw(self):
        self.screen.fill((20, 20, 30))
        
        if self.state == STATE_DEATH:
            self.draw_death_screen()
            return

        self.dungeon.draw(self.screen)
        
        for item in self.items:
            item.draw(self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        for proj in self.projectiles:
            proj.draw(self.screen)
        
        self.player.draw(self.screen)
        
        elapsed = time.time() - self.start_time
        self.hud.draw(self.player, self.floors_cleared, self.enemies_killed, elapsed)

    def draw_death_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        elapsed = self.death_time - self.start_time
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        
        title = self.font_large.render("YOU DIED", True, (220, 50, 50))
        self.screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 160)))
        
        stats = [
            f"Floors Cleared: {self.floors_cleared}",
            f"Enemies Killed: {self.enemies_killed}",
            f"Time Survived: {minutes:02d}:{seconds:02d}",
        ]
        
        for i, stat in enumerate(stats):
            surf = self.font_medium.render(stat, True, (220, 220, 220))
            self.screen.blit(surf, surf.get_rect(center=(self.width // 2, self.height // 2 - 60 + i * 50)))
        
        hint = self.font_small.render("Press R to Restart   |   ESC to Quit", True, (160, 160, 160))
        self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height // 2 + 120)))