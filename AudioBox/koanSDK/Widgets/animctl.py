import koan, color

#########################################################
#
#   Object Declare
#
#########################################################

class AnimCtl(koan.EventManager):
    def __init__(self, **argd):
        # TODO argd not used
        koan.EventManager.__init__(self)

        self.enabled = True
        self.focused = False
        self.pressed = False
        self.active = False

    def close(self):
        super(koan.EventManager, self).clear()

    def draw(self, render, r):
        render.SetTexture(None)
        render.DrawRect(*r)


