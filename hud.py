import pygame

class HUD:
    def __init__(self, screen, player, dungeon):
        self.screen = screen
        self.player = player
        self.dungeon = dungeon
        self.font_large = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 13)
        self.message_log = []

        # Panel background
        self.panel_rect = pygame.Rect(960, 0, 320, 720)

        # Minimap
        self.minimap_rect = pygame.Rect(960, 80, 320, 280)
        self.minimap_scale = 4

    def update(self, message_log):
        self.message_log = message_log

    def render(self):
        # Right panel background
        pygame.draw.rect(self.screen, (20, 18, 28), self.panel_rect)
        pygame.draw.line(self.screen, (80, 60, 100), (960, 0), (960, 720), 2)

        self._draw_stats()
        self._draw_minimap()
        self._draw_log()

    def _draw_stats(self):
        p = self.player
        font = self.font_large
        small = self.font_small
        x, y = 968, 8

        # Title
        title = font.render(f"FLOOR {self.dungeon.floor_num}", True, (200, 180, 255))
        self.screen.blit(title, (x, y))
        y += 24

        # HP bar
        self.screen.blit(small.render("HP", True, (255, 100, 100)), (x, y))
        self._draw_bar(x + 30, y + 2, 240, 14, p.hp, p.max_hp, (200, 50, 50), (100, 200, 100))
        hp_text = small.render(f"{p.hp}/{p.max_hp}", True, (255, 200, 200))
        self.screen.blit(hp_text, (x + 275, y))
        y += 20

        # Mana bar
        self.screen.blit(small.render("MP", True, (100, 150, 255)), (x, y))
        self._draw_bar(x + 30, y + 2, 240, 14, p.mana, p.max_mana, (30, 30, 120), (60, 100, 220))
        mp_text = small.render(f"{p.mana}/{p.max_mana}", True, (180, 200, 255))
        self.screen.blit(mp_text, (x + 275, y))
        y += 20

        # XP bar
        self.screen.blit(small.render("XP", True, (200, 200, 50)), (x, y))
        self._draw_bar(x + 30, y + 2, 240, 8, p.xp, p.xp_to_next, (40, 40, 10), (200, 200, 50))
        y += 16

        # Stats text
        stats = [
            f"Level: {p.level}",
            f"DMG:   {p.damage}",
            f"SPD:   {int(p.speed)}",
        ]
        for s in stats:
            surf = small.render(s, True, (200, 200, 220))
            self.screen.blit(surf, (x, y))
            y += 14

        # Boost indicators
        if p.speed_boost_timer > 0:
            surf = small.render(f"SPEED BOOST: {p.speed_boost_timer:.1f}s", True, (60, 220, 120))
            self.screen.blit(surf, (x, y))
            y += 14
        if p.damage_boost_timer > 0:
            surf = small.render(f"DMG BOOST: {p.damage_boost_timer:.1f}s", True, (255, 140, 0))
            self.screen.blit(surf, (x, y))
            y += 14

        # Dash cooldown
        if p.dash_cooldown > 0:
            surf = small.render(f"DASH CD: {p.dash_cooldown:.1f}s", True, (150, 150, 255))
            self.screen.blit(surf, (x, y))

    def _draw_bar(self, x, y, w, h, val, max_val, bg_color, fill_color):
        pygame.draw.rect(self.screen, bg_color, (x, y, w, h))
        if max_val > 0:
            ratio = max(0.0, min(1.0, val / max_val))
            pygame.draw.rect(self.screen, fill_color, (x, y, int(w * ratio), h))
        pygame.draw.rect(self.screen, (100, 100, 120), (x, y, w, h), 1)

    def _draw_minimap(self):
        pygame.draw.rect(self.screen, (15, 12, 20), self.minimap_rect)
        pygame.draw.rect(self.screen, (80, 60, 100), self.minimap_rect, 1)

        font = self.font_small
        self.screen.blit(font.render("MINIMAP", True, (150, 130, 180)),
                         (self.minimap_rect.x + 4, self.minimap_rect.y + 4))

        dungeon = self.dungeon
        scale = 3
        ox = self.minimap_rect.x + 4
        oy = self.minimap_rect.y + 20

        max_w = self.minimap_rect.width - 8
        max_h = self.minimap_rect.height - 24

        for ty in range(dungeon.height):
            for tx in range(dungeon.width):
                px = ox + tx * scale
                py = oy + ty * scale
                if px > ox + max_w or py > oy + max_h:
                    continue
                if dungeon.tiles[ty][tx] == 0:  # FLOOR
                    pygame.draw.rect(self.screen, (80, 70, 90), (px, py, scale, scale))

        # Draw player on minimap
        px = int(self.player.x // 32)
        py = int(self.player.y // 32)
        dot_x = ox + px * scale
        dot_y = oy + py * scale
        pygame.draw.rect(self.screen, (80, 160, 255), (dot_x - 1, dot_y - 1, 4, 4))

    
Looking at the failing QA criteria, I need to implement complete versions of all files with proper controls, delta-time, collision, items, death screen, and all enemy types.

```python
# filename: main.py
import pygame
import sys
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Roguelike Dungeon")
    clock = pygame.time.Clock()
    game = Game(screen)
    
    while True:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        game.handle_events(events)
        game.update(dt)
        game.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()