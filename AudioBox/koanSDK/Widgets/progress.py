
from component import Static
from text import TextBase

class Progress(Static, TextBase):
    def __init__(self, parent):
        Static.__init__(self, parent)
        TextBase.__init__(self)
        # data
        self.progress = 0.0     # 0.0 ~ 1.0
        
        # display
        self.margin = 0
        self.margin2 = 0
        self.progressImg = ''
        self.autoDirty(['progress', 'progressImg'])
        
    def onDraw(self, render):
        # draw background
        super(Progress, self).onDraw(render)
        
        # draw progress
        t = render.GetTexture(self.progressImg, gamma = self.gamma)
        render.SetTexture(t)
        margin = self.margin + self.margin2
        render.DrawRect(self.margin, self.margin,
             margin + self.margin2 + (self.width-(margin)*2) * self.progress,
             self.height-self.margin)
        
        # draw text
        #self.text = '%d%%' %int(self.progress * 100)
        TextBase.onDraw(self, render)