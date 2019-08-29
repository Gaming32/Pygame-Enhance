"""Pygenhance is short for Pygame Enhance. Pygenhance exports a Unity-like interface for making
games. It uses Pygame internally."""

__doc__ += """\nHere is an example:
    %s""" % (
    open(__file__[:-11] + '__main__.py').read().replace('\n', '\n    ')
)
__version__ = '0.0.1'

import sys
import pygame
from pygame import *
import math
from gameobjects.vector2 import Vector2

class ObjectDisposedError(RuntimeError):
    """This error occurs when an object is run through and done for (e.g. this error occurrs when a
Game object's mainloop is called after it has already been run)"""
    pass
from . import time

class Game:
    """This is the container object for running games.

Parameters
----------
screenpw : iterable
    the postional arguments to pass into Pygame's display set_mode function; a tuple as the
    resolution must be supplied as the first argument, otherwise it defaults to 640x480; if the 
    FULLSCREEN constant is passed as the second argument, the game will run in fullscreen

    examples:
        ``[(640, 480)]``
        ``[(640, 480), FULLSCREEN]``
screenkw : dict
    the keyword arguments to pass into Pygame's display set_mode function
frame_rate : number or None
    if set to None or left alone, it will default to the highest fps your computer can handle"""
    def __init__(self, screenpw=[(640, 480)], screenkw={}, frame_rate=None):
        pygame.init()
        self.screendata = screenpw, screenkw
        self._closed = False
        self.frame_rate = frame_rate
    def mainloop(self, scene):
        """Runs the game's mainloop (more commonly known as gameloop)

Parameters
----------
scene : Scene
    the scene to start with when the game is run

Raises
------
ObjectDisposedError
    if game has been run already and is trying to be run again

Warnings
--------
the game can only be run once because Pygame deinitializes after the mainloop is run once; this can
be bypassed with the following lines::
    import pygame
    game._closed = False
    pygame.init()
    game.mainloop(scene)"""
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
        """Ends the mainloop and exits the game"""
        self._closed = True

class GameObject:
    """Represents an object in a scene

Attributes
----------
parent : GameObject or Scene
    the parent object of this object
children : list
    the list of this object's children
components : list
    the list of this object's component; the component in index 0 will always be a Transform
    component
source : str
    a string describing where this object came from
    
Parameters
----------
parent : GameObject or Scene
    the parent object of this object"""
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
        """Recurs through all the children of this object"""
        for child in self.children:
            yield child
            for sub_child in child.recur_children():
                yield sub_child
    def _add_child(self, child):
        self.children.append(child)
    def dispose(self, recursive=False):
        """Deletes all references to other objects so thay can be easily garbage collected

Parameters
----------
recursive : bool
    if True, all children will also be disposed"""
        self.parent = None
        if recursive:
            for child in self.recur_children():
                child.dispose(recursive)
        self.children = []
        self.components = []
    def __del__(self): self.dispose(True)
    def add_component(self, cls):
        """Adds a new component to the object created by the specified callable; sprite functions
like create_color_sprite can be called when passed into this function (e.g.
``obj.add_component(create_color_sprite(size=(100, 100)))``)

Parameters
----------
cls

Raises
------
TypeError
    if you attempt to add an additional Transform component"""
        if cls is Transform: raise TypeError('Attempted to add an additional Transform component')
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
            self.ROOT.components = []
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
        has_root = hasattr(self, 'ROOT')
        if recursive and has_root:
            self.ROOT.dispose(recursive-1)
        self.game = None
        if has_root: del self.ROOT
    def __del__(self): self.dispose(2)

_globals = dir()
_pygame = dir(sys.modules['pygame'])
__all__ = []
for x in _globals:
    if x[0] != '_':
        if x not in _pygame:
            __all__.append(x)
del x
__all__.append('FULLSCREEN')
__all__.append('time')
__all__.append('Vector2')
# __all__ = [x for x in _globals if not x in _pygame or x[0] != '_']