__doc__ = """Here is an example:
    ```python
    %s
    ```""" % (
    open(__file__[:-11] + '__main__.py').read().replace('\n', '\n    ')
)
__version__ = '0.0.1'

import sys
import pygame
from pygame import *
import math
from gameobjects.vector2 import Vector2

class ObjectDisposedError(RuntimeError): pass
from . import time

class Game:
    def __init__(self, screenpw=(), screenkw={}, frame_rate=None):
        pygame.init()
        self.screendata = screenpw, screenkw
        self._closed = False
        self.frame_rate = frame_rate
    def mainloop(self, scene):
        if self._closed:
            raise ObjectDisposedError('Game has already been run and cannot be run again.')
        self.screen = pygame.display.set_mode(*self.screendata[0], **self.screendata[1])
        timer = pygame.time.Clock()
        if self.frame_rate is not None:
            tickfunc = (lambda f=self.frame_rate: timer.tick(f))
        else:
            tickfunc = (lambda: timer.tick())
        time.framecount = 0
        scene.game = self
        for comp in self._get_comps(scene):
            comp.start()
        while True:
            if self._closed:
                self._end_mainloop()
                return
            for event in pygame.event.get():
                if event.type == QUIT:
                    self._end_mainloop()
                    return
            time.deltatime = tickfunc() / 1000
            for comp in self._get_comps(scene):
                comp.update()
            for comp in self._get_comps(scene):
                comp.next_update()
            time.framecount += 1
            pygame.display.update()
    def _end_mainloop(self):
        time.deltatime = None
        time.framecount = None
        pygame.quit()
    def _get_comps(self, scene):
        for obj in scene.recur_children():
                for component in obj.components:
                    yield component
    def close(self):
        self._closed = True

class GameObject:
    def __init__(self, parent):
        self.source = '@%x' % id(self)

        self.parent = parent
        self.parent._add_child(self)
        self.children = []
        self.components = []
        self.components.append(Transform(self))
    def __repr__(self):
        return '<GameObject in=%r from=%r>' % (self.parent, self.source)
    def recur_children(self):
        for child in self.children:
            yield child
            for sub_child in child.recur_children():
                yield sub_child
    def _add_child(self, child):
        self.children.append(child)
    def dispose(self, recursive=False):
        self.parent = None
        if recursive:
            for child in self.recur_children():
                child.dispose(recursive)
        self.children = []
        self.components = []
    def __del__(self): self.dispose(True)
    def add_component(self, cls):
        if cls is Transform: raise TypeError
        self.components.append(cls(self))
    def has_component(self, cls):
        for c in self.components:
            if isinstance(c, cls):
                return True
        return False
    def get_component(self, cls):
        for c in self.components:
            if isinstance(c, cls):
                return c
        raise ValueError
    def del_component(self, cls):
        if cls is Transform: raise TypeError
        for (i, c) in enumerate(self.components):
            if isinstance(c, cls):
                del self.components[i]
                return
        raise ValueError
    @property
    def transform(self):
        return self.get_component(Transform)
    def get_scene(self):
        if isinstance(self.parent, Scene):
            return self.parent
        else: return self.parent.get_scene()

class Component:
    def awake(self): pass
    def start(self): pass
    def update(self): pass
    def next_update(self): pass
    def __init__(self, gobj):
        "Use obj.add_component(Component), no need to ever call __init__ directly."
        self.source = '@%x' % id(self)

        self.parent = gobj
        self.awake()
    def __repr__(self):
        return '<Component type=%s in=%r from=%r>' % (self.__class__.__qualname__, self.parent, self.source)
    @property
    def scene(self):
        return self.parent.get_scene()
    @property
    def game(self):
        return self.scene.game
    def __getattr__(self, name):
        return getattr(self.parent, name)
    def __setattr__(self, name, value):
        if name == 'transform':
            setattr(self.parent, name, value)
        else: object.__setattr__(self, name, value)

class Behaviour(Component):
    pass

class Transform(Component):
    def __init__(self, gobj):
        super().__init__(gobj)
        self.position = Vector2()
        self.rotation = 0.0
        self.scale = Vector2()

from ._sprite import *

class Scene:
    def __init__(self):
        self.source = '@%x' % id(self)

        GameObject(self)
        self.game = None
    def __repr__(self):
        return '<Scene in=%r from=%r>' % (self.game, self.source)
    def _add_child(self, child):
        if not hasattr(self, 'ROOT'):
            self.ROOT = child
        else:
            self.ROOT._add_child(child)
    def recur_children(self):
        yield self.ROOT
        for x in self.ROOT.recur_children(): yield x
    def get_root_object(self):
        return self.ROOT
    def get_debugger(self):
        from . import debug
        if not self.ROOT.has_component(debug.Debugger):
            self.ROOT.add_component(debug.Debugger)
        return self.ROOT.get_component(debug.Debugger)
    def dispose(self, recursive=1):
        if recursive:
            self.ROOT.dispose(recursive-1)
        del self.ROOT

_globals = dir()
_pygame = dir(sys.modules['pygame'])
__all__ = []
for x in _globals:
    if x[0] != '_':
        if x not in _pygame:
            __all__.append(x)
del x
# __all__ = [x for x in _globals if not x in _pygame or x[0] != '_']