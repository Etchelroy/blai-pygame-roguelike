import pygame
import math
from projectiles import Projectile

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 200  # pixels per second
        self.health = 100
        self.max_health = 100
        self.angle = 0
        self.damage = 10
        
        # Dash mechanic
        self.dash_speed = 600
        self.dash_duration = 0.15
        self.dash_cooldown = 0.5
        self.dash_remaining = 0
        self.dash_cooldown_remaining = 0
    
    def move(self, dx, dy, delta_time, dungeon):
        """Move player with delta-time and collision detection"""
        new_x = self.x + dx * self.speed * delta_time
        new_y = self.y + dy * self.speed * delta_time
        
        if not dungeon.collides_with_walls(new_x, new_y, self.radius):
            self.x = new_x
            self.y = new_y
        else:
            # Slide along walls
            if not dungeon.collides_with_walls(new_x, self.y, self.radius):
                self.x = new_x
            elif not dungeon.collides_with_walls(self.x, new_y, self.radius):
                self.y = new_y
    
    def attempt_dash(self, delta_time):
        """Handle dash input"""
        if self.dash_cooldown_remaining <= 0 and self.dash_remaining <= 0:
            self.dash_remaining = self.dash_duration
            self.dash_cooldown_remaining = self.dash_cooldown
    
    def update(self, delta_time):
        """Update dash state"""
        if self.dash_remaining > 0:
            self.dash_remaining -= delta_time
        if self.dash_cooldown_remaining > 0:
            self.dash_cooldown_remaining -= delta_time
    
    def shoot(self):
        """Create projectile at player angle"""
        if self.dash_remaining > 0:
            return None  # Can't shoot while dashing
        
        speed = 400
        vx = math.cos(self.angle) * speed
        vy = math.sin(self.angle) * speed
        
        return Projectile(
            self.x + math.cos(self.angle) * 15,
            self.y + math.sin(self.angle) * 15,
            vx, vy, self.damage
        )
    
    def take_damage(self, amount):
        """Reduce health"""
        self.health -= amount
    
    def heal(self, amount):
        """Restore health"""
        self.health = min(self.health + amount, self.max_health)
    
    def boost_damage(self, amount):
        """Increase damage"""
        self.damage += amount
    
    def boost_speed(self, amount):
        """Increase speed"""
        self.speed += amount
    
    def render(self, surface):
        """Draw player"""
        color = (100, 255, 100) if self.dash_remaining <= 0 else (200, 100, 255)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        
        # Draw aiming line
        end_x = self.x + math.cos(self.angle) * 30
        end_y = self.y + math.sin(self.angle) * 30
        pygame.draw.line(surface, (255, 255, 0), (int(self.x), int(self.y)), 
                        (int(end_x), int(end_y)), 2)