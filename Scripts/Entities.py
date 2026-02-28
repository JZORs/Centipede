import pygame, random 
 
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
        self.set_action('idle')

    def update(self, tilemap):
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
        self.lerp_factor = 0.2
        self.set_action('idle')

    def follow(self, leader, segment_index):
        delay = (segment_index + 1) * 4

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
        self.lives = [(455 + (self.game.assets['player'].get_width() * (i * 1.5)), 15) for i in range(3)]
        self.set_action('idle')

    def shoot(self):
        self.set_action('fire')
        self.game.projectiles.append([[self.rect().centerx, self.rect().centery], 5, 0])

    def update(self, tilemap, movement = (0, 0)):
        super().update(tilemap, movement)
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.set_action('idle')

        entity_rect = self.rect()
        if frame_movement[0] > 0:
            self.velocity[0] = min(1.2, self.velocity[0] + 0.1)
            if entity_rect.x + self.size[0] > self.game.display.get_width() - 14:
                entity_rect.x = self.game.display.get_width() - 14 - self.size[0]
                self.pos[0] = entity_rect.x
        if frame_movement[0] < 0:
            self.velocity[0] = min(-1.2, self.velocity[0] + 0.1)
            if entity_rect.x < 14:
                entity_rect.x = 14
                self.pos[0] = entity_rect.x
        entity_rect = self.rect()
        if frame_movement[1] > 0:
            if entity_rect.y + self.size[1] > self.game.display.get_height() - 14:
                entity_rect.y = self.game.display.get_height() - 14 - self.size[1]
                self.pos[1] = entity_rect.y
        if frame_movement[1] < 0:
            if entity_rect.y < self.game.display.get_height() - (96 + 14):
                entity_rect.y = self.game.display.get_height() - (96 + 14)
                self.pos[1] = entity_rect.y
        
        if movement[0] == 0:
            self.velocity[0] = 0
        if movement[1] == 0:
            self.velocity[1] = 0

    def render(self, surf):
        super().render(surf)