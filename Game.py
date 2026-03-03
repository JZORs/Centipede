import pygame, random, math, sys 

from arcade_machine_sdk import GameBase, GameMeta
from Scripts.Entities import PhysicsEntity, CentipedeHead, CentipedeBody, Player
from Scripts.Tilemap import Tilemap
from Scripts.Particles import Particle
from Scripts.Utils import Animation, load_image, load_images, load_sound, draw_text, BASE_PATH

class Game(GameBase):
    def __init__(self, metadata = GameMeta): 
        super().__init__(metadata)

        self.display = pygame.Surface((512, 384), pygame.SRCALPHA) 

        self.assets = {
            'player': load_image(BASE_PATH / "images" / "level_1" / "entities" / "player" / "player.png"),
            'projectile': load_image(BASE_PATH / "images" / "level_1" / "entities" / "player" / "projectile.png"),
            'normal_m': load_images(BASE_PATH / "images" / "level_1" / "tiles" / "normal_m"),
            'poison_m': load_images(BASE_PATH / "images" / "level_1" / "tiles" / "poisoned_m"),
            'particle/player': Animation(load_images(BASE_PATH / "images" / "level_1" / "particles" / "player"), img_dur=6, loop=False),
            'particle/centipede': Animation(load_images(BASE_PATH / "images" / "level_1" / "particles" / "centipede"), img_dur=6, loop=False),
            'particle/mushroom': Animation(load_images(BASE_PATH / "images" / "level_1" / "particles" / "mushroom"), img_dur=6, loop=False),
            'player/idle': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "player" / "idle"), img_dur=15),
            'player/fire': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "player" / "fire")),
            'centipede/head/idle': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "centipede" / "cent_head")),
            'centipede/head/tilt': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "centipede" / "head_tilt")),
            'centipede/body/idle': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "centipede" / "cent_body")),
            'centipede/body/tilt': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "centipede" / "body_tilt")),
        }

        self.sfx = {
            'mushroom': load_sound(BASE_PATH / "sounds" / "mushroom.wav"),
            'shoot': load_sound(BASE_PATH / "sounds" / "shoot.wav"),
            'get_shoot': load_sound(BASE_PATH / "sounds" / "get_shoot.wav"),
            'level_up' : load_sound(BASE_PATH / "sounds" / "level_up.wav"),
            'life_up' : load_sound(BASE_PATH / "sounds" / "life_up.wav"),
        }

        self.sfx['mushroom'].set_volume(0.1)
        self.sfx['get_shoot'].set_volume(0.1)
        self.sfx['shoot'].set_volume(0.2)
        self.sfx['level_up'].set_volume(0.2)
        self.sfx['life_up'].set_volume(0.2)

        self.movement = [False, False, False, False]

        self.font = pygame.font.Font(BASE_PATH / 'ADDLG___.TTF', 9)
        self.score = 0
        self.flag_score = 0
        self.death_timer = 0
        
        self.tilemap = Tilemap(self, tile_size = 8)
        self.tilemap.generate_map(70)
        self.healing_mushrooms = False

        self.level_borders = {
            '1': (28,163,28),
            '2': (189, 44, 153),
            '3': (198, 17, 17),
            '4': (255, 193, 0),
            '5': (0, 255, 193)
        }

        self.speed_configs = [
            {'speed': 1.5, 'lerp': 0.3},
            {'speed': 2.5, 'lerp': 0.2},
            {'speed': 3.5, 'lerp': 0.15}
        ]

        self.loop_levels = False
        self.level = 1
        self.load_level(self.level)

        self.screenshake = 0

    def load_level(self, level):
        if level > 5:
            level = 1
            self.level = 1
            self.loop_levels = True
        
        self.assets['normal_m'] = load_images(BASE_PATH / "images" / f"level_{level}" / "tiles" / "normal_m")
        self.assets['poison_m'] = load_images(BASE_PATH / "images" / f"level_{level}" / "tiles" / "poisoned_m")
        self.assets['player'] = load_image(BASE_PATH / "images" / f"level_{level}" / "entities" / "player" / "player.png")
        self.assets['projectile'] = load_image(BASE_PATH / "images" / f"level_{level}" / "entities" / "player" / "projectile.png")
        self.assets['particle/player'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "particles" / "player"), img_dur=6, loop=False)
        self.assets['particle/centipede'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "particles" / "centipede"), img_dur=6, loop=False)
        self.assets['particle/mushroom'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "particles" / "mushroom"), img_dur=6, loop=False)
        self.assets['player/idle'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "player" / "idle"), img_dur=15)
        self.assets['player/fire'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "player" / "fire"))
        self.assets['centipede/head/idle'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "centipede" / "cent_head"))
        self.assets['centipede/head/tilt'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "centipede" / "head_tilt"))
        self.assets['centipede/body/idle'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "centipede" / "cent_body"))
        self.assets['centipede/body/tilt'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "centipede" / "body_tilt"))

        self.current_color = self.level_borders[str(level)]
        config = random.choice(self.speed_configs)
        selected_speed = config['speed']
        selected_lerp = config['lerp']

        self.projectiles = []
        self.centipedes = []
        self.particles = []

        initial_head = CentipedeHead(self, (256, -10), selected_speed)
        initial_segments = []
        for i in range(8):
            segment = CentipedeBody(self, (initial_head.pos[0], initial_head.pos[1] * (i + 2)))
            segment.lerp_factor = selected_lerp
            initial_segments.append(segment)

        self.centipedes.append({'head': initial_head, 'body': initial_segments})

        if level > 1:
            num_extra_heads = level - 1
            
            for _ in range(num_extra_heads):
                spawn_x = random.randint(20, self.display.get_width() - 20)
                
                extra_head = CentipedeHead(self, (spawn_x, -10), selected_speed + 0.5)
                self.centipedes.append({'head': extra_head, 'body': []})

        if level == 1 and self.loop_levels == False:
            self.player = Player(self, (256, 350), (9, 9))
        else:
            self.player.pos = self.player.pos
            self.player.velocity = [0, 0]

        self.dead = 0
    
    def reset_after_death(self):
        self.projectiles = []
        self.centipedes = []

        config = random.choice(self.speed_configs)
        initial_head = CentipedeHead(self, (256, -10), config['speed'])
        initial_segments = []
        for i in range(8):
            segment = CentipedeBody(self, (initial_head.pos[0], initial_head.pos[1] * (i + 2)))
            segment.lerp_factor = config['lerp']
            initial_segments.append(segment)
        
        self.centipedes.append({'head': initial_head, 'body': initial_segments})

        if self.level > 1:
            num_extra_heads = self.level - 1
            
            for _ in range(num_extra_heads):
                spawn_x = random.randint(20, self.display.get_width() - 20)
                
                extra_head = CentipedeHead(self, (spawn_x, -10), config['speed'] + 0.5)
                self.centipedes.append({'head': extra_head, 'body': []})

        self.player.pos = [256, 350]
        self.player.velocity = [0, 0]

    def handle_events(self, events: list[pygame.event.Event]):
        if self.tilemap.current_row_idx >= len(self.tilemap.rows_ordered):
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.dead >= 1:
                        if event.key == pygame.K_SPACE:
                            self.score = 0
                            self.flag_score = 0
                            self.dead = 0
                            self.player.lives = [(452 + (self.assets['player'].get_width() * (i)), 15) for i in range(3)]
                            self.loop_levels = False
                            self.level = 1
                            self.load_level(1)
                    else:
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
                        if event.key == pygame.K_l:
                            self.level += 1
                            self.load_level(self.level)
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

                self.screenshake = max(0, self.screenshake - 1)

                if collision_detected and not self.healing_mushrooms and self.death_timer == 0:
                    self.sfx['get_shoot'].play()
                    self.screenshake = max(40, self.screenshake)
                    for _ in range(25):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.particles.append(Particle(self, 'player', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

                    if len(self.player.lives) > 0:        
                        self.player.lives.pop()
                        
                    if len(self.player.lives) == 0:
                        self.dead = 1
                    else:
                        self.player.pos = [-1000, -1000]
                        self.projectiles = [] 
                        self.centipedes = []
                        self.healing_mushrooms = True 
                
                if self.healing_mushrooms:
                    found_damaged = False
                    if pygame.time.get_ticks() % 150 < 20:
                        for loc in self.tilemap.tilemap:
                            tile = self.tilemap.tilemap[loc]
                            if tile['variant'] > 0:
                                tile['variant'] = 0
                                self.sfx['mushroom'].play()
                                found_damaged = True
                                break
                    else:
                        found_damaged = True

                    if not found_damaged:
                        self.healing_mushrooms = False
                        self.death_timer = 30

                if self.flag_score >= 12000:
                    self.sfx['life_up'].play()
                    self.player.add_life()
                    self.flag_score = 0
                
                if self.death_timer > 0:
                    self.death_timer -= 1
                    if self.death_timer == 0:
                        self.reset_after_death()
                    
                if self.dead:
                    self.player.pos = [-1000, -1000]
                    self.projectiles = []
                    return
                
                if len(self.centipedes) == 0 and not self.dead and self.death_timer == 0 and not self.healing_mushrooms:
                    self.sfx['level_up'].play()
                    self.screenshake = max(25, self.screenshake)
                    self.level += 1
                    self.load_level(self.level)

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
                            self.flag_score += 1
                            tile_loc = str(tile['pos'][0]) + ';' + str(tile['pos'][1])
                            del self.tilemap.tilemap[tile_loc]
                            for _ in range(8):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.particles.append(Particle(self, 'mushroom', (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size), velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                    elif projectile[0][1] < 15:
                            self.projectiles.remove(projectile)

                    proj_rect = pygame.Rect(projectile[0][0], projectile[0][1], 4, 4)
                    hit_something = False

                    for centi in self.centipedes[:]:
                        if centi['head'].rect().colliderect(proj_rect):
                            for _ in range(15):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.particles.append(Particle(self, 'centipede', centi['head'].rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                            self.score += 100
                            self.flag_score += 100
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
                                for _ in range(15):
                                    angle = random.random() * math.pi * 2
                                    speed = random.random() * 5
                                    self.particles.append(Particle(self, 'centipede', segment.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                                self.score += 10
                                self.flag_score += 10
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
            draw_text(self.display, self.font, "SCORE:", 16, 16, self.current_color)
            draw_text(self.display, self.font, score_str, 80, 16, self.current_color)
            draw_text(self.display, self.font, "LIVES:", 400, 16, self.current_color)

        pygame.draw.rect(self.display, self.current_color, (6, 6, self.display.get_width() - 12, self.display.get_height() - 12), 3)
        pygame.draw.rect(self.display, (15,13,20), (246, 0, 30, 10))

        for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display)
                if kill: 
                    self.particles.remove(particle)

        for i in range(len(self.player.lives)):
            self.display.blit(self.assets['player'], self.player.lives[i])
        self.tilemap.render(self.display)
        for centi in self.centipedes:
            centi['head'].render(self.display)
            for segment in centi['body']:
                segment.render(centi['head'], self.display)

        if self.dead:
            self.dead += 1
            overlay = pygame.Surface(self.display.get_size())
            overlay.set_alpha(125)
            overlay.fill((0, 0, 0))
            self.display.blit(overlay, (0,0))
            
            draw_text(self.display, self.font, "GAME OVER", self.display.get_width()//2 - 40, self.display.get_height()//2 - 30, (255, 0, 0))
            draw_text(self.display, self.font, f"FINAL SCORE: {self.score}", self.display.get_width()//2 - 55, self.display.get_height()//2 - 10, (255, 255, 255))
            
            if self.dead > 120:
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    draw_text(self.display, self.font, "PRESS SPACE TO RESTART", self.display.get_width()//2 - 100, self.display.get_height()//2 + 25, self.current_color)

        screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
        self.surface.blit(pygame.transform.scale(self.display, self.surface.get_size()), screenshake_offset)
        