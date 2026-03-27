import pygame
import random

class Room:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.wall_thickness = 20
        self._walls = None

    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    def get_walls(self):
        if self._walls is None:
            t = self.wall_thickness
            self._walls = [
                pygame.Rect(self.x, self.y, self.w, t),
                pygame.Rect(self.x, self.y + self.h - t, self.w, t),
                pygame.Rect(self.x, self.y, t, self.h),
                pygame.Rect(self.x + self.w - t, self.y, t, self.h),
            ]
        return self._walls

    def draw(self, screen):
        floor_color = (45, 45, 60)
        wall_color = (80, 60, 80)
        pygame.draw.rect(screen, floor_color, pygame.Rect(self.x, self.y, self.w, self.h))
        for wall in self.get_walls():
            pygame.draw.rect(screen, wall_color, wall)

class Dungeon:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        margin = 30
        self.current_room = Room(margin, margin, screen_w - margin * 2, screen_h - margin * 2)

    def next_room(self):
        margin = 30
        self.current_room = Room(margin, margin, self.screen_w - margin * 2, self.screen_h - margin * 2)
        self.current_room._walls = None

    def draw(self, screen):
        self.current_room.draw(screen)