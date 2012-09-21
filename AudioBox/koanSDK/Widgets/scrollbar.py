import color
from component import Component, CaptureObject, clamp
import koan

animTime = 0.3

class ScrollBar(Component, CaptureObject):
    '''
    events:
        - Scroll (offset)
    '''
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        CaptureObject.__init__(self)
        self.vertical = True
                
        self.autoHide = False        
        self.setRange(100, 10)
        self.changeEvent('autoHide', self.__fixVisible)
        self.changeEvent('fullSize', self.__fixVisible)
        self.changeEvent('viewSize', self.__fixVisible)
        
        self.__offset = 0        # 0 ~ 1
        self.thumbEffect = None
        self.thumbMinSize = 50
        self.thumbImage = ''
        self.isMouseOverThumb = False
        self.capture = False

        self.autoDirty( ['viewSize', 'fullSize', 'thumbImage'] )
        self.changeEvent('fullSize', self.__fixScroll)
        self.changeEvent('viewSize', self.__fixScroll)        
        
        self.bind('Capture Begin', self.__onBeginScroll, postevent = False)
        self.bind('Capture Offset', self.__onScroll, postevent = False)
        self.bind('Capture End', self.__onEndScroll, postevent = False)
        self.bind('Mouse Move', self.__onMouseMove)
        self.bind('Mouse Leave', setattr, self, 'isMouseOverThumb', False)
        self.__thumbStartAnim = koan.anim.AnimTarget('decay', 0, 0, 0, self)

    def close(self):
        if self.thumbEffect:
            self.thumbEffect.close()
            self.thumbEffect = None
        super(ScrollBar, self).close()

    def __onChangeOffset(self):
        self.invoke('Scroll', self.__offset)

    def __getOffset(self):
        return self.__offset
    def __setOffset(self, offset):
        self.__offset = offset
        self.__onChangeOffset()
    offset = property(__getOffset, __setOffset)

    def __getPageSize(self):
        if self.fullSize == 0:
            return 0
        else:
            return float(self.viewSize) / self.fullSize
    pageSize = property(__getPageSize)
    
    def __getMaxOffset(self):
        return max(0, 1.0 - self.pageSize)
    maxOffset = property(__getMaxOffset)
    
    def __getThumbSize(self):
        if self.vertical:
            size = self.height
        else:
            size = self.width
        return clamp(self.thumbMinSize, self.pageSize * size, size)
    thumbSize = property(__getThumbSize)

    def __getThumbBgSize(self):
        if self.vertical:
            size = self.height
        else:
            size = self.width
        return size - self.thumbSize
    thumbBgSize = property(__getThumbBgSize)
    
    def __getThumbStart(self):
        if self.maxOffset > 0:
            return self.__offset * self.thumbBgSize / self.maxOffset
        else:
            return 0
    thumbStart = property(__getThumbStart)

    def __getThumbEnd(self):
        return self.thumbStart + self.thumbSize
    thumbEnd = property(__getThumbEnd)

    def setRange(self, full, view):
        self.fullSize = full
        self.viewSize = view
        
    def __fixVisible(self):
        if self.autoHide:
            if self.fullSize > self.viewSize:
                #if not self.isVisible():
                self.invokeCmd('Show Scrollbar')
            else:
                #if self.isVisible():
                self.invokeCmd('Hide Scrollbar')

    def __animScroll(self, newScrollPos):
        self.__thumbStartAnim.ForceAssign(int(self.thumbStart))

    def __fixScroll(self):
        offset = clamp(0, self.__offset, self.maxOffset)
        if offset != self.__offset:
            self.__offset = offset
            self.__onChangeOffset()
            self.__animScroll(self.thumbStart)

    def onPageUp(self):
        self.__offset = clamp(0, self.__offset - self.pageSize, self.maxOffset)
        self.__onChangeOffset()
        self.__animScroll(self.thumbStart)
        
    def onPageDown(self):
        self.__offset = clamp(0, self.__offset + self.pageSize, self.maxOffset)
        self.__onChangeOffset()
        self.__animScroll(self.thumbStart)
            
    def captureTest(self, x, y):
        if self.vertical:
            x = y

        if self.thumbStart <= x and x <= self.thumbEnd:
            return True
        elif self.thumbStart > x:
            self.onPageUp()
            return False
        elif x > self.thumbEnd :
            self.onPageDown()
            return False
        return False

    def __onMouseMove(self, x, y, flag):
        if self.vertical:
            x = y
        if self.thumbStart <= x and x <= self.thumbEnd:
            self.isMouseOverThumb = True
        else:
            self.isMouseOverThumb = False
        
    def __onBeginScroll(self, x, y):
        self.__capOffset = self.__offset
        self.capture = True

    def __onEndScroll(self, x, y):
        self.capture = False

    def __onScroll(self, x, y):
        if self.vertical:
            offset = float(y) / self.height
        else:
            offset = float(x) / self.width
        self.__offset = clamp(0, self.__capOffset + offset, self.maxOffset)
        self.__onChangeOffset()
        self.__animScroll(self.thumbStart)

    def setScroll(self, value):
        self.__offset = clamp(0, value, self.maxOffset)
        self.__onChangeOffset()
        self.__animScroll(self.thumbStart)

    def fixScroll(self, value):
        self.__offset = clamp(0, value, self.maxOffset)
        self.__animScroll(self.thumbStart)

    def onDraw(self, render):
        super(ScrollBar, self).onDraw(render)

        if self.vertical:
            render.Translate(0, self.__thumbStartAnim)
            self.onDrawThumb(render,
                    0,
                    0,
                    self.width,
                    self.thumbSize
            )
        else:
            render.Translate(self.__thumbStartAnim, 0)
            self.onDrawThumb(render,
                    0,
                    0,
                    self.thumbSize,
                    self.height
            )

    def onDrawThumb(self, render, l, t, r, b):
        if self.thumbEffect:
            render.Translate(l, t)
            self.thumbEffect.draw(render, r - l, b - t)
        else:
            t = render.GetTexture(self.thumbImage, gamma = self.gamma)
            render.SetTexture(t)
            render.DrawRect(l, t, r, b)
            
    def onKey(self, key):
        if self.vertical and (key == 'UP' or key == 'DOWN') or not self.vertical and (key == 'LEFT' or key == 'RIGHT'):
            if key == 'UP' or key == 'LEFT':
                self.onPageUp()
            else:
                self.onPageDown()
            return True
        return super(ScrollBar, self).onKey(key)
        

        
if __name__ == '__main__':
    from window import Window
    import color

    def trace(v):
        print 'Scroll offset', v
    koan.init()
    
    w = Window()
    w.create(0, 0, 800, 600, caption = True)
    w.bgColor = color.darkblue    
    
    s = ScrollBar(w)
    s.rect = 100, 100, 50, 400
    s.bgColor = color.green
    s.thumbImage = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\scrollbar\scroll_slider_p.png|(5,2,5,2)'
    s.setRange(100, 10.3)
    s.bind('Scroll', trace)
    
    w.show()
    
    koan.run(1)
    koan.final()




