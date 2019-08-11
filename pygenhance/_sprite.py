import pygame
from pygame.locals import *
import pygenhance
class Sprite(pygenhance.Component):
    frame = 0
    def __init__(self, gobj, surface, startfunc=(lambda: None)):
        "Use obj.add_component(make_sprite()), no need to ever call __init__ directly."
        super().__init__(gobj)
        self.surface = surface
        self.startfunc = startfunc
    def start(self):
        if 'self' in self.startfunc.__code__.co_varnames: self.startfunc(self=self)
        else: self.startfunc()
    def update(self):
        if pygenhance.time.framecount > self.frame:
            self.frame = pygenhance.time.framecount
            self.game.screen.fill((0, 0, 0))
        self.game.screen.blit(self.surface, self.transform.position.as_tuple())

def make_color_sprite(color=(255, 255, 255), size=(1, 1)):
    surf = pygame.Surface(size)
    surf.fill(color)
    def ColorSprite(gobj, surf=surf):
        return Sprite(gobj, surf)
    return ColorSprite

def make_image_sprite(image, alpha=False, size=None):
    surf = pygame.image.load(image)
    def startfunc(self, alpha=alpha, size=size):
        if alpha: self.surface = self.surface.convert_alpha()
        else:     self.surface = self.surface.convert()
        if size: self.surface = pygame.transform.scale(self.surface, size)
    def ImageSprite(gobj, surf=surf, startfunc=startfunc):
        return Sprite(gobj, surf, startfunc)
    return ImageSprite

def make_text_sprite(text, font='calibri', fontmode='SysFont', fontsize=11, size=None, color=(255, 255, 255),
        *, antialias=True):
    fontobj = getattr(pygame.font, fontmode)(font, fontsize)
    surf = fontobj.render(text, antialias, color)
    def startfunc(self, size=size):
        if size: self.surface = pygame.transform.scale(self.surface, size)
    def TextSprite(gobj, surf=surf, startfunc=startfunc):
        return Sprite(gobj, surf, startfunc)
    return TextSprite