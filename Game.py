import pygame, random, math, sys 

from arcade_machine_sdk import GameBase, GameMeta
from Scripts.Entities import PhysicsEntity, CentipedeHead, CentipedeBody, Player
from Scripts.Tilemap import Tilemap
from Scripts.Particles import Particle
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
            'particle/player': Animation(load_images(BASE_PATH / "images" / "particles" / "player"), img_dur=6, loop=False),
            'particle/centipede': Animation(load_images(BASE_PATH / "images" / "particles" / "centipede"), img_dur=6, loop=False),
            'particle/mushroom': Animation(load_images(BASE_PATH / "images" / "particles" / "mushroom"), img_dur=6, loop=False),
            'player/idle': Animation(load_images(BASE_PATH / "images" / "entities" / "player" / "idle"), img_dur=8),
            'player/fire': Animation(load_images(BASE_PATH / "images" / "entities" / "player" / "fire")),
            'centipede/head/idle': Animation(load_images(BASE_PATH / "images" / "entities" / "centipede" / "cent_head")),
            'centipede/head/tilt': Animation(load_images(BASE_PATH / "images" / "entities" / "centipede" / "head_tilt")),
            'centipede/body/idle': Animation(load_images(BASE_PATH / "images" / "entities" / "centipede" / "cent_body")),
            'centipede/body/tilt': Animation(load_images(BASE_PATH / "images" / "entities" / "centipede" / "body_tilt")),
        }

        self.sfx = {
            'mushroom': load_sound(BASE_PATH / "sounds" / "mushroom.wav"),
            'shoot': load_sound(BASE_PATH / "sounds" / "shoot.wav"),
            'get_shoot': load_sound(BASE_PATH / "sounds" / "get_shoot.wav"),
        }

        self.sfx['mushroom'].set_volume(0.1)
        self.sfx['shoot'].set_volume(0.2)
        self.sfx['get_shoot'].set_volume(0.2)

        self.font = pygame.font.Font(BASE_PATH / 'ADDLG___.TTF', 9)

        self.projectiles = []
        self.centipedes = []
        self.particles = []

        initial_head = CentipedeHead(self, (256, -10), 2.5)
        initial_segments = []
        for i in range(8):
            initial_segments.append(CentipedeBody(self, (initial_head.pos[0], initial_head.pos[1] * (i + 2))))

        self.centipedes.append({'head': initial_head, 'body': initial_segments})

        self.movement = [False, False, False, False]
        self.player = Player(self, (256, 350), (9, 9))
        self.dead = 0
        self.score = 0
        
        self.tilemap = Tilemap(self, tile_size = 8)
        self.tilemap.generate_map(70)

    def load_level(self):
        pass

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
                for centi in self.centipedes[:]:
                    head = centi['head']
                    body = centi['body']

                    if head.pos[1] >= 32:
                        head.falling = False
                        head.update(self.tilemap)
                    else:
                        head.falling = True
                        head.pos[1] += head.speed
                        head.history.append({'pos': list(head.pos), 'tilt': False})
                        head.animation.update()

                    for i, segment in enumerate(body):
                        segment.follow(head, i)

                collision_detected = False
                
                for centi in self.centipedes[:]:
                    if centi['head'].rect().colliderect(self.player.rect()):
                        collision_detected = True
                    for segment in centi['body']:
                        if segment.rect().colliderect(self.player.rect()):
                            collision_detected = True
                    if collision_detected:
                        break

                if collision_detected:
                    if len(self.player.lives) > 0:
                        self.player.lives.pop(0)

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
                            self.score += 1
                            tile_loc = str(tile['pos'][0]) + ';' + str(tile['pos'][1])
                            del self.tilemap.tilemap[tile_loc]
                    elif projectile[0][1] < 15:
                            self.projectiles.remove(projectile)

                    proj_rect = pygame.Rect(projectile[0][0], projectile[0][1], 4, 4)
                    hit_something = False

                    for centi in self.centipedes[:]:
                        if centi['head'].rect().colliderect(proj_rect):
                            self.score += 100
                            self.tilemap.add_mushroom(centi['head'].pos)
                            if centi['body']:
                                new_head_segment = centi['body'].pop(0)
                                centi['head'] = CentipedeHead(self, new_head_segment.pos, centi['head'].speed)
                            else:
                                self.centipedes.remove(centi)
                            centi['head'].set_action('idle')
                            hit_something = True
                            break

                        for i, segment in enumerate(centi['body']):
                            if segment.rect().colliderect(proj_rect):
                                self.score += 10
                                self.tilemap.add_mushroom(segment.pos)
                                new_body = centi['body'][i+1:]
                                centi['body'] = centi['body'][:i] 
                                if new_body:
                                    new_leader = new_body.pop(0)
                                    new_head = CentipedeHead(self, new_leader.pos, centi['head'].speed)
                                    new_head.pos[1] = round(new_head.pos[1] / 8) * 8
                                    self.centipedes.append({'head': new_head, 'body': new_body})
                                hit_something = True
                                break
                        if hit_something: break

                    if hit_something:
                        self.projectiles.remove(projectile)
                        self.sfx['get_shoot'].play()

    def render(self):
        if not self.dead:
            self.player.render(self.display)

            score_str = f"{self.score:03d}"
            draw_text(self.display, self.font, "SCORE:", 16, 16, (28,163,28))
            draw_text(self.display, self.font, score_str, 80, 16, (28,163,28))
            draw_text(self.display, self.font, "LIVES:", 400, 16, (28,163,28))

        pygame.draw.rect(self.display, (28,163,28), (6, 6, self.display.get_width() - 12, self.display.get_height() - 12), 3)
        pygame.draw.rect(self.display, (15,13,20), (246, 0, 30, 10))

        for i in range(len(self.player.lives)):
            self.display.blit(self.assets['player'], self.player.lives[i])
        self.tilemap.render(self.display)
        for centi in self.centipedes:
            centi['head'].render(self.display)
            for segment in centi['body']:
                segment.render(centi['head'], self.display)

        self.surface.blit(pygame.transform.scale(self.display, self.surface.get_size()), (0, 0))
        