import pygenhance
# import pygenhance.debug as debug
import pygenhance.time as time
game = pygenhance.Game([(640, 480)])
scene = pygenhance.Scene()
# deb = scene.get_debugger()
#scene.get_debugger().debuggers.append(debug.Delta_Time)
#scene.get_debugger().debuggers.append(debug.Frame_Rate)
obj = pygenhance.GameObject(scene)
# surf = pygenhance.Surface((250, 250))
# surf.fill((255, 255, 255))
# comp = pygenhance.Sprite(obj, surf)
# obj.components.append(comp)
# obj.add_component(pygenhance.make_color_sprite(size=(250, 250)))
# obj.add_component(pygenhance.make_text_sprite(text="Josiah's Dad loves his family", font='Corbel', fontsize=25))
obj.add_component(pygenhance.make_image_sprite(r"c:\users\josia\pictures\dat dat dat.png", size=(153, 55)))
width = obj.get_component(pygenhance.Sprite).surface.get_width()
obj.transform.position = pygenhance.Vector2(100, 100)
class test(pygenhance.Behaviour):
    def update(self):
        self.transform.position.x += 50 * time.deltatime
        if self.transform.position.x > 640:
            self.transform.position.x = -width
        print(self.transform.position, end='\r')
obj.add_component(test)
game.mainloop(scene)