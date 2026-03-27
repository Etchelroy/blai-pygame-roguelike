import pygame
import sys
from game import Game

def main():
    pygame.init()
    game = Game()
    clock = pygame.time.Clock()
    FPS = 60
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            game.handle_event(event)
        
        game.update(dt)
        game.render()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()