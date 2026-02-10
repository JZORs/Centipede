import pygame, random 
 
class PhysicsEntity():
    def __init__(self, game, e_type, position, size):
        self.game = game
        self.type = e_type
        self.size = size
        self.pos = list(position)
        self.velocity = [0, 0]

        self.action = ''
        self.flip = False

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
    
    def update(self, tilemap, movement = (0,0)):
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                self.pos[1] = entity_rect.y
    
    def render(self, surf):
        surf.blit(self.game.assets[self.type], self.pos)

class Centipede(PhysicsEntity):
    pass

class Player(PhysicsEntity):
    def __init__(self, game, position, size):
        super().__init__(game, 'player', position, size)

    def shoot(self):
        self.game.projectiles.append([[self.rect().centerx, self.rect().centery], 5, 0])

    def update(self, tilemap, movement = (0, 0)):
        super().update(tilemap, movement)
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        entity_rect = self.rect()
        if frame_movement[0] > 0:
            self.velocity[0] = min(1.2, self.velocity[0] + 0.1)
            if entity_rect.x + self.size[0] > self.game.display.get_width() - 15:
                entity_rect.x = self.game.display.get_width() - 15 - self.size[0]
                self.pos[0] = entity_rect.x
        if frame_movement[0] < 0:
            self.velocity[0] = min(-1.2, self.velocity[0] + 0.1)
            if entity_rect.x < 15:
                entity_rect.x = 15
                self.pos[0] = entity_rect.x
        entity_rect = self.rect()
        if frame_movement[1] > 0:
            if entity_rect.y + self.size[1] > self.game.display.get_height() - 15:
                entity_rect.y = self.game.display.get_height() - 15 - self.size[1]
                self.pos[1] = entity_rect.y
        if frame_movement[1] < 0:
            if entity_rect.y < self.game.display.get_height() - (96 + 15):
                entity_rect.y = self.game.display.get_height() - (96 + 15)
                self.pos[1] = entity_rect.y
        
        if movement[0] == 0:
            self.velocity[0] = 0
        if movement[1] == 0:
            self.velocity[1] = 0

    def render(self, surf):
        super().render(surf)