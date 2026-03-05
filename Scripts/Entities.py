import pygame, random, math
 
class PhysicsEntity():
    def __init__(self, game, e_type, position, size):
        self.game = game
        self.type = e_type
        self.size = size
        self.pos = list(position)
        self.velocity = [0, 0]
        self.collisions = {'right': False, 'left': False, 'up': False, 'down': False}

        self.action = ''
        self.flip = False

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
    
    def update(self, tilemap, movement = (0,0)):
        self.collisions = {'right': False, 'left': False, 'up': False, 'down': False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        self.animation.update()
    
    def render(self, surf):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), self.pos)

class CentipedeHead(PhysicsEntity):
    def __init__(self, game, position, speed):
        super().__init__(game, 'centipede/head', position, (8, 8))
        self.direction = random.choice((-1, 1))
        self.speed = speed
        self.history = []
        self.is_tilting = False
        self.change = 1
        self.flip = True if self.direction == 1 else False
        self.falling = False
        self.poisoned = False
        self.zigzag_timer = 0
        self.set_action('idle')

    def update(self, tilemap):
        for tile in tilemap.tiles_around(self.pos):
            tile = tilemap.tilemap[f"{tile['pos'][0]};{tile['pos'][1]}"]
            if tile['type'] == 'poison_m':
                self.poisoned = True
                self.falling = True

        if self.poisoned:
            self.pos[1] += self.speed * 1.5 
            self.zigzag_timer += 0.5
            self.pos[0] += math.sin(self.zigzag_timer) * 2
            
            if self.pos[1] >= self.game.display.get_height() - 24:
                self.poisoned = False
                self.falling = False
                self.pos[1] = (self.pos[1] // 8) * 8
        else:
            movement = (self.direction * self.speed, 0)
            super().update(tilemap, movement)

            self.pos[1] = round(self.pos[1] / 8) * 8

            wall_hit = self.pos[0] < 14 or self.pos[0] + self.size[0] > self.game.display.get_width() - 14
            
            if self.collisions['right'] or self.collisions['left'] or wall_hit:
                self.direction *= -1
                self.flip = not self.flip
                self.is_tilting = True
                self.set_action('tilt')

                super().update(tilemap, movement=(0, 8 * self.change))
                if self.collisions['down'] or self.collisions['up']:
                    super().update(tilemap, movement=(0, 16 * self.change))

            else:
                self.is_tilting = False
                self.set_action('idle')

            if self.pos[1] + self.size[1] >= self.game.display.get_height() - 25 and self.change == 1:
                self.change = -1
            elif self.pos[1] <= 25 and self.change == -1:
                self.change = 1

        self.history.append({'pos': list(self.pos), 'tilt': self.is_tilting})

        if len(self.history) > 200:
            self.history.pop(0)

    def render(self, surf):
        if self.falling:
            surf.blit(pygame.transform.rotate(self.animation.img(), 90), self.pos)
        else:
            super().render(surf)

class CentipedeBody(PhysicsEntity):
    def __init__(self, game, position):
        super().__init__(game, 'centipede/body', position, (8, 8))
        self.current_tilt = False
        self.lerp_factor = 0
        self.set_action('idle')

    def follow(self, leader, segment_index):
        base_delay = round(9 / leader.speed)
        delay = (segment_index + 1) * base_delay

        if len(leader.history) >= delay:
            data = leader.history[-delay]
            target_pos = data['pos']

            dx = target_pos[0] - self.pos[0]
            dy = target_pos[1] - self.pos[1]

            if abs(dx) < 0.1:
                self.pos[0] = target_pos[0]
            else:
                self.pos[0] += dx * self.lerp_factor * leader.speed

            if abs(dy) < 0.1:
                self.pos[1] = target_pos[1]
            else:
                self.pos[1] += dy * self.lerp_factor * leader.speed

            if data['tilt']:
                self.set_action('tilt')
            else:
                self.set_action('idle')

        self.animation.update()

    def render(self, leader, surf):
        self.flip = leader.flip
        if leader.falling:
            surf.blit(pygame.transform.rotate(self.animation.img(), 90), self.pos)
        else:
            super().render(surf)

class Player(PhysicsEntity):
    def __init__(self, game, position, size):
        super().__init__(game, 'player', position, size)
        self.lives = [(452 + (self.game.assets['player'].get_width() * (i)), 15) for i in range(3)]
        self.set_action('idle')

    def add_life(self):
        self.lives.append((452 + (self.game.assets['player'].get_width() * (len(self.lives))), 15))

    def shoot(self):
        self.set_action('fire')
        self.game.projectiles.append([[self.rect().centerx, self.rect().centery], 5, 0])

    def update(self, tilemap, movement = (0, 0)):
        self.set_action('idle')
        if movement[0] != 0:
            self.velocity[0] += movement[0] * 0.4
            self.velocity[0] = max(-2, min(self.velocity[0], 2))
        else:
            if self.velocity[0] > 0:
                self.velocity[0] = max(0, self.velocity[0] - 0.5)
            elif self.velocity[0] < 0:
                self.velocity[0] = min(0, self.velocity[0] + 0.5)

        if (movement[0] > 0 and self.velocity[0] < 0) or (movement[0] < 0 and self.velocity[0] > 0):
            self.velocity[0] = 0

        super().update(tilemap, movement)

        if self.pos[0] < 14:
            self.pos[0] = 14
        if self.pos[0] > self.game.display.get_width() - 14 - self.size[0]:
            self.pos[0] = self.game.display.get_width() - 14 - self.size[0]
        if self.pos[1] < self.game.display.get_height() * 0.75:
            self.pos[1] = self.game.display.get_height() * 0.75
        if self.pos[1] > self.game.display.get_height() - 14 - self.size[1]:
            self.pos[1] = self.game.display.get_height() - 14 - self.size[1]

    def render(self, surf):
        super().render(surf)


class Spider(PhysicsEntity):
    def __init__(self, game, position):
        super().__init__(game, 'spider', position, (15, 8))
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        self.speed = random.uniform(1.0, 2.0)
        self.set_action('idle')
        
        # Área de movimiento limitada al área del jugador
        self.min_x = 14
        self.max_x = game.display.get_width() - 14
        self.min_y = game.display.get_height() - (96 + 14)
        self.max_y = game.display.get_height() - 14
        
        # Timer para cambios de dirección aleatorios
        self.direction_timer = random.randint(30, 90)
    
    def update(self, tilemap):
        # Movimiento diagonal
        movement = (self.direction[0] * self.speed, self.direction[1] * self.speed)
        super().update(tilemap, movement)
        
        # Verificar límites del área del jugador
        if self.pos[0] < self.min_x:
            self.pos[0] = self.min_x
            self.direction[0] *= -1
        elif self.pos[0] + self.size[0] > self.max_x:
            self.pos[0] = self.max_x - self.size[0]
            self.direction[0] *= -1
            
        if self.pos[1] < self.min_y:
            self.pos[1] = self.min_y
            self.direction[1] *= -1
        elif self.pos[1] + self.size[1] > self.max_y:
            self.pos[1] = self.max_y - self.size[1]
            self.direction[1] *= -1
        
        # Cambio aleatorio de dirección
        self.direction_timer -= 1
        if self.direction_timer <= 0:
            if random.random() < 0.5:
                self.direction[0] *= -1
            if random.random() < 0.5:
                self.direction[1] *= -1
            self.direction_timer = random.randint(30, 90)
        
        # Eliminar hongos al pasar sobre ellos
        # Verificar las 4 esquinas del rectángulo de la araña
        corners = [
            (self.pos[0], self.pos[1]),  
            (self.pos[0] + self.size[0], self.pos[1]),  
            (self.pos[0], self.pos[1] + self.size[1]),  
            (self.pos[0] + self.size[0], self.pos[1] + self.size[1])
        ]
        
        for corner in corners:
            grid_x = int(corner[0] // tilemap.tile_size)
            grid_y = int(corner[1] // tilemap.tile_size)
            tile_loc = str(grid_x) + ';' + str(grid_y)
            
            if tile_loc in tilemap.tilemap:
                del tilemap.tilemap[tile_loc]
        
        self.animation.update()
    
    def render(self, surf):
        super().render(surf)

class Flea(PhysicsEntity):
    def __init__(self, game, position):
        super().__init__(game, 'flea', position, (9, 8))
        self.speed = 3.0  # Velocidad más rápida
        self.set_action('idle')
        self.mushroom_drop_timer = 0
        
    def update(self, tilemap):
        # Movimiento vertical hacia abajo SIN colisiones con hongos
        self.pos[0] = (int(self.pos[0]) // 8) * 8
        self.pos[1] += self.speed
        
        # Generar hongos mientras cae con menor probabilidad (cada 16 píxeles aproximadamente)
        self.mushroom_drop_timer += self.speed
        if self.mushroom_drop_timer >= 16:  # Cambiado de 8 a 16 para reducir frecuencia
            self.mushroom_drop_timer = 0
            
            # Probabilidad del 40% de colocar un hongo
            if random.random() < 0.4:
                grid_x = int(self.pos[0] // tilemap.tile_size)
                grid_y = int(self.pos[1] // tilemap.tile_size)
                
                # Límites del área de juego (considerando los bordes de 14 píxeles)
                min_grid_x = 2
                max_grid_x = (self.game.display.get_width() - 14) // tilemap.tile_size
                min_grid_y = 4 
                max_grid_y = (self.game.display.get_height() - 14) // tilemap.tile_size
                
                # Solo generar hongos si está dentro del área válida
                if min_grid_x <= grid_x < max_grid_x and min_grid_y <= grid_y < max_grid_y:
                    tilemap.add_mushroom([grid_x * tilemap.tile_size, grid_y * tilemap.tile_size])
        
        self.animation.update()
    
    def render(self, surf):
        surf.blit(self.animation.img(), (self.pos[0], self.pos[1]))

class Scorpion(PhysicsEntity):
    def __init__(self, game, position, direction):
        super().__init__(game, 'scorpion', position, (15, 8))
        self.direction = direction  # -1 para izquierda, 1 para derecha
        self.speed = 2.0
        self.set_action('idle')
        self.flip = True if self.direction == 1 else False
        
    def update(self, tilemap):
        # Movimiento horizontal SIN colisiones
        self.pos[0] += self.direction * self.speed
        
        # Envenenar hongos al pasar sobre ellos
        grid_x = int(self.pos[0] // tilemap.tile_size)
        grid_y = int(self.pos[1] // tilemap.tile_size)
        tile_loc = str(grid_x) + ';' + str(grid_y)
        
        if tile_loc in tilemap.tilemap:
            tile = tilemap.tilemap[tile_loc]
            if tile['type'] == 'normal_m':
                tile['type'] = 'poison_m'
        
        self.animation.update()
    
    def render(self, surf):
        super().render(surf)
