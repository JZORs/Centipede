from pathlib import Path 
import pygame, os

BASE_PATH = Path(__file__).resolve().parents[1] / "Data"

def load_image(path):
    img = pygame.image.load(path)
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(path)):
        images.append(load_image(str(path) + '/' + img_name))
    return images

def load_sound(path):
    sound = pygame.mixer.Sound(path)
    return sound

def draw_text(surf, font, text, x, y, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    
    surf.blit(text_surface, text_rect)

class Animation:
    def __init__(self, images, img_dur = 5, loop = True):
        self.images = images
        self.img_dur = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.images, self.img_dur, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_dur * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_dur * len(self.images) - 1)
            if self.frame >= self.img_dur * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_dur)]