import color
from component import Component, Static

class ImageBase:
    def __init__(self):
        # property
        self.image = ''
        self.imageColor = color.white
        self.stretch = 'Fill'
        self.autoDirty(['image', 'imageColor', 'stretch'])
    
    def getTexture(self, render):
        return render.GetTexture(self.image, gamma = self.gamma)
    
    def onDraw(self, render):
        t = self.getTexture(render)
        if t:
            if self.imageColor != color.white:
                render.SetColor(*self.imageColor)
                
            render.SetTexture(t)
            if self.stretch == 'Fill':
                render.DrawRect(*self.localRect)
            elif self.stretch == 'Uniform':
                render.DrawUniformRect(t.GetSize(), self.localRect)
            elif self.stretch == 'Uniform Fill':
                render.DrawUniformFillRect(t.GetSize(), self.localRect)
            elif self.stretch == 'None':
                w, h = t.GetSize()
                x = (self.width - w) / 2
                y = (self.height - h) / 2
                render.DrawRect(x, y, x+w, y+h)
                
            if self.imageColor != color.white:
                render.SetColor(*color.white)

class Image(Static, ImageBase):
    def __init__(self, parent = None):
        Static.__init__(self, parent)
        ImageBase.__init__(self)
        self.tabStop = False

    def onDraw(self, render):
        super(Image, self).onDraw(render)
        ImageBase.onDraw(self, render)

    def setContent(self, data):
        self.image = data






if __name__ == '__main__':
    import koan
    from window import Window
    from panel import DockPanel, DockSplitter
    
    koan.init()
    
    w = Window()
    w.create(0, 0, 800, 600, True)
    w.bgColor = color.darkgray
    
    p = DockPanel(w)
    p.defaultDock = 'left'
    p.bindData('width', w, 'width', dir = '<-')
    p.bindData('height', w, 'height', dir = '<-')
    
    p1 = DockPanel(p)
    i = Image(p1)
    i.image = r'D:\Documents and Settings\chunming_su\My Documents\My Pictures\zoo\DSCF0423.jpg'
    i.stretch = 'Uniform'
    DockSplitter(p1).bgColor = color.black
    i = Image(p1)
    i.image = r'D:\Documents and Settings\chunming_su\My Documents\My Pictures\zoo\DSCF0423.jpg'
    i.stretch = 'Fill'
    
    DockSplitter(p).bgColor = color.black
    
    p2 = DockPanel(p)
    i = Image(p2)    
    i.image = r'D:\Documents and Settings\chunming_su\My Documents\My Pictures\zoo\DSCF0423.jpg'
    i.stretch = 'Uniform Fill'
    DockSplitter(p2).bgColor = color.black    
    i = Image(p2)
    i.image = r'D:\Documents and Settings\chunming_su\My Documents\My Pictures\zoo\DSCF0423.jpg'

    
    w.show()
    
    koan.run(1)
    
    koan.final()