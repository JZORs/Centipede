import pygame, sys

from arcade_machine_sdk import GameBase, GameMeta
from Scripts.Entities import PhysicsEntity, Player
from Scripts.Utils import load_image, load_images, BASE_PATH

class Game(GameBase):
    def __init__(self, metadata = GameMeta):
        super().__init__(metadata)

        self.display = pygame.Surface((512, 384)) 

        self.assets = {
            'mushroom': load_images(BASE_PATH / "tiles" / "normal_m"),
            'poison_mushroom': load_images(BASE_PATH / "tiles" / "poisoned_m"),
            'centipede_head': load_images(BASE_PATH / "entities" / "centipede" / "cent_head"),
            'head_tilt': load_images(BASE_PATH / "entities" / "centipede" / "head_tilt"),
            'centipede_body': load_images(BASE_PATH / "entities" / "centipede" / "cent_body"),
            'body_tilt': load_images(BASE_PATH / "entities" / "centipede" / "body_tilt"),
            'player': load_image(BASE_PATH / "entities" / "player" / "player.png"),
            'projectile': load_image(BASE_PATH / "entities" / "player" / "projectile.png"),
        }

        self.movement = [False, False, False, False]

        self.player = Player(self, (256, 350), (9, 10))

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
        self.player.update((self.movement[3] - self.movement[2], self.movement[1] - self.movement[0]))

    def render(self):
        self.display.fill((20,18,29))
        self.player.render(self.display)

        pygame.draw.rect(self.display, (28,163,28), (5, 5, self.display.get_width() - 10, self.display.get_height() - 10), 5)

        self.surface.blit(pygame.transform.scale(self.display, self.surface.get_size()), (0, 0))
        