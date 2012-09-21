import color
from component import Component, CaptureObject, clamp
from image import ImageBase
from button import Button
import koan

#---------------------------
# Thumb
#---------------------------
class Thumb(Button, CaptureObject):
    def __init__(self, parent = None):
        Button.__init__(self, parent)
        CaptureObject.__init__(self)
        self.useGlobalCapture = True
        self.tabStop = False

#---------------------------
# Slider
#---------------------------
class Slider(Component):
    '''
    event:
        Slide Start             -> drag
        Slide End               -> drop
        Slide To (value)        -> click
        Slide (value)           -> value change
    '''
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        self.vertical = False

        # range
        self.__valueStart = 0
        self.__valueEnd = 1
        
        # value
        self.__value = 0
        
        # snap
        self.snap = 0
                
        # thumb
        self.thumb = Thumb(self)
        self.bindData('gamma', self.thumb, 'gamma', dir = '->')
        self._thumbStartAnim = koan.anim.AnimTarget('decay', 0, 0, 0, self)
        self.thumbImage = ''
        self.thumbEffect = None
        #self.bindData('thumbImage', self.thumb, 'background')
        self.autoDirty( ['thumbImage'] )

        # drag / drop thumb
        # self.changeEvent('snap', self.__updateValue)
        self.autoRemove( self.thumb.bind('Capture Begin', self.onSlideStart) )
        self.autoRemove( self.thumb.bind('Capture Offset', self.onSlideMove) )
        self.autoRemove( self.thumb.bind('Capture End', self.onSlideStop) )
        # click to
        self.bind('Mouse Down', self.onSlideTo)

        self.__updateThumbSize()
        self.bind('Size Change', self.__updateThumbSize)
    
    def close(self):
        if self.thumbEffect:
            self.thumbEffect.close()
            self.thumbEffect = None
        super(Slider, self).close()

    #----------------------- property ------------------------------    
    def getRange(self):
        return self.__valueStart, self.__valueEnd
    def setRange(self, r):
        self.__valueStart = r[0]
        self.__valueEnd = r[1]
        self.__updateValue()
    valueRange = property(getRange, setRange)
    
    def setValue(self, value, forceChangeEvent = False):
        oldValue = self.__value
        self.fixValue(value, True)
        if oldValue != value or forceChangeEvent:
            self.invoke('Slide', self.__value)
    def getValue(self):
        return self.__value
    value = property(getValue, setValue)
    
    def fixValue(self, value, force = False):
        if (force or not self.thumb._CaptureObject__capture) and value != self.__value:
            self.__value = value
            self.__updateThumbPos()
    
    
    #------------------------- method -----------------------------
    #def setValue(self, value):
    #    self.value = clamp(self.__valueStart, value, self.__valueEnd)
    #    self.__updateThumbPos()

    def __setThumbStart(self, v):
        if self.vertical:   self.thumb.top = v
        else:               self.thumb.left = v
    def __getThumbStart(self):
        return self.thumb.top if self.vertical else self.thumb.left
    thumbStart = property(__getThumbStart, __setThumbStart)
    
    def __updateValue(self):
        r = float(self.__valueEnd - self.__valueStart)
        pos = self.thumbStart
        if self.__end > 0:
            pos = float(pos) / self.__end * r
            if self.snap > 0:
                grad = map( lambda x: self.__valueStart+ x*r/self.snap, range(self.snap+1) )
                intval = float(r)/self.snap
                v = pos + intval/2
                self.value = grad[int(v/intval)]
            else:
                self.value = self.__valueStart + pos            
        else:
            self.value = self.__valueStart
    
    def __updateThumbPos(self):
        r = self.__valueEnd - self.__valueStart
        pos = (float(self.value) - self.__valueStart) / r
        self.thumbStart = pos * (self.__end - self.__start)
        self._thumbStartAnim.ForceAssign(int(self.thumbStart))

    def __updateThumbSize(self):
        if self.vertical:
            #w, e = self.width, self.height
            w, e = self.thumbHeight if hasattr(self, 'thumbHeight') else self.width, self.height
            self.thumb.width = self.width
            self.thumb.height = w
        else:
            #w, e = self.height, self.width
            w, e = self.thumbWidth if hasattr(self, 'thumbWidth') else self.height, self.width
            self.thumb.width = w
            self.thumb.height = self.height
            
        self.__start = 0
        self.__end = e - w
        self.__updateThumbPos()

    def onSlideStart(self, x, y):
        self.__capPos = self.thumbStart
        self.invoke('Slide Start')

    def onSlideMove(self, x, y):
        self.thumbStart = clamp(self.__start, self.__capPos + (y if self.vertical else x), self.__end)
        self._thumbStartAnim.ForceAssign(int(self.thumbStart))
        if self.snap == 0:
            self.__updateValue()

    def onSlideStop(self, x, y):
        if self.snap > 0:
            self.__updateValue()
            self.__updateThumbPos()
        self.invoke('Slide To', self.__value)
        self.invoke('Slide End')

    def onSlideTo(self, x, y, flag):
        self.thumbStart = clamp(self.__start, (y - self.thumb.height / 2) if self.vertical else (x - self.thumb.width / 2), self.__end)
        if self.snap > 0:
            self.__updateValue()
            self.__updateThumbPos()
        else:            
            self._thumbStartAnim.ForceAssign(int(self.thumbStart))
            self.__updateValue()
        self.invoke('Slide To', self.__value)
        
    def onDraw(self, render):
        super(Slider, self).onDraw(render)

        render.PushMatrix()
        if self.vertical:
            render.Translate(0, self._thumbStartAnim)
        else:
            render.Translate(self._thumbStartAnim, 0)
        
        self.onDrawThumb(render,
                self.thumb.width,
                self.thumb.height
        )
        render.PopMatrix()
        
    def onDrawThumb(self, render, w, h):
        if self.thumbEffect:
            self.thumbEffect.draw(render, w, h)
        else:
            t = render.GetTexture(self.thumbImage, gamma = self.gamma)
            render.SetTexture(t)
            render.DrawRect(0, 0, w, h)

    def onKey(self, key):        
        if self.vertical and (key == 'UP' or key == 'DOWN') or not self.vertical and (key == 'LEFT' or key == 'RIGHT'):
            interval = float(self.valueRange[1] - self.valueRange[0]) / 10
            if key == 'UP' or key == 'LEFT':
                interval = -interval
            self.value = clamp(self.valueRange[0], self.value + interval, self.valueRange[1])
            return True
        return super(Slider, self).onKey(key)


if __name__ == '__main__':
    from window import Window
    import color
    from pprint import pprint
    def kprint(*argv):
        pprint(argv)
        #print '%f : %s' %(v, msg)

    koan.init()
    
    w = Window()
    w.create(0, 0, 420, 240, caption = True)
    w.bgColor = color.darkblue        
    
    s = Slider(w)
    s.rect = 0.5, 100, 400, 100
    s.bgColor = color.green
    s.background = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\slider\zoom_bar.png|(9,0,9,0)'
    s.thumbImage = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\seekbar\seek_btn_p.png|(1,1,1,1)'
    s.thumbWidth = 20
    s.snap = 5
    s.setRange((-0.5, 0.5))
    import functools
    s.bind('Slide', functools.partial(kprint, 'Slide'))
    #s.bind('Slide To', functools.partial(kprint, 'Slide To'))
    s.bind('Slide To', lambda x: pprint(('Slide To', x)))
    
    w.show()
    
    koan.run(1)
    s = None
    w = None
    koan.final()
    koan.traceLeak()

