import color
from component import Component, Static


class TextBase:
    def __init__(self):
        # property
        self.font = ''
        self.fontSize = 12
        self.fontColor = color.black
        self.align = 'L'
        self.text = ''
        self.__textSize = 0, 0

        assert isinstance(self, Component)
        self.changeEvent('text', self.__onTextChanged)
        self.autoDirty( ['text', 'font', 'fontSize', 'fontColor', 'align'] )

    def __getTexPosition(self):
        return self.localRect
    textPos = property(__getTexPosition)
    
    def __onTextChanged(self):
        self.__textSize = self.calTextSize(self.text, self.font, self.fontSize)
    
    def __getTextSize(self):
        return self.__textSize
    textSize = property(__getTextSize)

    def setContent(self, data):
        self.text = data
        
    def getContent(self):
        return self.text

    def onDraw(self, render, pos = None):
        if not pos:
            pos = self.textPos
        render.DrawTextEx(self.getContent(), pos, self.align, self.fontSize, self.fontColor, self.font)

class Text(Static, TextBase):
    def __init__(self, parent = None):
        Static.__init__(self, parent)
        TextBase.__init__(self)
        self.tabStop = False

        # property
        self.autosize = False
        
        # binding
        self.changeEvent('text', self.onAutoSize)

    def onAutoSize(self):
        if self.autosize:
            self.size = self.textSize
        
    def onDraw(self, render):
        super(Text, self).onDraw(render)
        TextBase.onDraw(self, render)


        
if __name__ == '__main__':
    import koan
    from window import Window
        
    koan.init()
    
    w = Window()
    w.create(0, 0, 800, 600, caption = True)
    w.bgColor = color.darkblue    
    
    t = Text(w)
    t.text = 'Hello world'
    t.font = 'aSegoe UI'
    t.autosize = True
    t.bgColor = color.white
    t.fontSize = 30
    t.fontColor = color.black
    
    w.show()
    
    koan.run(1)
    koan.final()


