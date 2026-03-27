import pygame

class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.time_survived = 0
    
    def update_time(self, delta_time):
        """Update elapsed time"""
        self.time_survived += delta_time
    
    def render(self, surface, player, floor, enemies_killed):
        """Draw HUD"""
        health_text = self.font.render(f"Health: {int(player.health)}/{int(player.max_health)}", True, (100, 255, 100))
        damage_text = self.font.render(f"Damage: {int(player.damage)}", True, (255, 100, 100))
        speed_text = self.font.render(f"Speed: {int(player.speed)}", True, (100, 100, 255))
        floor_text = self.font.render(f"Floor: {floor + 1}", True, (255, 255, 100))
        enemies_text = self.font.render(f"Enemies Killed: {enemies_killed}", True, (255, 255, 255))
        time_text = self.font.render(f"Time: {int(self.time_survived)}s", True, (200, 200, 200))
        
        surface.blit(health_text, (10, 10))
        surface.blit(damage_text, (10, 35))
        surface.blit(speed_text, (10, 60))
        surface.blit(floor_text, (self.width // 2 - 50, 10) if hasattr(self, 'width') else (640, 10))
        surface.blit(enemies_text, (10, surface.get_height() - 60))
        surface.blit(time_text, (10, surface.get_height() - 35))