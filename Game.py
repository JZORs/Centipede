import pygame, sys 

from arcade_machine_sdk import GameBase, GameMeta
from Source.Scripts.Entities import PhysicsEntity, Player
from Source.Scripts.Tilemap import Tilemap
from Source.Scripts.Utils import load_image, load_images, BASE_PATH

class Game(GameBase):
    def __init__(self, metadata = GameMeta): 
        super().__init__(metadata)

        self.display = pygame.Surface((512, 384)) 

        self.assets = {
            'player': load_image(BASE_PATH / "entities" / "player" / "player.png"),
            'projectile': load_image(BASE_PATH / "entities" / "player" / "projectile.png"),
            'normal_m': load_images(BASE_PATH / "tiles" / "normal_m"),
            'poison_m': load_images(BASE_PATH / "tiles" / "poisoned_m"),
            'centipede/head': load_images(BASE_PATH / "entities" / "centipede" / "cent_head"),
            'centipede/h_tilt': load_images(BASE_PATH / "entities" / "centipede" / "head_tilt"),
            'centipede/body': load_images(BASE_PATH / "entities" / "centipede" / "cent_body"),
            'centipede/b_tilt': load_images(BASE_PATH / "entities" / "centipede" / "body_tilt"),
        }

        self.movement = [False, False, False, False]
        self.projectiles = []

        self.tilemap = Tilemap(self, tile_size = 8)
        self.tilemap.generate_map()

        self.player = Player(self, (256, 350), (9, 9))

    def handle_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.movement[0] = True
                if event.key == pygame.K_s:
                    self.movement[1] = True
                if event.key == pygame.K_a:
                    self.movement[2] = True
                if event.key == pygame.K_d:
                    self.movement[3] = True
                if event.key == pygame.K_SPACE:
                    self.player.shoot()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.movement[0] = False
                if event.key == pygame.K_s:
                    self.movement[1] = False
                if event.key == pygame.K_a:
                    self.movement[2] = False
                if event.key == pygame.K_d:
                    self.movement[3] = False
    
    def update(self, dt: float):
        self.display.fill((20,18,29))
        self.player.update(self.tilemap, (self.movement[3] - self.movement[2], self.movement[1] - self.movement[0]))

        for projectile in self.projectiles:
            projectile[0][1] -= projectile[1]
            img = self.assets['projectile']
            self.display.blit(img, (projectile[0][0] - img.get_width() / 2 + 1, projectile[0][1] - img.get_height() / 2))
            if self.tilemap.solid_check(projectile[0]):
                tile = self.tilemap.solid_check(projectile[0])
                self.projectiles.remove(projectile)
                tile['variant'] += 1
                if tile['variant'] > 3:
                    tile_loc = str(tile['pos'][0]) + ';' + str(tile['pos'][1])
                    del self.tilemap.tilemap[tile_loc]
            elif projectile[0][1] < 15:
                self.projectiles.remove(projectile)

    def render(self):
        self.player.render(self.display)
        self.tilemap.render(self.display)

        pygame.draw.rect(self.display, (28,163,28), (6, 6, self.display.get_width() - 12, self.display.get_height() - 12), 3)

        self.surface.blit(pygame.transform.scale(self.display, self.surface.get_size()), (0, 0))
        