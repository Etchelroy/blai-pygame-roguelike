import pygame
import math
import random
from projectiles import Projectile

class Enemy:
    def __init__(self, x, y, enemy_type="melee"):
        self.x = x
        self.y = y
        self.radius = 6
        self.enemy_type = enemy_type
        self.health = 20
        self.speed = 100
        self.damage = 10
        self.color = (255, 100, 100)
        
        if enemy_type == "ranged":
            self.speed = 80
            self.health = 15
            self.color = (255, 150, 100)
            self.shoot_cooldown = 1.0
            self.shoot_timer = 0
        elif enemy_type == "boss":
            self.speed = 60
            self.health = 100
            self.radius = 12
            self.color = (255, 50, 50)
            self.damage = 20
    
    def update(self, delta_time, player, dungeon):
        """Update enemy movement"""
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        
        new_x = self.x + dx * self.speed * delta_time
        new_y = self.y + dy * self.speed * delta_time
        
        if not dungeon.collides_with_walls(new_x, new_y, self.radius):
            self.x = new_x
            self.y = new_y
        
        if self.enemy_type == "ranged":
            self.shoot_timer -= delta_time
    
    def take_damage(self, amount):
        """Reduce health"""
        self.health -= amount
    
    def shoot(self, player):
        """Ranged enemy shoots at player"""
        if self.shoot_timer > 0 or self.enemy_type != "ranged":
            return None
        
        self.shoot_timer = 1.0
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        
        speed = 250
        return Projectile(self.x + dx * 10, self.y + dy * 10, 
                         dx * speed, dy * speed, self.damage, hostile=True)
    
    def render(self, surface):
        """Draw enemy"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Health bar
        bar_width = 12
        bar_height = 2
        health_ratio = self.health / 20 if self.enemy_type != "boss" else self.health / 100
        pygame.draw.rect(surface, (100, 100, 100), 
                        (int(self.x - bar_width/2), int(self.y - self.radius - 5), bar_width, bar_height))
        pygame.draw.rect(surface, (100, 255, 100), 
                        (int(self.x - bar_width/2), int(self.y - self.radius - 5), 
                         bar_width * health_ratio, bar_height))

class EnemyManager:
    def __init__(self):
        self.enemies = []
    
    def spawn_random(self, width, height, dungeon):
        """Spawn random enemy"""
        while True:
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            if not dungeon.collides_with_walls(x, y, 10):
                break
        
        enemy_type = random.choices(["melee", "ranged"], weights=[70, 30])[0]
        self.enemies.append(Enemy(x, y, enemy_type))
    
    def update(self, delta_time, player, projectile_manager, dungeon):
        """Update all enemies"""
        for enemy in self.enemies:
            enemy.update(delta_time, player, dungeon)
            
            if enemy.enemy_type == "ranged":
                proj = enemy.shoot(player)
                if proj:
                    projectile_manager.add(proj)
    
    def remove(self, enemy):
        """Remove enemy"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
    
    def render(self, surface):
        """Render all enemies"""
        for enemy in self.enemies:
            enemy.render(surface)