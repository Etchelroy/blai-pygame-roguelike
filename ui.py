import pygame
import math

class UI:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.font_large = pygame.font.SysFont('Arial', 64, bold=True)
        self.font_med = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 20)
        self.font_tiny = pygame.font.SysFont('Arial', 16)
        self.menu_hover = None
        self.tick = 0

    def draw_menu(self, surface):
        self.tick += 1
        surface.fill((8, 8, 18))

        for i in range(40):
            x = (i * 137 + self.tick) % self.sw
            y = (i * 97 + self.tick // 2) % self.sh
            pygame.draw.circle(surface, (20, 20, 40), (x, y), 2)

        title = self.font_large.render("DUNGEON ROGUELIKE", True, (200, 180, 255))
        surface.blit(title, (self.sw//2 - title.get_width()//2, 180))

        sub = self.font_small.render("Survive the depths. Slay the boss. Ascend.", True, (140, 120, 180))
        surface.blit(sub, (self.sw//2 - sub.get_width()//2, 260))

        mouse = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()

        btn_x = self.sw//2 - 120
        btn_y = 340
        btn_w = 240
        btn_h = 56
        hovered = btn_x <= mouse[0] <= btn_x + btn_w and btn_y <= mouse[1] <= btn_y + btn_h
        btn_color = (100, 80, 200) if hovered else (60, 50, 140)
        pygame.draw.rect(surface, btn_color, (btn_x, btn_y, btn_w, btn_h), border_radius=10)
        pygame.draw.rect(surface, (200, 180, 255), (btn_x, btn_y, btn_w, btn_h), 2, border_radius=10)
        btn_text = self.font_med.render("START RUN", True, (255, 255, 255))
        surface.blit(btn_text, (btn_x + btn_w//2 - btn_text.get_width()//2, btn_y + btn_h//2 - btn_text.get_height()//2))

        if hovered and clicks[0]:
            return 'start'

        hints = [
            "WASD - Move  |  Mouse - Aim  |  LMB - Shoot  |  SPACE - Dash",
            "Clear all rooms to advance to the next floor  |  Pick up items between rooms"
        ]
        for i, hint in enumerate(hints):
            t = self.font_tiny.render(hint, True, (100, 100, 130))
            surface.blit(t, (self.sw//2 - t.get_width()//2, 430 + i * 24))

        pygame.display.flip()
        return None

    def draw_hud(self, surface, player, floors, kills, elapsed):
        bar_w = 200
        bar_h = 18
        px, py = 20, 20
        ratio = player.hp / player.max_hp
        pygame.draw.rect(surface, (30, 30, 30), (px, py, bar_w, bar_h), border_radius=4)
        hp_color = (50, 200, 50) if ratio > 0.5 else (220, 180, 50) if ratio > 0.25 else (220, 50, 50)
        pygame.draw.rect(surface, hp_color, (px, py, int(bar_w * ratio), bar_h), border_radius=4)
        pygame.draw.rect(surface, (200, 200, 200), (px, py, bar_w, bar_h), 2, border_radius=4)
        hp_text = self.font_tiny.render(f"HP: {int(player.hp)}/{player.max_hp}", True, (255, 255, 255))
        surface.blit(hp_text, (px + bar_w + 8, py + 1))

        stats = [
            f"Floor: {floors + 1}",
            f"Kills: {kills}",
            f"Time: {int(elapsed//60):02d}:{int(elapsed%60):02d}",
            f"DMG: {player.damage}",
            f"SPD: {int(player.speed)}",
        ]
        for i, stat in enumerate(stats):
            t = self.font_tiny.render(stat, True, (200, 200, 220))
            surface.blit(t, (20, 50 + i * 20))

        dash_cd = max(0, player.dash_cooldown)
        dash_ready = dash_cd <= 0
        dash_color = (80, 200, 255) if dash_ready else (60, 60, 100)
        dash_label = self.font_tiny.render(f"DASH {'READY' if dash_ready else f'{dash_cd:.1f}s'}", True, dash_color)
        surface.blit(dash_label, (20, 160))

    def draw_death(self, surface, floors, kills, elapsed):
        surface.fill((5, 5, 10))
        self.tick += 1

        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((180, 0, 0, 30 + int(20 * math.sin(self.tick * 0.05))))
        surface.blit(overlay, (0, 0))

        title = self.font_large.render("YOU DIED", True, (220, 30, 30))
        surface.blit(title, (self.sw//2 - title.get_width()//2, 150))

        stats = [
            f"Floors Cleared: {floors}",
            f"Enemies Killed: {kills}",
            f"Time Survived: {int(elapsed//60):02d}:{int(elapsed%60):02d}",
        ]
        for i, stat in enumerate(stats):
            t = self.font_med.render(stat, True, (200, 180, 180))
            surface.blit(t, (self.sw//2 - t.get_width()//2, 280 + i * 50))

        mouse = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()
        result = None

        buttons = [
            ('PLAY AGAIN', 'restart', self.sw//2 - 260, 480),
            ('MAIN MENU', 'menu', self.sw//2 + 20, 480),
        ]
        for label, action, bx, by in buttons:
            bw, bh = 220, 52
            hovered = bx <= mouse[0] <= bx + bw and by <= mouse[1] <= by + bh
            color = (140, 40, 40) if hovered else (80, 20, 20)
            pygame.draw.rect(surface, color, (bx, by, bw, bh), border_radius=8)
            pygame.draw.rect(surface, (220, 80, 80), (bx, by, bw, bh), 2, border_radius=8)
            t = self.font_med.render(label, True, (255, 220, 220))
            surface.blit(t, (bx + bw//2 - t.get_width()//2, by + bh//2 - t.get_height()//2))
            if hovered and clicks[0]:
                result = action

        pygame.display.flip()
        return result