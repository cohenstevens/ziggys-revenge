import pygame
import os

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert() # converts image in pygame and makes it more efficient
    img.set_colorkey((0,0,0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)): # dynamically loads images with os.listdir, goesd through all files in that folder
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0  # tracks where ur at in the animation

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop) # bc ur passing images ur getting a reference rather than copying
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images)) # += 1 does not work bc you go outside of index # if want to loop use modulo
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1) # have to -1 bc indexing starts from 0
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)] # frame of game / duration of img # determines which img is to be shown
    
