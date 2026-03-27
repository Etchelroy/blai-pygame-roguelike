import pygame

class UI:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

    def draw_main_menu(self, surface):
        surface.fill((20, 20, 20))
        title = self.font_large.render('ROGUELIKE DUNGEON', True, (255, 255, 0))
        start_text = self.font_medium.render('Press SPACE to Start Run', True, (100, 255, 100))
        instructions = self.font_small.render('WASD: Move | Mouse: Aim | Click: Shoot | Space: Dash', True, (200, 200, 200))

        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, 100))
        surface.blit(start_text, (surface.get_width() // 2 - start_text.get_width() // 2, 300))
        surface.blit(instructions, (surface.get_width() // 2 - instructions.get_width() // 2, 400))

        button_rect = pygame.Rect(surface.get_width() // 2 - 100, 250, 200, 60)
        pygame.draw.rect(surface, (0, 200, 0), button_rect)
        button_text = self.font_medium.render('START', True, (255, 255, 255))
        surface.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))

        return button_rect

    def draw_hud(self, surface, player, dungeon, time_survived):
        health_text = self.font_small.render(f'Health: {max(0, int(player.health))}/{int(player.max_health)}', True, (255, 0, 0))
        damage_text = self.font_small.render(f'Damage: {int(player.damage)}', True, (255, 100, 0))
        floor_text = self.font_small.render(f'Floor: {dungeon.floor}', True, (100, 200, 255))
        room_text = self.font_small.render(f'Room: {dungeon.current_room_idx + 1}/{len(dungeon.rooms)}', True, (100, 200, 255))
        time_text = self.font_small.render(f'Time: {int(time_survived)}s', True, (200, 200, 200))

        surface.blit(health_text, (10, 10))
        surface.blit(damage_text, (10, 40))
        surface.blit(floor_text, (10, 70))
        surface.blit(room_text, (10, 100))
        surface.blit(time_text, (surface.get_width() - time_text.get_width() - 10, 10))

        room = dungeon.get_current_room()
        if room and len(room.enemies) > 0:
            enemies_text = self.font_small.render(f'Enemies: {len(room.enemies)}', True, (255, 100, 100))
            surface.blit(enemies_text, (surface.get_width() - enemies_text.get_width() - 10, 40))

    def draw_death_screen(self, surface, floors_cleared, enemies_killed, time_survived):
        surface.fill((20, 20, 20))
        game_over = self.font_large.render('GAME OVER', True, (255, 0, 0))
        floors_text = self.font_medium.render(f'Floors Cleared: {floors_cleared}', True, (255, 255, 0))
        enemies_text = self.font_medium.render(f'Enemies Killed: {enemies_killed}', True, (255, 255, 0))
        time_text = self.font_medium.render(f'Time Survived: {int(time_survived)}s', True, (255, 255, 0))
        restart_text = self.font_small.render('Press SPACE to return to menu', True, (100, 255, 100))

        surface.blit(game_over, (surface.get_width() // 2 - game_over.get_width() // 2, 100))
        surface.blit(floors_text, (surface.get_width() // 2 - floors_text.get_width() // 2, 250))
        surface.blit(enemies_text, (surface.get_width() // 2 - enemies_text.get_width() // 2, 320))
        surface.blit(time_text, (surface.get_width() // 2 - time_text.get_width() // 2, 390))
        surface.blit(restart_text, (surface.get_width() // 2 - restart_text.get_width() // 2, 500))