import pygame, sys 

from arcade_machine_sdk import GameBase, GameMeta
from Scripts.Entities import PhysicsEntity, CentipedeHead, CentipedeBody, Player
from Scripts.Tilemap import Tilemap
from Scripts.Utils import Animation, load_image, load_images, load_sound, draw_text, BASE_PATH

class Game(GameBase):
    def __init__(self, metadata = GameMeta): 
        super().__init__(metadata)

        self.display = pygame.Surface((512, 384)) 

        self.assets = {
            'player': load_image(BASE_PATH / "images" / "entities" / "player" / "player.png"),
            'projectile': load_image(BASE_PATH / "images" / "entities" / "player" / "projectile.png"),
            'normal_m': load_images(BASE_PATH / "images" / "tiles" / "normal_m"),
            'poison_m': load_images(BASE_PATH / "images" / "tiles" / "poisoned_m"),
            'player/idle': Animation(load_images(BASE_PATH / "images" / "entities" / "player" / "idle")),
            'player/fire': Animation(load_images(BASE_PATH / "images" / "entities" / "player" / "fire")),
            'centipede/head/idle': Animation(load_images(BASE_PATH / "images" / "entities" / "centipede" / "cent_head")),
            'centipede/head/tilt': Animation(load_images(BASE_PATH / "images" / "entities" / "centipede" / "head_tilt")),
            'centipede/body/idle': Animation(load_images(BASE_PATH / "images" / "entities" / "centipede" / "cent_body")),
            'centipede/body/tilt': Animation(load_images(BASE_PATH / "images" / "entities" / "centipede" / "body_tilt")),
        }

        self.sfx = {
            'mushroom': load_sound(BASE_PATH / "sounds" / "mushroom.wav"),
            'shoot': load_sound(BASE_PATH / "sounds" / "shoot.wav"),
        }

        self.sfx['shoot'].set_volume(0.2)
        self.sfx['mushroom'].set_volume(0.1)

        self.font = pygame.font.Font(BASE_PATH / 'ADDLG___.TTF', 9)

        self.movement = [False, False, False, False]
        self.projectiles = []

        self.tilemap = Tilemap(self, tile_size = 8)
        self.tilemap.generate_map(65)

        self.player = Player(self, (256, 350), (9, 9))
        self.dead = False

        self.centipede_head = CentipedeHead(self, (256, -10), 1.4)
        self.centipede_segments = []
        for i in range(8):
            self.centipede_segments.append(CentipedeBody(self, (self.centipede_head.pos[0], self.centipede_head.pos[1] * (i + 2))))

    def handle_events(self, events: list[pygame.event.Event]):
        if self.tilemap.current_row_idx >= len(self.tilemap.rows_ordered):
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
                        self.sfx['shoot'].play()
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
        self.display.fill((15,13,20))
        
        if self.tilemap.current_row_idx >= len(self.tilemap.rows_ordered):
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[3] - self.movement[2], self.movement[1] - self.movement[0]))
                if self.centipede_head.pos[1] >= 32:
                    self.centipede_head.falling = False
                    self.centipede_head.update(self.tilemap)
                else:
                    self.centipede_head.falling = True
                    self.centipede_head.pos[1] += self.centipede_head.speed
                    self.centipede_head.history.append({'pos': list(self.centipede_head.pos), 'tilt': False})
                    self.centipede_head.animation.update()

                for i, segment in enumerate(self.centipede_segments):
                    segment.follow(self.centipede_head, i)

                for projectile in self.projectiles:
                    projectile[0][1] -= projectile[1]
                    img = self.assets['projectile']
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 + 1, projectile[0][1] - img.get_height() / 2))
                    if self.tilemap.solid_check(projectile[0]):
                        tile = self.tilemap.solid_check(projectile[0])
                        self.projectiles.remove(projectile)
                        tile['variant'] += 1
                        self.sfx['mushroom'].play()
                        if tile['variant'] > 3:
                            tile_loc = str(tile['pos'][0]) + ';' + str(tile['pos'][1])
                            del self.tilemap.tilemap[tile_loc]
                    elif projectile[0][1] < 15:
                            self.projectiles.remove(projectile)

    def render(self):
        if not self.dead:
            draw_text(self.display, self.font, "SCORE:", 16, 16, (28,163,28))
            draw_text(self.display, self.font, "LIVES:", 400, 16, (28,163,28))

        pygame.draw.rect(self.display, (28,163,28), (6, 6, self.display.get_width() - 12, self.display.get_height() - 12), 3)
        pygame.draw.rect(self.display, (15,13,20), (246, 0, 30, 10))

        self.player.render(self.display)
        for i in range(len(self.player.lives)):
            self.display.blit(self.assets['player'], self.player.lives[i])
        self.tilemap.render(self.display)
        self.centipede_head.render(self.display)
        for segment in self.centipede_segments:
            segment.render(self.centipede_head, self.display)

        self.surface.blit(pygame.transform.scale(self.display, self.surface.get_size()), (0, 0))
        