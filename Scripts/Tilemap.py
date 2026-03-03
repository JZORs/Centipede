import pygame, random

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

class Tilemap():
    def __init__(self, game, tile_size = 8):
        self.game = game
        self.tile_size = tile_size
        self.random_pos = [list(range(2,60)), list(range(7, 38))]
        self.tilemap = {}
        self.rows_ordered = []
        self.current_row_idx = 0  
        self.timer = 0
        self.speed = 13

    def add_mushroom(self, pos):
        grid_pos = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        tile_loc = str(grid_pos[0]) + ';' + str(grid_pos[1])
        
        if tile_loc not in self.tilemap:
            self.tilemap[tile_loc] = {'type': 'normal_m', 'variant': 0, 'pos': grid_pos}

    def generate_map(self, tiles_to_create):
        self.tilemap = {}
        self.tiles_to_create = tiles_to_create
        self.range_x = self.random_pos[0]
        self.range_y = self.random_pos[1]
        
        while self.tiles_to_create > 0:
            x = random.choice(self.range_x)
            y = random.choice(self.range_y)
            loc = str(x) + ';' + str(y)

            if loc not in self.tilemap:
                self.tilemap[loc] = {'type': 'normal_m', 'variant': 0, 'pos': (x, y)}
                self.tiles_to_create -= 1

        all_ys = set(tile['pos'][1] for tile in self.tilemap.values())
        self.rows_ordered = sorted(list(all_ys))
        self.current_row_idx = 0
        self.timer = 0

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
        if self.current_row_idx < len(self.rows_ordered):
            self.timer += 1
            if self.timer >= self.speed:
                self.current_row_idx += 1
                self.timer = 0
                self.game.sfx['mushroom'].play()
        
        if self.current_row_idx > 0:
            max_y = self.rows_ordered[self.current_row_idx - 1]
        else: 
            max_y = -1

        if self.current_row_idx >= len(self.rows_ordered):
            max_y = float('inf')
        
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if tile['pos'][1] <= max_y:
                surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))