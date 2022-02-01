import os
import pygame
import sys
import time

class Explosion(object):
    def __init__(self, explosion, width, height):
        self.explosionImg = explosion
        self.width = width
        self.height = height
    
    def loadExplosion(self):
        animation_frames = []
        image = pygame.image.load(self.explosionImg).convert_alpha()
        width, height = image.get_size()
        for row in range(height//self.height):
            for col in range(width//self.width):
                animation_frames.append(
                    image.subsurface((col * self.width, row * self.height, \
                    self.width,self.height)))
        return animation_frames


    def run(self,screen,location):
        timer = pygame.time.Clock()
        spritesheet = self.loadExplosion()
        running = True
        counter = 0
        t = 0
        while running: 
            if t > len(spritesheet):
                running = False
            screen.blit(spritesheet[counter], location)
            counter = (counter + 1) % len(spritesheet)
            pygame.display.update()
            t += 1
            time.sleep(0.1)


