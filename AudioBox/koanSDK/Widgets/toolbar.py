import koan
from component import Component, CaptureObject, Static
from panel import DockPanel, StackPanel, Canvas, AutoHide
from text import Text
import weakref

class Toolbar(StackPanel):
    def __init__(self, parent = None):
        StackPanel.__init__(self, parent)
        self.orientation = 'Horizontal'
        self.autosize = True

class AutoHideToolbar(Toolbar, AutoHide):
    def __init__(self, parent = None):
        Toolbar.__init__(self, parent)
        AutoHide.__init__(self)

class Captionbar(Canvas):
    def __init__(self, parent = None):
        Canvas.__init__(self, parent)
        self.enableFullscreen = True
        self.bind('Mouse Down', self.onMoveWindow)        
        self.bind('Dbl Click', self.onDblClick)

    def onDblClick(self, x, y, flag):
        if self.window and self.enableFullscreen:
            self.window.toggleFullscreen()

    def onMoveWindow(self, x, y, flag):
        if self.window:
            self.window.onMoveWindow()

class Caption(Canvas, CaptureObject):
    def __init__(self, parent = None):
        Canvas.__init__(self, parent)
        CaptureObject.__init__(self)
        self.useGlobalCapture = True
        self.__moveTarget = weakref.ref(self.parent)
        self.caption = ''

        self.bind('Capture Begin', self.onBeginMove, postevent = False)
        self.bind('Capture Offset', self.onMove, postevent = False)

    def __setMoveTarget(self, target):
        self.__moveTarget = weakref.ref(target)
    def __getMoveTarget(self):
        return self.__moveTarget()
    moveTarget = property(__getMoveTarget, __setMoveTarget)
    
    def onBeginMove(self, x, y):
        if self.moveTarget:
            self.capX, self.capY = self.moveTarget.left, self.moveTarget.top
        
    def onMove(self, x, y):
        if self.moveTarget and self.moveTarget.parent:
            l = self.capX + x
            t = self.capY + y
            self.moveTarget.left = min(max(l, 0), self.moveTarget.parent.width - self.parent.width)
            self.moveTarget.top = min(max(t, 0), self.moveTarget.parent.height - self.parent.height)




if __name__ == '__main__':
    from window import Window
    from panel import Canvas, StackPanel
    from component import Component
    from random import randint
    import color

    koan.init()

    w = Window()
    w.create(0, 0, 800, 600, True)
    w.bgColor = color.black
    
    b = Captionbar(w)
    b.bindData('width', w, 'width', dir = '<-')
    b.height = 100
    b.bgColor = color.darkblue
    
    c = StackPanel(w)
    c.bgColor = color.darkgray
    c.size = 400, 300
    
    b = Caption(c)
    #b.bindData('width', c, 'width', dir = '<-')
    b.height = 50
    b.bgColor = color.lightgray
    
    # toolbar
    b = Toolbar(c)
    b.autosize = False
    b.height = 100
    b.bgColor = color.darkblue
    
    o = Component(b)
    o.size = 64, 64
    o.bgColor = (255, randint(0,255), randint(0,255), randint(0,255))
    o = Component(b)
    o.size = 64, 64
    o.bgColor = (255, randint(0,255), randint(0,255), randint(0,255))
    o = Component(b)
    o.size = 64, 64
    o.bgColor = (255, randint(0,255), randint(0,255), randint(0,255))
    
    # autohide toolbar    
    b = AutoHideToolbar(c)
    b.autosize = False
    b.height = 100
    b.bgColor = color.darkblue
    
    o = Component(b)
    o.size = 64, 64
    o.bgColor = (255, randint(0,255), randint(0,255), randint(0,255))
    o = Component(b)
    o.size = 64, 64
    o.bgColor = (255, randint(0,255), randint(0,255), randint(0,255))
    o = Component(b)
    o.size = 64, 64
    o.bgColor = (255, randint(0,255), randint(0,255), randint(0,255))
    
    w.show()
    
    koan.run(1)
    
    koan.final()