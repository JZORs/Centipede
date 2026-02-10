import pygame, random

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

class Tilemap():
    def __init__(self, game, tile_size = 8):
        self.game = game
        self.tile_size = tile_size
        self.random_pos = [list(range(2,60)), list(range(5, 40))]
        self.tilemap = {}

    def generate_map(self):
        self.random_pos = [list(range(2,60)), list(range(5, 40))]
        self.tilemap = {}
        tiles_to_create = 30
        while tiles_to_create > 0:
            if not self.random_pos[0] or not self.random_pos[1]:
                break
                
            x = random.choice(self.random_pos[0])
            y = random.choice(self.random_pos[1])
            
            self.tilemap[f"{x};{y}"] = {'type': 'normal_m', 'variant': 0, 'pos': (x, y)}
            
            self.random_pos[0].remove(x)
            self.random_pos[1].remove(y)
            tiles_to_create -= 1

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def solid_check(self, pos):
        tile_loc = str(pos[0] // self.tile_size) + ';' + str(pos[1] // self.tile_size)
        if tile_loc in self.tilemap:
            return self.tilemap[tile_loc]
            
    def render(self, surf):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))