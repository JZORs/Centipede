import pygame, random

class Mushroom():
    def __init__(self, game, position, size = (8, 8), lifes = 4):
        self.pos = list(position)
        self.game = game
        self.size = size
        self.lifes = lifes

    def update(self):
        pass

    def render(self, surf):
        surf.blit(self.game.assets['mushroom'][self.lifes], self.pos)

class Tilemap():
    def __init__(self, game, tile_size = 8):
        self.game = game
        self.tile_size = tile_size
        self.mushrooms = {}

    def auto_tile(self):
        pass

    def render(self, surf):
        pass    