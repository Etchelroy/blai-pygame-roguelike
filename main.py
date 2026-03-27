import pygame
import sys
import math
import time
from dungeon import Dungeon, TILE_WALL, TILE_FLOOR, TILE_DOOR
from player import Player
from enemies import MeleeRusher, RangedShooter, Boss
from items import HealthPickup, DamagePickup, SpeedPickup
from ui import UI

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Dungeon")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Game:
    def __init__(self):
        self.state = "menu"  # menu, playing, death
        self.floor = 1
        self.enemies_killed = 0
        self.time_survived = 0
        self.start_time = 0
        self.dungeon = None
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.items = []
        self.current_room = 0
        self.ui = UI()

    def start_run(self):
        self.state = "playing"
        self.floor = 1
        self.enemies_killed = 0
        self.time_survived = 0
        self.start_time = time.time()
        self.generate_dungeon()

    def generate_dungeon(self):
        self.dungeon = Dungeon(width=80, height=60, num_rooms=6)
        self.current_room = 0
        self.load_room(0)

    def load_room(self, room_idx):
        self.current_room = room_idx
        self.enemies = []
        self.items = []
        self.projectiles = []
        
        room = self.dungeon.rooms[room_idx]
        self.player = Player(room['center'][0] * 10, room['center'][1] * 10)
        
        # Spawn enemies based on room
        enemy_count = 3 + room_idx
        if room_idx == len(self.dungeon.rooms) - 1:
            enemy_count = 1
            self.enemies.append(Boss(room['center'][0] * 10 + 100, room['center'][1] * 10))
        else:
            for i in range(enemy_count):
                angle = (i / enemy_count) * math.pi * 2
                x = room['center'][0] * 10 + math.cos(angle) * 150
                y = room['center'][1] * 10 + math.sin(angle) * 150
                if i % 2 == 0:
                    self.enemies.append(MeleeRusher(x, y))
                else:
                    self.enemies.append(RangedShooter(x, y))

    def next_floor(self):
        self.floor += 1
        self.generate_dungeon()
        self.load_room(0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == "menu" and event.key == pygame.K_SPACE:
                    self.start_run()
                elif self.state == "death" and event.key == pygame.K_SPACE:
                    self.state = "menu"
        return True

    def update(self, dt):
        if self.state == "playing":
            self.time_survived = time.time() - self.start_time
            
            # Update player
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            self.player.update(keys, mouse_pos, dt)
            
            # Player movement collision
            self.player.x = max(0, min(SCREEN_WIDTH - 10, self.player.x))
            self.player.y = max(0, min(SCREEN_HEIGHT - 10, self.player.y))
            
            room = self.dungeon.rooms[self.current_room]
            for tile_y in range(room['y'], room['y'] + room['height']):
                for tile_x in range(room['x'], room['x'] + room['width']):
                    tile = self.dungeon.grid[tile_y][tile_x]
                    if tile == TILE_WALL:
                        wall_rect = pygame.Rect(tile_x * 10, tile_y * 10, 10, 10)
                        player_rect = pygame.Rect(self.player.x - 5, self.player.y - 5, 10, 10)
                        if player_rect.colliderect(wall_rect):
                            if self.player.vx > 0:
                                self.player.x = wall_rect.left - 5
                            elif self.player.vx < 0:
                                self.player.x = wall_rect.right + 5
                            if self.player.vy > 0:
                                self.player.y = wall_rect.top - 5
                            elif self.player.vy < 0:
                                self.player.y = wall_rect.bottom + 5
            
            # Update projectiles
            for proj in self.projectiles[:]:
                proj['x'] += proj['vx'] * dt
                proj['y'] += proj['vy'] * dt
                
                if proj['x'] < 0 or proj['x'] > SCREEN_WIDTH or proj['y'] < 0 or proj['y'] > SCREEN_HEIGHT:
                    self.projectiles.remove(proj)
                    continue
                
                # Collision with enemies
                for enemy in self.enemies[:]:
                    dist = math.sqrt((proj['x'] - enemy.x)**2 + (proj['y'] - enemy.y)**2)
                    if dist < 15:
                        enemy.health -= proj['damage']
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.enemies_killed += 1
                        break
            
            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update(self.player, dt)
                
                # Enemy projectiles
                if hasattr(enemy, 'shoot'):
                    new_projs = enemy.shoot()
                    self.projectiles.extend(new_projs)
            
            # Enemy projectile collisions
            for proj in self.projectiles[:]:
                if proj['owner'] == 'enemy':
                    dist = math.sqrt((proj['x'] - self.player.x)**2 + (proj['y'] - self.player.y)**2)
                    if dist < 10:
                        self.player.health -= proj['damage']
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        if self.player.health <= 0:
                            self.state = "death"
            
            # Check room clear
            if len(self.enemies) == 0:
                # Spawn items
                room = self.dungeon.rooms[self.current_room]
                for i in range(2):
                    x = room['center'][0] * 10 + (i - 0.5) * 80
                    y = room['center'][1] * 10
                    item_type = i % 3
                    if item_type == 0:
                        self.items.append(HealthPickup(x, y))
                    elif item_type == 1:
                        self.items.append(DamagePickup(x, y))
                    else:
                        self.items.append(SpeedPickup(x, y))
            
            # Item pickup
            for item in self.items[:]:
                dist = math.sqrt((item.x - self.player.x)**2 + (item.y - self.player.y)**2)
                if dist < 30:
                    item.apply(self.player)
                    self.items.remove(item)
            
            # Room transition
            if len(self.enemies) == 0 and len(self.items) == 0:
                if self.current_room < len(self.dungeon.rooms) - 1:
                    self.load_room(self.current_room + 1)
                else:
                    self.next_floor()

    def draw(self):
        screen.fill((20, 20, 30))
        
        if self.state == "menu":
            self.ui.draw_menu(screen)
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "death":
            self.ui.draw_death_screen(screen, self.floor, self.enemies_killed, self.time_survived)

    def draw_game(self):
        # Draw dungeon
        room = self.dungeon.rooms[self.current_room]
        for tile_y in range(room['y'], room['y'] + room['height']):
            for tile_x in range(room['x'], room['x'] + room['width']):
                tile = self.dungeon.grid[tile_y][tile_x]
                if tile == TILE_WALL:
                    pygame.draw.rect(screen, (100, 100, 120), (tile_x * 10, tile_y * 10, 10, 10))
                elif tile == TILE_FLOOR:
                    pygame.draw.rect(screen, (40, 40, 50), (tile_x * 10, tile_y * 10, 10, 10))
        
        # Draw items
        for item in self.items:
            pygame.draw.circle(screen, item.color, (int(item.x), int(item.y)), 8)
        
        # Draw projectiles
        for proj in self.projectiles:
            color = (100, 200, 255) if proj['owner'] == 'player' else (255, 100, 100)
            pygame.draw.circle(screen, color, (int(proj['x']), int(proj['y'])), 4)
        
        # Draw enemies
        for enemy in self.enemies:
            color = (200, 50, 50) if isinstance(enemy, MeleeRusher) else (220, 100, 50) if isinstance(enemy, RangedShooter) else (150, 30, 30)
            pygame.draw.circle(screen, color, (int(enemy.x), int(enemy.y)), 8)
            # Health bar
            pygame.draw.rect(screen, (100, 100, 100), (enemy.x - 10, enemy.y - 20, 20, 3))
            pygame.draw.rect(screen, (100, 255, 100), (enemy.x - 10, enemy.y - 20, 20 * (enemy.health / enemy.max_health), 3))
        
        # Draw player
        pygame.draw.circle(screen, (100, 200, 100), (int(self.player.x), int(self.player.y)), 8)
        # Player health bar
        pygame.draw.rect(screen, (100, 100, 100), (20, 20, 200, 10))
        pygame.draw.rect(screen, (100, 255, 100), (20, 20, 200 * (self.player.health / self.player.max_health), 10))
        
        # HUD
        self.ui.draw_hud(screen, self.player, self.floor, int(self.time_survived), len(self.enemies))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            dt = clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()
            pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()