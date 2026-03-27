import pygame
import sys
import math
from player import Player
from enemies import Enemy
from dungeon import Dungeon
from items import ItemManager
from ui import UI

pygame.init()

WIDTH, HEIGHT = 1600, 900
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Roguelike Dungeon')
clock = pygame.time.Clock()

ui = UI()
state = 'menu'
player = None
dungeon = None
item_manager = None
time_survived = 0
enemies_killed = 0
floors_cleared = 0

def start_game():
    global player, dungeon, item_manager, time_survived, enemies_killed, floors_cleared, state
    player = Player(WIDTH // 2, HEIGHT // 2)
    dungeon = Dungeon(WIDTH, HEIGHT)
    item_manager = ItemManager()
    time_survived = 0
    enemies_killed = 0
    floors_cleared = 0
    state = 'playing'

def reset_game():
    global state
    state = 'menu'

def check_collisions():
    global enemies_killed
    room = dungeon.get_current_room()
    if not room:
        return

    for projectile in player.projectiles[:]:
        proj_rect = pygame.Rect(projectile['x'] - projectile['radius'], projectile['y'] - projectile['radius'], projectile['radius'] * 2, projectile['radius'] * 2)
        for enemy in room.enemies[:]:
            if proj_rect.colliderect(enemy.get_rect()):
                if enemy.take_damage(projectile['damage']):
                    room.enemies.remove(enemy)
                    enemies_killed += 1
                if projectile in player.projectiles:
                    player.projectiles.remove(projectile)
                break

    for enemy in room.enemies:
        if player.get_rect().colliderect(enemy.get_rect()):
            if player.take_damage(enemy.damage):
                return True

    for projectile in enemy.projectiles[:]:
        proj_rect = pygame.Rect(projectile['x'] - projectile['radius'], projectile['y'] - projectile['radius'], projectile['radius'] * 2, projectile['radius'] * 2)
        if proj_rect.colliderect(player.get_rect()):
            if player.take_damage(projectile['damage']):
                return True
            enemy.projectiles.remove(projectile)

    return False

def check_wall_collisions():
    room = dungeon.get_current_room()
    if not room:
        return

    player_rect = player.get_rect()
    room_rect = room.get_rect()

    if player_rect.left < room_rect.left:
        player.x = room_rect.left + player.width // 2
    if player_rect.right > room_rect.right:
        player.x = room_rect.right - player.width // 2
    if player_rect.top < room_rect.top:
        player.y = room_rect.top + player.height // 2
    if player_rect.bottom > room_rect.bottom:
        player.y = room_rect.bottom - player.height // 2

    for enemy in room.enemies:
        enemy_rect = enemy.get_rect()
        if enemy_rect.left < room_rect.left:
            enemy.x = room_rect.left + enemy.width // 2
        if enemy_rect.right > room_rect.right:
            enemy.x = room_rect.right - enemy.width // 2
        if enemy_rect.top < room_rect.top:
            enemy.y = room_rect.top + enemy.height // 2
        if enemy_rect.bottom > room_rect.bottom:
            enemy.y = room_rect.bottom - enemy.height // 2

def check_room_transition():
    room = dungeon.get_current_room()
    if not room:
        return

    player_rect = player.get_rect()
    room_rect = room.get_rect()

    if player_rect.top < room_rect.top and room.doors['up']:
        if dungeon.current_room_idx > 0:
            dungeon.current_room_idx -= 1
            player.y = room_rect.bottom - 30
    elif player_rect.bottom > room_rect.bottom and room.doors['down']:
        dungeon.advance_room()
        room = dungeon.get_current_room()
        if room:
            player.y = room.get_rect().top + 30
    elif player_rect.left < room_rect.left and room.doors['left']:
        if dungeon.current_room_idx > 0:
            dungeon.current_room_idx -= 1
            player.x = room_rect.right - 30
    elif player_rect.right > room_rect.right and room.doors['right']:
        dungeon.advance_room()
        room = dungeon.get_current_room()
        if room:
            player.x = room.get_rect().left + 30

def update_game(dt):
    global time_survived, floors_cleared

    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    player.update(dt, keys, mouse_pos)
    time_survived += dt

    room = dungeon.get_current_room()
    if room:
        for enemy in room.enemies:
            enemy.update(dt, player)

        item_manager.update(dt)
        item_manager.check_player_collision(player)

        dungeon.current_room_cleared()
        if room.cleared and len(room.enemies) == 0:
            if dungeon.advance_room():
                floors_cleared += 1
            else:
                new_room = dungeon.get_current_room()
                if new_room:
                    item_manager.spawn_items(new_room)

    check_wall_collisions()
    check_room_transition()

    if check_collisions():
        return True

    return False

def draw_game():
    screen.fill((0, 0, 0))

    dungeon.draw(screen)

    room = dungeon.get_current_room()
    if room:
        for enemy in room.enemies:
            enemy.draw(screen)

    player.draw(screen)
    item_manager.draw(screen)

    ui.draw_hud(screen, player, dungeon, time_survived)

    pygame.display.flip()

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if state == 'menu':
                    start_game()
                elif state == 'death':
                    reset_game()
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == 'playing' and event.button == 1:
                player.shoot()

    if state == 'menu':
        ui.draw_main_menu(screen)
        pygame.display.flip()
    elif state == 'playing':
        if update_game(dt):
            state = 'death'
            floors_cleared = dungeon.floor - 1
        else:
            draw_game()
    elif state == 'death':
        ui.draw_death_screen(screen, floors_cleared, enemies_killed, time_survived)
        pygame.display.flip()

    keys = pygame.key.get_pressed()
    if state == 'playing' and keys[pygame.K_SPACE]:
        if hasattr(player, 'last_dash_key') and player.last_dash_key:
            pass
        else:
            player.last_dash_key = True
            player.dash()
    else:
        player.last_dash_key = False

pygame.quit()
sys.exit()