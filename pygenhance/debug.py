from .__init__ import Component
class Debugger(Component):
    def __init__(self, gobj, *d):
        super().__init__(gobj)
        self.debuggers = list(d)
    def next_update(self):
        if self.debuggers:
            print('\u001b[256D', end='')
            for debugger in self.debuggers:
                print(debugger.__name__.replace('_', ' ') + ':', debugger())
            print('\u001b[' + str(len(self.debuggers)) + 'A', end='')

def Delta_Time():
    from . import time
    return time.deltatime

def Frame_Rate():
    from . import time
    if time.deltatime:
        return (1 / time.deltatime)
    else: return 0