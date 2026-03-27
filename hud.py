import pygame

class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.w = screen.get_width()
        self.h = screen.get_height()

    def draw(self, player, floors_cleared, enemies_killed, elapsed):
        self._draw_health_bar(player)
        self._draw_stats(player, floors_cleared, enemies_killed, elapsed)
        self._draw_dash_indicator(player)

    def _draw_health_bar(self, player):
        bar_w = 220
        bar_h = 22
        x, y = 20, self.h - 40
        pygame.draw.rect(self.screen, (60, 0, 0), (x, y, bar_w, bar_h), border_radius=4)
        ratio = max(0, player.health / player.max_health)
        fill = int(bar_w * ratio)
        r = max(0, int(220 * (1 - ratio)))
        g = max(0, int(200 * ratio))
        if fill > 0:
            pygame.draw.rect(self.screen, (r, g, 40), (x, y, fill, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, bar_w, bar_h), 2, border_radius=4)
        hp_text = self.font_small.render(f"HP: {player.health}/{player.max_health}", True, (255, 255, 255))
        self.screen.blit(hp_text, (x + 6, y + 3))

    def _draw_stats(self, player, floors_cleared, enemies_killed, elapsed):
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        lines = [
            f"Floor: {floors_cleared}",
            f"Kills: {enemies_killed}",
            f"Time: {minutes:02d}:{seconds:02d}",
            f"DMG: {player.damage}",
        ]
        for i, line in enumerate(lines):
            surf = self.font_small.render(line, True, (220, 220, 220))
            self.screen.blit(surf, (20, 16 + i * 22))

    def _draw_dash_indicator(self, player):
        x = 260
        y = self.h - 40
        w = 90
        h = 22
        pygame.draw.rect(self.screen, (20, 20, 60), (x, y, w, h), border_radius=4)
        if player.dash_cd_timer <= 0:
            pygame.draw.rect(self.screen, (80, 180, 255), (x, y, w, h), border_radius=4)
            label = self.font_small.render("DASH RDY", True, (0, 0, 0))
        else:
            ratio = 1.0 - (player.dash_cd_timer / player.dash_cooldown)
            pygame.draw.rect(self.screen, (40, 80, 160), (x, y, int(w * ratio), h), border_radius=4)
            label = self.font_small.render("DASH", True, (150, 150, 255))
        pygame.draw.rect(self.screen, (100, 140, 220), (x, y, w, h), 2, border_radius=4)
        self.screen.blit(label, label.get_rect(center=(x + w // 2, y + h // 2)))