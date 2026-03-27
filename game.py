import pygame
import sys
import time
from player import Player
from dungeon import Dungeon
from enemies import MeleeEnemy, RangedEnemy, BossEnemy
from items import Item
from projectiles import ProjectileManager
from hud import HUD
from screens import DeathScreen, MainMenuScreen, LevelUpScreen
from collision import CollisionSystem

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "menu"  # menu, playing, dead, levelup
        self.clock_start = 0.0
        self.time_survived = 0.0
        self.floors_cleared = 0
        self.enemies_killed = 0
        self.current_floor = 1

        self.dungeon = None
        self.player = None
        self.enemies = []
        self.items = []
        self.proj_manager = None
        self.hud = None
        self.collision = None

        self.death_screen = DeathScreen(screen)
        self.main_menu = MainMenuScreen(screen)
        self.levelup_screen = LevelUpScreen(screen)

        self.camera_x = 0
        self.camera_y = 0

        self.message_log = []
        self.levelup_pending = False

        self.font = pygame.font.SysFont("monospace", 16)

    def show_main_menu(self):
        self.state = "menu"

    def start_game(self):
        self.state = "playing"
        self.floors_cleared = 0
        self.enemies_killed = 0
        self.time_survived = 0.0
        self.clock_start = time.time()
        self.current_floor = 1
        self.message_log = []
        self.levelup_pending = False
        self._load_floor()

    def _load_floor(self):
        self.dungeon = Dungeon(self.current_floor)
        spawn = self.dungeon.get_player_spawn()
        self.player = Player(spawn[0], spawn[1])
        self.proj_manager = ProjectileManager()
        self.collision = CollisionSystem(self.dungeon)
        self.hud = HUD(self.screen, self.player, self.dungeon)
        self.enemies = self._spawn_enemies()
        self.items = []
        self._update_camera()

    def _spawn_enemies(self):
        enemies = []
        rooms = self.dungeon.rooms[1:]  # skip spawn room
        floor = self.current_floor
        for i, room in enumerate(rooms):
            cx = (room[0] + room[2] // 2) * 32
            cy = (room[1] + room[3] // 2) * 32
            if i == len(rooms) - 1:
                boss = BossEnemy(cx, cy, floor)
                enemies.append(boss)
            else:
                num_melee = 1 + floor // 2
                num_ranged = floor // 2
                for j in range(num_melee):
                    ex = cx + (j - num_melee // 2) * 40
                    ey = cy + 20
                    enemies.append(MeleeEnemy(ex, ey, floor))
                for j in range(num_ranged):
                    ex = cx + (j - num_ranged // 2) * 50
                    ey = cy - 20
                    enemies.append(RangedEnemy(ex, ey, floor))
        return enemies

    def handle_event(self, event):
        if self.state == "menu":
            result = self.main_menu.handle_event(event)
            if result == "start":
                self.start_game()
            elif result == "quit":
                pygame.quit()
                sys.exit()

        elif self.state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                wx = mx + self.camera_x
                wy = my + self.camera_y
                self.player.shoot(wx, wy, self.proj_manager)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.dash()

        elif self.state == "dead":
            result = self.death_screen.handle_event(event)
            if result == "restart":
                self.start_game()
            elif result == "menu":
                self.show_main_menu()

        elif self.state == "levelup":
            result = self.levelup_screen.handle_event(event)
            if result:
                self.player.apply_levelup(result)
                self.levelup_pending = False
                self.state = "playing"

    def update(self, dt):
        if self.state != "playing":
            return

        self.time_survived = time.time() - self.clock_start

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.collision)

        self._update_camera()

        # update projectiles
        self.proj_manager.update(dt, self.collision)

        # update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, self.player, self.proj_manager, self.collision)
            # check player projectile hits on enemy
            for proj in self.proj_manager.player_projectiles[:]:
                if enemy.rect.colliderect(proj.rect):
                    dmg = proj.damage
                    enemy.take_damage(dmg)
                    self.proj_manager.player_projectiles.remove(proj)
                    if enemy.hp <= 0:
                        self.enemies_killed += 1
                        self._drop_item(enemy.x, enemy.y)
                        self.enemies.remove(enemy)
                        self.player.gain_xp(enemy.xp_value)
                        if self.player.level_up_ready:
                            self.player.level_up_ready = False
                            self.levelup_pending = True
                        break

            # check enemy projectile hits on player
            for proj in self.proj_manager.enemy_projectiles[:]:
                if self.player.rect.colliderect(proj.rect):
                    self.player.take_damage(proj.damage)
                    self.proj_manager.enemy_projectiles.remove(proj)

        # check melee enemy collision with player
        for enemy in self.enemies:
            if hasattr(enemy, 'melee_attack'):
                if enemy.rect.colliderect(self.player.rect):
                    enemy.melee_attack(self.player, dt)

        # pickup items
        for item in self.items[:]:
            if self.player.rect.colliderect(item.rect):
                item.apply(self.player)
                self.items.remove(item)
                self.message_log.append(f"Picked up: {item.name}")
                if len(self.message_log) > 5:
                    self.message_log.pop(0)

        # check player death
        if self.player.hp <= 0:
            self.state = "dead"
            self.death_screen.set_stats(self.floors_cleared, self.enemies_killed, self.time_survived)
            return

        # check floor cleared
        if len(self.enemies) == 0:
            self.floors_cleared += 1
            self.current_floor += 1
            self.levelup_pending = False
            self._load_floor()
            return

        if self.levelup_pending:
            self.state = "levelup"
            self.levelup_screen.activate()
            self.levelup_pending = False

        self.hud.update(self.message_log)

    def _drop_item(self, x, y):
        import random
        if random.random() < 0.4:
            itype = random.choice(["health", "damage", "speed"])
            self.items.append(Item(x, y, itype))

    def _update_camera(self):
        self.camera_x = int(self.player.x - 480)
        self.camera_y = int(self.player.y - 360)

    def render(self):
        self.screen.fill((10, 10, 20))

        if self.state == "menu":
            self.main_menu.render()

        elif self.state == "playing":
            self._render_game()

        elif self.state == "dead":
            self.death_screen.render()

        elif self.state == "levelup":
            self._render_game()
            self.levelup_screen.render()

    def _render_game(self):
        # Draw dungeon
        self.dungeon.render(self.screen, self.camera_x, self.camera_y)

        # Draw items
        for item in self.items:
            item.render(self.screen, self.camera_x, self.camera_y)

        # Draw enemies (depth sorted)
        all_entities = self.enemies[:]
        all_entities.append(self.player)
        all_entities.sort(key=lambda e: e.y)

        for entity in all_entities:
            entity.render(self.screen, self.camera_x, self.camera_y)

        # Draw projectiles
        self.proj_manager.render(self.screen, self.camera_x, self.camera_y)

        # Draw HUD
        self.hud.render()

        # Draw message log
        for i, msg in enumerate(self.message_log):
            surf = self.font.render(msg, True, (255, 220, 100))
            self.screen.blit(surf, (10, 600 - i * 20))