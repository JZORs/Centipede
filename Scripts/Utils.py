from pathlib import Path
import pygame, os

BASE_PATH = Path(__file__).resolve().parents[1] / "Data" / "images"

def load_image(path):
    img = pygame.image.load(path)
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(path)):
        images.append(load_image(str(path) + '/' + img_name))
    return images