from pygenhance import *
# import debug as debug
# game = Game([(640, 480), FULLSCREEN])
game = Game([(640, 480)])
scene = Scene()
# deb = scene.get_debugger()
#scene.get_debugger().debuggers.append(debug.Delta_Time)
#scene.get_debugger().debuggers.append(debug.Frame_Rate)
obj = GameObject(scene)
# surf = Surface((250, 250))
# surf.fill((255, 255, 255))
# comp = Sprite(obj, surf)
# obj.components.append(comp)
# obj.add_component(make_color_sprite(size=(250, 250)))
# obj.add_component(make_text_sprite(text="Josiah's Dad loves his family", font='Corbel', fontsize=25))
obj.add_component(make_image_sprite(r"c:\users\josia\pictures\dat dat dat.png", size=(153, 55)))
width = obj.get_component(Sprite).surface.get_width()
obj.transform.position = Vector2(100, 100)
class test(Behaviour):
    def update(self):
        self.transform.position.x += 50 * time.deltatime
        if self.transform.position.x > 640:
            self.transform.position.x = -width
        print(self.transform.position, end='\r')
obj.add_component(test)
game.mainloop(scene)
scene.dispose(2)