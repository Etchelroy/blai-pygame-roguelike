import pygame
import math

class UI:
    def __init__(self, screen_w, screen_h, viewport_w, panel_w, tile):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.viewport_w = viewport_w
        self.panel_w = panel_w
        self.tile = tile
        self.font_lg = pygame.font.SysFont(None, 64)
        self.font_md = pygame.font.SysFont(None, 36)
        self.font_sm = pygame.font.SysFont(None, 24)
        self.font_xs = pygame.font.SysFont(None, 18)
        self.menu_btn_rect = None
        self.death_btn_rect = None

    def get_menu_button(self):
        return self.menu_btn_rect

    def get_death_button(self):
        return self.death_btn_rect

    def draw_menu(self, surf):
        surf.fill((10, 8, 18))
        # Title
        title = self.font_lg.render("DARKSTONE", True, (200, 160, 80))
        sub = self.font_md.render("A Dark Fantasy Roguelike", True, (140, 110, 60))
        surf.blit(title, (self.screen_w // 2 - title.get_width() // 2, 180))
        surf.blit(sub, (self.screen_w // 2 - sub.get_width() // 2, 260))

        # Decorative line
        pygame.draw.line(surf, (80, 60, 40),
            (self.screen_w // 2 - 200, 310),
            (self.screen_w // 2 + 200, 310), 2)

        # Instructions
        lines = [
            "WASD — Move",
            "Mouse — Aim",
            "Left Click — Shoot",
            "Space — Dash",
        ]
        for i, line in enumerate(lines):
            t = self.font_sm.render(line, True, (160, 140, 120))
            surf.blit(t, (self.screen_w // 2 - t.get_width() // 2, 330 + i * 30))

        # Start button
        btn_w, btn_h = 220, 55
        btn_x = self.screen_w // 2 - btn_w // 2
        btn_y = 500
        self.menu_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        mx, my = pygame.mouse.get_pos()
        hover = self.menu_btn_rect.collidepoint(mx, my)
        btn_col = (180, 140, 60) if hover else (130, 100, 40)
        pygame.draw.rect(surf, btn_col, self.menu_btn_rect, border_radius=8)
        pygame.draw.rect(surf, (220, 180, 80), self.menu_btn_rect, 2, border_radius=8)
        btn_label = self.font_md.render("Start Run", True, (255, 240, 200))
        surf.blit(btn_label, (btn_x + btn_w // 2 - btn_label.get_width() // 2,
                               btn_y + btn_h // 2 - btn_label.get_height() // 2))

        hint = self.font_xs.render("Press ENTER to start", True, (100, 90, 70))
        surf.blit(hint, (self.screen_w // 2 - hint.get_width() // 2, 570))

    def draw_death(self, surf, floors, kills, elapsed):
        surf.fill((8, 5, 12))
        title = self.font_lg.render("YOU DIED", True, (200, 30, 30))
        surf.blit(title, (self.screen_w // 2 - title.get_width() // 2, 160))

        pygame.draw.line(surf, (100, 30, 30),
            (self.screen_w // 2 - 200, 240),
            (self.screen_w // 2 + 200, 240), 2)

        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        stats = [
            f"Floors Cleared:   {floors}",
            f"Enemies Killed:   {kills}",
            f"Time Survived:    {mins:02d}:{secs:02d}",
        ]
        for i, line in enumerate(stats):
            t = self.font_md.render(line, True, (200, 160, 120))
            surf.blit(t, (self.screen_w // 2 - t.get_width() // 2, 270 + i * 45))

        btn_w, btn_h = 240, 55
        btn_x = self.screen_w // 2 - btn_w // 2
        btn_y = 460
        self.death_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        mx, my = pygame.mouse.get_pos()
        hover = self.death_btn_rect.collidepoint(mx, my)
        btn_col = (130, 30, 30) if hover else (90, 20, 20)
        pygame.draw.rect(surf, btn_col, self.death_btn_rect, border_radius=8)
        pygame.draw.rect(surf, (200, 50, 50), self.death_btn_rect, 2, border_radius=8)
        btn_label = self.font_md.render("Return to Menu", True, (255, 200, 200))
        surf.blit(btn_label, (btn_x + btn_w // 2 - btn_label.get_width() // 2,
                               btn_y + btn_h // 2 - btn_label.get_height() // 2))

        hint = self.font_xs.render("Press ENTER to continue", True, (100, 60, 60))
        surf.blit(hint, (self.screen_w // 2 - hint.get_width() // 2, 530))

    def draw_panel(self, surf, player, floor_num, kills, elapsed, dungeon, cam_x, cam_y,
                   current_room, cleared_rooms, total_rooms):
        px = self.viewport_w
        panel_rect = pygame.Rect(px, 0, self.panel_w, self.screen_h)
        pygame.draw.rect(surf, (18, 14, 28), panel_rect)
        pygame.draw.line(surf, (80, 60, 100), (px, 0), (px, self.screen_h), 2)

        y = 10
        # Floor info
        floor_txt = self.font_md.render(f"Floor {floor_num}", True, (200, 180, 100))
        surf.blit(floor_txt, (px + self.panel_w // 2 - floor_txt.get_width() // 2, y))
        y += 38

        # HP bar
        self._draw_bar(surf, px + 10, y, self.panel_w - 20, 18,
                       player.hp, player.max_hp, (50, 180, 50), (20, 60, 20), "HP")
        y += 26
        # Mana bar
        self._draw_bar(surf, px + 10, y, self.panel_w - 20, 18,
                       player.mana, player.max_mana, (50, 100, 210), (15,