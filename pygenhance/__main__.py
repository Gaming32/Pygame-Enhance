import pygenhance
import pygenhance.debug as debug
game = pygenhance.Game([(640, 480)])
scene = pygenhance.Scene()
deb = scene.get_debugger()
#scene.get_debugger().debuggers.append(debug.Delta_Time)
#scene.get_debugger().debuggers.append(debug.Frame_Rate)
obj = pygenhance.GameObject(scene)
surf = pygenhance.Surface((250, 250))
surf.fill((255, 255, 255))
comp = pygenhance.Sprite(obj, surf)
obj.children.append(surf)
obj.transform.position = pygenhance.Vector2(100, 100)
game.mainloop(scene)