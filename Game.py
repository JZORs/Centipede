import pygame, random, math, sys 

from arcade_machine_sdk import GameBase, GameMeta
from Scripts.Entities import PhysicsEntity, CentipedeHead, CentipedeBody, Player, Spider, Flea, Scorpion
from Scripts.Tilemap import Tilemap
from Scripts.Particles import Particle
from Scripts.Utils import Animation, load_image, load_images, load_sound, draw_text, BASE_PATH

class Game(GameBase):
    def __init__(self, metadata = GameMeta): 
        super().__init__(metadata)

        self.display = pygame.Surface((512, 384), pygame.SRCALPHA)

        self.assets = {
            'logo': load_image(BASE_PATH / "images" / "logo.png"),
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
            'spider/idle': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "spider"), img_dur=8),
            'flea/idle': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "fleas"), img_dur=7),
            'scorpion/idle': Animation(load_images(BASE_PATH / "images" / "level_1" / "entities" / "scorpion"), img_dur=10),
            'wasd': Animation(load_images(BASE_PATH / "images" / "tutorial" / "wasd"), img_dur=12),
            'space': Animation(load_images(BASE_PATH / "images" / "tutorial" / "space"), img_dur=12),
        }

        self.logo_menu = pygame.transform.scale(self.assets['logo'], (320, 45))

        pygame.mixer.pre_init(44100, -16, 2, 2048) 

        self.sfx = {
            'mushroom': load_sound(BASE_PATH / "sounds" / "mushroom.wav"),
            'shoot': load_sound(BASE_PATH / "sounds" / "shoot.wav"),
            'get_shoot': load_sound(BASE_PATH / "sounds" / "get_shoot.wav"),
            'level_up' : load_sound(BASE_PATH / "sounds" / "level_up.wav"),
            'life_up' : load_sound(BASE_PATH / "sounds" / "life_up.wav"),
        }

        self.music = {
            'music_1': BASE_PATH / "music" / "music_1.ogg",
            'music_2': BASE_PATH / "music" / "music_2.ogg",
            'music_3': BASE_PATH / "music" / "music_3.ogg",
        }

        self.sfx['mushroom'].set_volume(0.1)
        self.sfx['get_shoot'].set_volume(0.1)
        self.sfx['shoot'].set_volume(0.1)
        self.sfx['level_up'].set_volume(0.2)
        self.sfx['life_up'].set_volume(0.2)

        self.movement = [False, False, False, False]

        self.font = pygame.font.Font(BASE_PATH / 'ADDLG___.TTF', 9)
        self.large_font = pygame.font.Font(BASE_PATH / 'ADDLG___.TTF', 100)
        self.level_display_timer = 0

        self.score = 0
        self.flag_score = 0
        self.death_timer = 0
        self.retry_timer = 0
        
        self.tilemap = Tilemap(self, tile_size = 8)
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

        self.in_menu = True
        self.menu_timer = 0

        self.game_loop = 0
        self.difficulty_level = 1
        self.level = 1

        self.screenshake = 0
        self.tutorial = True
        self.key_pressed = set()
        self.wasd_anim = self.assets['wasd'].copy()
        self.space_anim = self.assets['space'].copy()

        self.music_start = False

    def load_level(self, level):
        if level > 5:
            level = 1
            self.level = 1
            self.game_loop += 1
        
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
        self.assets['spider/idle'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "spider"), img_dur=8)
        self.assets['flea/idle'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "fleas"), img_dur=7)
        self.assets['scorpion/idle'] = Animation(load_images(BASE_PATH / "images" / f"level_{level}" / "entities" / "scorpion"), img_dur=10)

        self.current_color = self.level_borders[str(level)]
        config = random.choice(self.speed_configs)
        selected_speed = config['speed']
        selected_lerp = config['lerp']

        self.projectiles = []
        self.centipedes = []
        self.particles = []
        self.spiders = []
        self.spider_spawn_timer = random.randint(180, 420)  # 3-7 segundos a 60 FPS
        self.fleas = []
        self.flea_spawn_timer = random.randint(240, 480)  # 4-8 segundos a 60 FPS
        self.scorpions = []
        self.scorpion_spawn_timer = random.randint(300, 600)  # 5-10 segundos a 60 FPS

        initial_head = CentipedeHead(self, (256, -10), selected_speed)
        initial_segments = []
        for i in range(8):
            segment = CentipedeBody(self, (initial_head.pos[0], initial_head.pos[1] * (i + 2)))
            segment.lerp_factor = selected_lerp
            initial_segments.append(segment)

        self.centipedes.append({'head': initial_head, 'body': initial_segments})

        if level > 1 or self.game_loop >= 1:
            if self.difficulty_level < 6:
                num_extra_heads = self.difficulty_level - 1
            else:
                num_extra_heads = 6
            
            for _ in range(num_extra_heads):
                spawn_x = random.randint(20, self.display.get_width() - 20)
                
                extra_head = CentipedeHead(self, (spawn_x, -10), selected_speed + 0.5)
                self.centipedes.append({'head': extra_head, 'body': []})

        if level == 1 and self.game_loop < 1:
            self.player = Player(self, (256, 350), (9, 9))
        else:
            self.player.pos = self.player.pos
            self.player.velocity = [0, 0]
            self.player.set_action('fire')

        self.dead = 0
        self.level_display_timer = 120
    
    def reset_after_death(self):
        self.projectiles = []
        self.centipedes = []
        self.spiders = []
        self.spider_spawn_timer = random.randint(180, 420)
        self.fleas = []
        self.flea_spawn_timer = random.randint(240, 480)
        self.scorpions = []
        self.scorpion_spawn_timer = random.randint(300, 600)

        config = random.choice(self.speed_configs)
        initial_head = CentipedeHead(self, (256, -10), config['speed'])
        initial_segments = []
        for i in range(8):
            segment = CentipedeBody(self, (initial_head.pos[0], initial_head.pos[1] * (i + 2)))
            segment.lerp_factor = config['lerp']
            initial_segments.append(segment)
        
        self.centipedes.append({'head': initial_head, 'body': initial_segments})

        if self.level > 1 or self.game_loop >= 1:
            if self.difficulty_level < 6:
                num_extra_heads = self.difficulty_level - 1
            else:
                num_extra_heads = 6
            
            for _ in range(num_extra_heads):
                spawn_x = random.randint(20, self.display.get_width() - 20)
                
                extra_head = CentipedeHead(self, (spawn_x, -10), config["speed"] + 0.5)
                self.centipedes.append({'head': extra_head, 'body': []})

        self.player.pos = [256, 350]
        self.player.velocity = [0, 0]

    def draw_main_menu(self):
        logo_rect = self.logo_menu.get_rect(center=(self.display.get_width() // 2, 100))
        logo_out = self.logo_menu.get_rect(center=(self.display.get_width() // 2 - 5, 100 - 5))
        
        self.display.blit(self.logo_menu, logo_rect)

        pygame.draw.rect(self.display, (28,163,28), (6, 6, self.display.get_width() - 12, self.display.get_height() - 12), 3)
        pygame.draw.rect(self.display, (28,163,28), (logo_out.x, logo_out.y, logo_out.width + 10, logo_out.height + 10), 3, 5)
        draw_text(self.display, self.font, "1984 ATARI", logo_out.centerx - 35, logo_out.bottom + 15, (28,163,28))

        self.menu_timer += 1
        if (self.menu_timer // 30) % 2 == 0:
            draw_text(self.display, self.font, "PRESS SPACE TO START", self.display.get_width()//2 - 90, self.display.get_height()//2 + 60, (28,163,28))

    def draw_background_level(self):
        if self.level_display_timer > 0:
            alpha = min(100, self.level_display_timer * 2) 
            text_surf = self.large_font.render(f"{self.difficulty_level}", True, self.current_color)
            text_surf.set_alpha(alpha)
            
            x = (self.display.get_width() // 2) - (text_surf.get_width() // 2) + 10
            y = (self.display.get_height() // 2) - (text_surf.get_height() // 2) + 6
            
            self.display.blit(text_surf, (x, y))
            self.level_display_timer -= 1

    def handle_events(self, events: list[pygame.event.Event]):
        if self.tilemap.current_row_idx >= len(self.tilemap.rows_ordered):
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.in_menu == True:
                        if event.key == pygame.K_SPACE:
                            self.in_menu = False
                            self.sfx['life_up'].play()
                            self.tilemap.generate_map(70)
                            self.music_start = False
                            self.tutorial = True
                            self.key_pressed = set()
                            self.score = 0
                            self.game_loop = 0
                            self.difficulty_level = 1
                            self.flag_score = 0
                            self.level = 1
                            self.load_level(self.level)
                        if event.key == pygame.K_ESCAPE:
                            GameBase.stop(self)
                    elif self.dead > 120:
                        if event.key == pygame.K_SPACE:
                            self.sfx['life_up'].play()
                            self.screenshake = max(0, self.screenshake - 0.5)
                            self.tilemap = Tilemap(self, tile_size = 8)
                            self.tilemap.generate_map(70)
                            self.music_start = False
                            self.score = 0
                            self.flag_score = 0
                            self.game_loop = 0
                            self.difficulty_level = 1
                            self.dead = 0
                            self.level = 1
                            self.load_level(1)
                        if event.key == pygame.K_ESCAPE:
                            self.in_menu = True
                            pygame.mixer.music.stop()
                    elif not self.dead >= 1 and not self.healing_mushrooms and self.death_timer == 0:
                        if event.key == pygame.K_w:
                            self.movement[0] = True
                            self.key_pressed.add('w')
                        if event.key == pygame.K_s:
                            self.movement[1] = True
                            self.key_pressed.add('s')
                        if event.key == pygame.K_a:
                            self.movement[2] = True
                            self.key_pressed.add('a')
                        if event.key == pygame.K_d:
                            self.movement[3] = True
                            self.key_pressed.add('d')
                        if event.key == pygame.K_SPACE:
                            self.key_pressed.add('space')
                            self.player.shoot()
                            self.sfx['shoot'].play()
                        if event.key == pygame.K_ESCAPE:
                            self.in_menu = True
                            pygame.mixer.music.stop()
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

        if self.in_menu:
            self.draw_main_menu()
        else:
            if self.tilemap.current_row_idx >= len(self.tilemap.rows_ordered):
                if not self.music_start:
                    pygame.mixer.music.load(random.choice(list(self.music.values())))
                    pygame.mixer.music.set_volume(0.2)
                    pygame.mixer.music.play(loops=-1)
                    self.music_start = True

                self.screenshake = max(0, self.screenshake - 0.5)
                if not self.dead:
                    required_keys = {'w', 's', 'a', 'd', 'space'}
                    if required_keys.issubset(self.key_pressed):
                        self.tutorial = False

                    if not self.healing_mushrooms and self.death_timer == 0:
                        self.player.update(self.tilemap, (self.movement[3] - self.movement[2], self.movement[1] - self.movement[0]))
                        
                    if not self.tutorial:
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

                        # Sistema de aparición aleatoria de arañas
                        self.spider_spawn_timer -= 1
                        if self.spider_spawn_timer <= 0:
                            if len(self.spiders) == 0:
                                # Aparecer araña desde un lado aleatorio
                                side = random.choice(['left', 'right'])
                                if side == 'left':
                                    spider_x = 14
                                    spider_y = random.randint(self.display.get_height() - 100, self.display.get_height() - 30)
                                else:
                                    spider_x = self.display.get_width() - 22
                                    spider_y = random.randint(self.display.get_height() - 100, self.display.get_height() - 30)
                                
                                self.spiders.append(Spider(self, (spider_x, spider_y)))
                                self.spider_spawn_timer = random.randint(300, 600)  # 5-10 segundos
                            else:
                                # Si ya hay una araña, esperar menos tiempo para revisar
                                self.spider_spawn_timer = random.randint(240, 560)

                        # Actualizar arañas
                        for spider in self.spiders[:]:
                            spider.update(self.tilemap)

                        # Sistema de aparición aleatoria de moscas (solo desde nivel 2)
                        if self.level >= 2 or self.game_loop >= 1:
                            self.flea_spawn_timer -= 1
                            if self.flea_spawn_timer <= 0 and len(self.tilemap.tilemap) < 70:
                                # Aparecer mosca aleatoriamente
                                # Posición X aleatoria cada vez
                                flea_x = random.randint(20, self.display.get_width() - 20) 
                                self.fleas.append(Flea(self, (flea_x, 10)))
                                
                                # Reiniciar timer para la próxima aparición
                                self.flea_spawn_timer = random.randint(240, 480)

                        # Actualizar moscas
                        for flea in self.fleas[:]:
                            flea.update(self.tilemap)
                            # Eliminar mosca si sale de la pantalla
                            if flea.pos[1] > self.display.get_height():
                                self.fleas.remove(flea)

                        # Sistema de aparición aleatoria de escorpiones (solo desde nivel 3)
                        if self.level >= 3 or self.game_loop >= 1:
                            self.scorpion_spawn_timer -= 1
                            if self.scorpion_spawn_timer <= 0:
                                min_y = 4
                                max_y = (self.display.get_height() - (96 + 14)) // self.tilemap.tile_size
                                
                                # Intentar encontrar una fila con espacio
                                available_rows = []
                                for y in range(min_y, max_y):
                                    # Contar hongos en esta fila
                                    mushrooms_in_row = 0
                                    for loc in self.tilemap.tilemap:
                                        tile = self.tilemap.tilemap[loc]
                                        if tile['pos'][1] == y:
                                            mushrooms_in_row += 1
                                    
                                    # Si la fila tiene espacio (menos de 50 hongos), es válida
                                    if mushrooms_in_row < 50:
                                        available_rows.append(y)
                                
                                # Si hay filas disponibles, crear escorpión
                                if available_rows:
                                    chosen_row = random.choice(available_rows)
                                    # Elegir lado aleatorio (izquierda o derecha)
                                    side = random.choice(['left', 'right'])
                                    if side == 'left':
                                        scorpion_x = 10
                                        direction = 1  # Moverse a la derecha
                                    else:
                                        scorpion_x = self.display.get_width() - 18
                                        direction = -1  # Moverse a la izquierda
                                    
                                    scorpion_y = chosen_row * self.tilemap.tile_size
                                    self.scorpions.append(Scorpion(self, (scorpion_x, scorpion_y), direction))
                                
                                # Reiniciar timer
                                self.scorpion_spawn_timer = random.randint(300, 600)

                        # Actualizar escorpiones
                        for scorpion in self.scorpions[:]:
                            scorpion.update(self.tilemap)
                            # Eliminar escorpión si sale de la pantalla
                            if scorpion.pos[0] < -10 or scorpion.pos[0] > self.display.get_width() + 10:
                                self.scorpions.remove(scorpion)

                    collision_detected = False
                    
                    for centi in self.centipedes[:]:
                        if centi['head'].rect().colliderect(self.player.rect()):
                            collision_detected = True
                        for segment in centi['body']:
                            if segment.rect().colliderect(self.player.rect()):
                                collision_detected = True
                        if collision_detected:
                            break

                    # Verificar colisiones con arañas
                    if not collision_detected:
                        for spider in self.spiders[:]:
                            if spider.rect().colliderect(self.player.rect()):
                                collision_detected = True
                                break
                    
                    # Verificar colisiones con moscas
                    if not collision_detected:
                        for flea in self.fleas[:]:
                            if flea.rect().colliderect(self.player.rect()):
                                collision_detected = True
                                break
                    
                    # Verificar colisiones con escorpiones
                    if not collision_detected:
                        for scorpion in self.scorpions[:]:
                            if scorpion.rect().colliderect(self.player.rect()):
                                collision_detected = True
                                break

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
                            self.spiders = []
                            self.fleas = []  
                            self.scorpions = []  
                            self.healing_mushrooms = True 
                    
                    if self.healing_mushrooms:
                        found_damaged = False
                        self.spiders = []
                        self.fleas = []  
                        self.scorpions = []  
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
                        pygame.mixer.music.fadeout(2000)
                        self.player.pos = [-1000, -1000]
                        self.projectiles = []
                    
                    if len(self.centipedes) == 0 and not self.dead and self.death_timer == 0 and not self.healing_mushrooms:
                        self.sfx['level_up'].play()
                        self.screenshake = max(25, self.screenshake)
                        self.level += 1
                        self.difficulty_level += 1
                        self.load_level(self.level)

                    for projectile in self.projectiles[:]:
                        projectile[0][1] -= projectile[1]
                        img = self.assets['projectile']
                        self.display.blit(img, (projectile[0][0] - img.get_width() / 2 + 1, projectile[0][1] - img.get_height() / 2))
                        was_removed = False
                        if self.tilemap.solid_check(projectile[0]):
                            tile = self.tilemap.solid_check(projectile[0])
                            self.projectiles.remove(projectile)
                            was_removed = True
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
                                was_removed = True

                        if not was_removed:
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
                            else:
                                # Verificar colisiones con arañas
                                for spider in self.spiders[:]:
                                    if spider.rect().colliderect(proj_rect):
                                        for _ in range(20):
                                            angle = random.random() * math.pi * 2
                                            speed = random.random() * 5
                                            self.particles.append(Particle(self, 'centipede', spider.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                                        self.score += 250
                                        self.flag_score += 250
                                        self.spiders.remove(spider)
                                        if projectile in self.projectiles:
                                            self.projectiles.remove(projectile)
                                        self.sfx['get_shoot'].play()
                                        hit_something = True
                                        break
                                
                                # Verificar colisiones con moscas
                                if not hit_something:
                                    for flea in self.fleas[:]:
                                        if flea.rect().colliderect(proj_rect):
                                            for _ in range(15):
                                                angle = random.random() * math.pi * 2
                                                speed = random.random() * 5
                                                self.particles.append(Particle(self, 'centipede', flea.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                                            self.score += 100
                                            self.flag_score += 100
                                            self.fleas.remove(flea)
                                            if projectile in self.projectiles:
                                                self.projectiles.remove(projectile)
                                            self.sfx['get_shoot'].play()
                                            break
                                
                                # Verificar colisiones con escorpiones
                                if not hit_something:
                                    for scorpion in self.scorpions[:]:
                                        if scorpion.rect().colliderect(proj_rect):
                                            for _ in range(20):
                                                angle = random.random() * math.pi * 2
                                                speed = random.random() * 5
                                                self.particles.append(Particle(self, 'centipede', scorpion.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                                            self.score += 500
                                            self.flag_score += 500
                                            self.scorpions.remove(scorpion)
                                            if projectile in self.projectiles:
                                                self.projectiles.remove(projectile)
                                            self.sfx['get_shoot'].play()
                                            break

    def render(self):
        if not self.in_menu:
            if not self.dead and self.death_timer == 0 and not self.healing_mushrooms:
                self.player.render(self.display)

            if not self.dead:
                score_str = f"{self.score:03d}"
                draw_text(self.display, self.font, "SCORE:", 16, 16, self.current_color)
                draw_text(self.display, self.font, score_str, 75, 16, self.current_color)
                draw_text(self.display, self.font, "LIVES:", 400, 16, self.current_color)

            self.draw_background_level()

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

            for spider in self.spiders:
                spider.render(self.display)
            
            for flea in self.fleas:
                flea.render(self.display)

            for scorpion in self.scorpions:
                scorpion.render(self.display)

            if self.tilemap.current_row_idx >= len(self.tilemap.rows_ordered):
                if self.tutorial:
                    self.display.blit(self.wasd_anim.img(), (self.player.pos[0] - 50, self.player.pos[1] - (self.player.size[1] + 3.5)))
                    self.display.blit(self.space_anim.img(), (self.player.pos[0] + 25, self.player.pos[1] - (self.player.size[1] - 2)))
                    self.wasd_anim.update()
                    self.space_anim.update()

            if self.dead:
                self.dead += 1
                overlay = pygame.Surface(self.display.get_size())
                overlay.set_alpha(125)
                overlay.fill((0, 0, 0))
                self.display.blit(overlay, (0,0))
                
                draw_text(self.display, self.font, "GAME OVER", self.display.get_width()//2 - (self.font.size("GAME OVER")[0]//2), self.display.get_height()//2 - 40, (255, 0, 0))
                draw_text(self.display, self.font, "FINAL SCORE:", self.display.get_width()//2 - (self.font.size("FINAL SCORE:")[0]//2), self.display.get_height()//2 - 20, (255, 255, 255))
                draw_text(self.display, self.font, str(self.score), self.display.get_width()//2 - (self.font.size(str(self.score))[0]//2), self.display.get_height()//2, (255, 255, 255))
                
                if self.dead > 120:
                    if (pygame.time.get_ticks() // 500) % 2 == 0:
                        draw_text(self.display, self.font, "PRESS SPACE TO RESTART", self.display.get_width()//2 - (self.font.size("PRESS SPACE TO RESTART")[0]//2), self.display.get_height()//2 + 30, self.current_color)

        screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
        self.surface.blit(pygame.transform.scale(self.display, self.surface.get_size()), screenshake_offset)
        