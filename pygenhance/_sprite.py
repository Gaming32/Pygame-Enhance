import pygame
from pygame.locals import *
import pygenhance
class Sprite(pygenhance.Component):
    def __init__(self, gobj, surface):
        super().__init__(gobj)
        self.surface = surface
    def update(self):
        self.game.screen.blit(self.surface, self.transform.as_tuple())