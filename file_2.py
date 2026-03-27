import pygame
import math
from player import Player
from enemies import EnemyManager
from projectiles import ProjectileManager
from items import ItemManager
from dungeon import Dungeon
from collision import CollisionManager
from hud import HUD
from screens import DeathScreen
from utils import clamp

class Game:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Roguelike Dungeon")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "playing"  # "playing", "death"
        
        self.dungeon = Dungeon(width, height)
        self.player = Player(width // 2, height // 2)
        self.enemy_manager = EnemyManager()
        self.projectile_manager = ProjectileManager()
        self.item_manager = ItemManager()
        self.collision_manager = CollisionManager()
        self.hud = HUD()
        self.death_screen = None
        
        self.floor = 0
        self.enemies_killed = 0
        self.spawn_enemies_for_floor(self.floor)
        
    def spawn_enemies_for_floor(self, floor):
        """Spawn enemies based on floor number"""
        count = 3 + floor * 2
        for _ in range(count):
            self.enemy_manager.spawn_random(self.width, self.height, self.dungeon)
    
    def handle_input(self, delta_time):
        """Handle player input with delta-time"""
        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # WASD movement
        move_x = (keys[pygame.K_d] - keys[pygame.K_a])
        move_y = (keys[pygame.K_s] - keys[pygame.K_w])
        
        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x**2 + move_y**2)
            move_x /= length
            move_y /= length
            self.player.move(move_x, move_y, delta_time, self.dungeon)
        
        # Mouse aim
        dx = mouse_x - self.player.x
        dy = mouse_y - self.player.y
        if dx != 0 or dy != 0:
            self.player.angle = math.atan2(dy, dx)
        
        # Spacebar dash
        if keys[pygame.K_SPACE]:
            self.player.attempt_dash(delta_time)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Shoot projectile
                proj = self.player.shoot()
                if proj:
                    self.projectile_manager.add(proj)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
    
    def update(self, delta_time):
        """Update game state"""
        if self.state == "death":
            return
        
        self.player.update(delta_time)
        self.enemy_manager.update(delta_time, self.player, self.projectile_manager, self.dungeon)
        self.projectile_manager.update(delta_time, self.dungeon)
        self.item_manager.update(delta_time)
        
        # Collision: projectiles vs enemies
        for proj in list(self.projectile_manager.projectiles):
            for enemy in list(self.enemy_manager.enemies):
                if self.collision_manager.circles_overlap(
                    proj.x, proj.y, proj.radius,
                    enemy.x, enemy.y, enemy.radius
                ):
                    enemy.take_damage(proj.damage)
                    self.projectile_manager.remove(proj)
                    if enemy.health <= 0:
                        self.enemies_killed += 1
                        self.item_manager.spawn_item(enemy.x, enemy.y)
                        self.enemy_manager.remove(enemy)
                    break
        
        # Collision: projectiles vs walls
        for proj in list(self.projectile_manager.projectiles):
            if self.dungeon.collides_with_walls(proj.x, proj.y, proj.radius):
                self.projectile_manager.remove(proj)
        
        # Collision: player vs items
        for item in list(self.item_manager.items):
            if self.collision_manager.circles_overlap(
                self.player.x, self.player.y, self.player.radius,
                item.x, item.y, item.radius
            ):
                item.apply(self.player)
                self.item_manager.remove(item)
        
        # Collision: player vs enemies
        for enemy in list(self.enemy_manager.enemies):
            if self.collision_manager.circles_overlap(
                self.player.x, self.player.y, self.player.radius,
                enemy.x, enemy.y, enemy.radius
            ):
                self.player.take_damage(1)
                if self.player.health <= 0:
                    self.state = "death"
                    self.death_screen = DeathScreen(
                        self.floor, self.enemies_killed, 
                        self.hud.time_survived
                    )
        
        # Check floor completion
        if len(self.enemy_manager.enemies) == 0 and self.floor < 10:
            self.floor += 1
            self.spawn_enemies_for_floor(self.floor)
    
    def render(self):
        """Render game"""
        self.screen.fill((20, 20, 30))
        
        if self.state == "playing":
            self.dungeon.render(self.screen)
            self.player.render(self.screen)
            self.enemy_manager.render(self.screen)
            self.projectile_manager.render(self.screen)
            self.item_manager.render(self.screen)
            self.hud.render(self.screen, self.player, self.floor, self.enemies_killed)
        elif self.state == "death":
            self.death_screen.render(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop with delta-time"""
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0  # 60 FPS, delta in seconds
            self.hud.update_time(delta_time)
            
            self.handle_events()
            self.handle_input(delta_time)
            self.update(delta_time)
            self.render()
        
        pygame.quit()