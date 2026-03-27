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
I'll analyze what's needed and implement the complete game across all six modules.

```python
# filename: main.py
import pygame
import sys
import time
from dungeon import Dungeon
from player import Player
from ui import UI
from items import ItemPickup

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60

def run_game(screen, clock):
    dungeon = Dungeon(screen_w=SCREEN_W, screen_h=SCREEN_H)
    player = Player(0, 0)
    ui = UI(SCREEN_W, SCREEN_H)
    
    start_room = dungeon.rooms[0]
    player.x = start_room.center_x * dungeon.tile_size
    player.y = start_room.center_y * dungeon.tile_size
    
    floors_cleared = 0
    enemies_killed = 0
    start_time = time.time()
    current_floor_enemies_killed = 0
    
    item_pickups = []
    between_rooms = False
    pending_item = None
    
    camera_x, camera_y = 0, 0
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)
        
        mouse_pos = pygame.mouse.get_pos()
        world_mouse_x = mouse_pos[0] + camera_x
        world_mouse_y = mouse_pos[1] + camera_y
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit', 0, 0, 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit', floors_cleared, enemies_killed, time.time() - start_time
                if event.key == pygame.K_SPACE:
                    player.dash()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.shoot(world_mouse_x, world_mouse_y)
        
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        
        player.update(dt, dx, dy, dungeon)
        player.update_projectiles(dt, dungeon)
        
        current_room = dungeon.get_room_at(player.x, player.y)
        
        if not between_rooms:
            active_enemies = dungeon.get_active_enemies()
            for enemy in active_enemies:
                enemy.update(dt, player, dungeon)
            
            for proj in player.projectiles[:]:
                for enemy in active_enemies[:]:
                    if enemy.alive and proj.check_collision(enemy):
                        enemy.take_damage(proj.damage)
                        proj.active = False
                        if not enemy.alive:
                            enemies_killed += 1
                            current_floor_enemies_killed += 1
            
            player.projectiles = [p for p in player.projectiles if p.active]
            
            for enemy in active_enemies:
                if enemy.alive:
                    for proj in enemy.projectiles[:]:
                        if proj.check_collision(player):
                            player.take_damage(proj.damage)
                            proj.active = False
                    enemy.projectiles = [p for p in enemy.projectiles if p.active]
                    
                    if enemy.enemy_type == 'melee':
                        ex, ey = enemy.x + enemy.size//2, enemy.y + enemy.size//2
                        px, py = player.x + player.size//2, player.y + player.size//2
                        dist = ((ex-px)**2 + (ey-py)**2)**0.5
                        if dist < (enemy.size + player.size) // 2 + 5:
                            player.take_damage(enemy.contact_damage * dt)
            
            if current_room and dungeon.is_room_cleared(current_room):
                if not current_room.cleared:
                    current_room.cleared = True
                    if current_room != dungeon.rooms[-1]:
                        item_type = ['health', 'damage', 'speed'][current_floor_enemies_killed % 3]
                        cx = current_room.center_x * dungeon.tile_size
                        cy = current_room.center_y * dungeon.tile_size
                        item_pickups.append(ItemPickup(cx, cy, item_type))
            
            for item in item_pickups[:]:
                if not item.collected:
                    px, py = player.x + player.size//2, player.y + player.size//2
                    ix, iy = item.x + item.size//2, item.y + item.size//2
                    dist = ((px-ix)**2 + (py-iy)**2)**0.5
                    if dist < (player.size + item.size) // 2:
                        item.apply(player)
                        item.collected = True
                        item_pickups.remove(item)
            
            if dungeon.all_rooms_cleared():
                floors_cleared += 1
                current_floor_enemies_killed = 0
                dungeon = Dungeon(screen_w=SCREEN_W, screen_h=SCREEN_H, floor=floors_cleared)
                item_pickups = []
                start_room = dungeon.rooms[0]
                player.x = start_room.center_x * dungeon.tile_size
                player.y = start_room.center_y * dungeon.tile_size
                player.projectiles = []
        
        if not player.alive:
            elapsed = time.time() - start_time
            return 'dead', floors_cleared, enemies_killed, elapsed
        
        camera_x = int(player.x + player.size // 2 - SCREEN_W // 2)
        camera_y = int(player.y + player.size // 2 - SCREEN_H // 2)
        
        screen.fill((10, 10, 15))
        dungeon.draw(screen, camera_x, camera_y)
        
        for item in item_pickups:
            item.draw(screen, camera_x, camera_y)
        
        active_enemies = dungeon.get_active_enemies()
        for enemy in active_enemies:
            enemy.draw(screen, camera_x, camera_y)
        
        player.draw(screen, camera_x, camera_y)
        
        ui.draw_hud(screen, player, floors_cleared, enemies_killed, time.time() - start_time)
    
    return 'quit', floors_cleared, enemies_killed, time.time() - start_time


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Dungeon Roguelike")
    clock = pygame.time.Clock()
    ui = UI(SCREEN_W, SCREEN_H)
    
    state = 'menu'
    result_data = None
    
    while True:
        if state == 'menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            
            action = ui.draw_menu(screen)
            if action == 'start':
                state = 'game'
            pygame.display.flip()
            clock.tick(FPS)
        
        elif state == 'game':
            outcome, floors, kills, elapsed = run_game(screen, clock)
            if outcome == 'quit':
                pygame.quit(); sys.exit()
            elif outcome == 'dead':
                result_data = (floors, kills, elapsed)
                state = 'death'
        
        elif state == 'death':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
            
            action = ui.draw_death(screen, *result_data)
            if action == 'menu':
                state = 'menu'
            elif action == 'restart':
                state = 'game'
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == '__main__':
    main()