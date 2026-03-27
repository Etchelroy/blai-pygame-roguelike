import pygame

class DeathScreen:
    def __init__(self, floor, enemies_killed, time_survived):
        self.floor = floor
        self.enemies_killed = enemies_killed
        self.time_survived = time_survived
        self.font_large = pygame.font.Font(None, 60)
        self.font_med = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def render(self, surface):
        """Draw death screen"""
        surface.fill((20, 20, 30))
        
        title = self.font_large.render("YOU DIED", True, (255, 100, 100))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 80))
        surface.blit(title, title_rect)
        
        stats = [
            f"Floors Cleared: {self.floor}",
            f"Enemies Killed: {self.enemies_killed}",
            f"Time Survived: {int(self.time_survived)}s"
        ]
        
        y = 200
        for stat in stats:
            text = self.font_med.render(stat, True, (255, 255, 255))
            text_rect = text.get_rect(center=(surface.get_width() // 2, y))
            surface.blit(text, text_rect)
            y += 60
        
        restart = self.font_small.render("Press ESC to exit", True, (200, 200, 200))
        restart_rect = restart.get_rect(center=(surface.get_width() // 2, surface.get_height() - 50))
        surface.blit(restart, restart_rect)