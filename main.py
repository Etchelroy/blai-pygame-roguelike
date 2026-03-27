import pygame
import sys
from game import Game

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Dark Dungeon Roguelike")
    clock = pygame.time.Clock()

    game = Game(screen)
    game.show_main_menu()

    while True:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)  # cap delta time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update(dt)
        game.render()
        pygame.display.flip()

if __name__ == "__main__":
    main()