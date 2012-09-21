import math
import koan
import color
from component import Component, clamp

class ListView(Component):
    '''
    events:
        - Offset Change
    functions:
        setItems
        moveToFocus
        onScroll (for scrollbar binding)
        
    overridable functions:
        onFixScroll
        itemHitTest
        onDrawItem
   

       |------------F------------|
       |                         |
       ---------------------------
       |      |           |      |
       ---------------------------
       |      |           |      |
       |--o1--|-----V-----|--o2--|
    Full(F):      self._full
    View(V):      self.width
    Offset1(o1):  self.o1
    Offset2(o2):  self.o2
    '''    
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        
        # selected items
        self._items = []
        self.focusIdx = 0
        self.highlitIdx = -1
        
        # display parameters
        self.vertical = False
        self.animTime = 0.3
        self._cellWidth = 20
        self._cellHeight = 20
        self.margin = 0, 0
        self.o1 = koan.anim.AnimTarget('decay', 0, 0, 0, self)

        self.bind('Mouse Down', self.__onMouseDown)
        self.bind('Mouse Wheel', self.__onMouseWheel)
        self.bind('Mouse Move', self.__onMouseMove)
        self.bind('Mouse Leave', setattr, self, 'highlitIdx', -1)
        self.bind('Size Change', self.onSize)
        self.bind('Fix Scroll', self.onFixScroll)
        self.autoDirty(['o1', 'focusIdx', 'highlitIdx'])

    def __getViewSize(self):
        if self.vertical:
            return self.height
        else:
            return self.width
    viewSize = property(__getViewSize)
    
    def __getFullSize(self):
        return self._full
    fullSize = property(__getFullSize)
    
    def __getCellSize(self):
        if self.vertical:
            return self._cellHeight
        else:
            return self._cellWidth
    cellSize = property(__getCellSize)    
    
    def __getPageSize(self):
        if self.vertical:
            return int(self.height / (self._cellHeight + self.margin[1]))
        else:
            return int(self.width / (self._cellWidth + self.margin[0]))
    pageSize = property(__getPageSize)
    
    def __getMargin(self):
        if self.vertical:
            return self.margin[1]
        else:
            return self.margin[0]
    cellMargin = property(__getMargin)

    def setItems(self, items, focusIdx = -1):
        self._items = items
        if focusIdx != -1:
            self.focusIdx = focusIdx
        self.highlitIdx = -1
        self.onSize()
        self.moveToFocus(anim = False)

    def __focus(self, idx):
        self.focusIdx = clamp(0, idx, len(self._items)-1 )
        self.moveToFocus()
        
    def onPrevPage(self):
        self.__focus(self.focusIdx - self.pageSize)
        
    def onNextPage(self):
        self.__focus(self.focusIdx + self.pageSize)
        
    def onPrev(self):
        self.__focus(self.focusIdx - 1)
    
    def onNext(self):
        self.__focus(self.focusIdx + 1)

    def onHome(self):
        self.__focus(0)

    def onEnd(self):
        self.__focus(len(self._items)-1)
        
    def moveToFocus(self, anim = True):
        '''
        move focus item to center
        '''
        #prevent invalid offset when list item is less than view
        old_o1 = -self.o1.QueryValue()
        o1 = 0
        if self.cellSize * len(self._items) <= self.viewSize:
            o1 = 0
            if anim:
                self.o1.Reset( self.animTime, 0 )
            else:
                self.o1.Assign( 0 )
        else:
            o1 = (self.cellSize + self.cellMargin) * self.focusIdx - (self.viewSize-self.cellSize-self.cellMargin) / 2
            o1 = clamp(0, o1, self._full - self.viewSize)
            if anim:
                self.o1.Reset( self.animTime, -o1 )
            else:
                self.o1.Assign( -o1 )
        #self.o1 = -o1
        self.__resetDisplayRange(old_o1, o1)
        if self._full:
            self.invoke('Fix Scroll', -self.o1 / self._full)

    def onScroll(self, offset):
        old_o1 = -self.o1.QueryValue()
        new_o1 = offset * self._full
        self.o1.Reset( self.animTime, -new_o1 )
        self.__resetDisplayRange(old_o1, new_o1)
        
    def onFixScroll(self, value):
        '''Please override this function'''
        pass
        
    def itemHitTest(self, x, y, idx):
        '''Override this function if you have specified hit test'''
        # check if point is inside the item        
        rect = 0, 0, self._cellWidth, self._cellHeight
        return x >= rect[0] and x <= rect[2] and y >= rect[1] and y <= rect[3]

    #-------------------------------------------------------------------------
    # render function
    #-------------------------------------------------------------------------
    def onDrawItem(render, idx):
        pass

    def onDraw(self, render):
        super(ListView, self).onDraw(render)
        render.PushMatrix()
        if(self.vertical):
            render.Translate(0, self.o1)
        else:
            render.Translate(self.o1, 0)
            
        offset = self.cellSize + self.margin[1 if self.vertical else 0]
        render.Translate(self.margin[0], self.margin[1])
        
        idx = self._startIdx
        if self.vertical:
            render.Translate(0, offset * idx)
        else:
            render.Translate(offset * idx, 0)
        #print '--- Item list ---', self._startIdx, ' : ', self._endIdx, ' = ', self._endIdx - self._startIdx
        for idx in xrange(self._startIdx, self._endIdx):
            self.onDrawItem(render, idx)
            if self.vertical:
                render.Translate(0, offset)
            else:
                render.Translate(offset, 0)
        render.PopMatrix()

    #-------------------------------------------------------------------------
    # private function
    #-------------------------------------------------------------------------       
    def __getIndexByOffset(self, o):
        '''
        @param o: offset from start of full size
        @type o: float
        @rtype: None
        '''
        o = o / (self.cellSize + self.cellMargin)
        idx = int(math.floor(o))
        if idx >= len(self._items):
            return -1
        return idx
        
    def _getIndexByPoint(self, x, y, query = True):
        '''
        @param x, y: position in local space
        @type x, y: float
        @rtype: None
        '''
        if self.vertical:
            y = y - (self.o1.QueryValue() if query else self.o1)
            idx = self.__getIndexByOffset( y )
            if idx == -1:
                return -1
                
            # check if point is inside the item
            y = y - (self._cellHeight + self.margin[1]) * idx - self.margin[1]
            x = x - self.margin[0]
        else:
            x = x - (self.o1.QueryValue() if query else self.o1)
            idx = self.__getIndexByOffset( x )
            if idx == -1:
                return -1
                
            # check if point is inside the item
            x = x - (self._cellWidth + self.margin[0]) * idx - self.margin[0]
            y = y - self.margin[1]

        if not self.itemHitTest(x, y, idx):
            return -1
        return idx

    def onDataChanged(self):
        self._full = (self.cellSize + self.cellMargin) * len(self._items) + self.cellMargin
        old_o1 = -self.o1.QueryValue()
        self.__resetDisplayRange(old_o1, old_o1)
        
    def __resetDisplayRange(self, old_o1, new_o1):
        '''
        recalculate visible item range (self._startIdx, self._endIdx)
        @param old_o1: old offset
        @param new_o1: new offset
        @type old_o1, new_o1: float
        @rtype: None
        '''
        start = self.__getIndexByOffset( min(old_o1, new_o1) )
        if start == -1:
            start = 0
        self._startIdx = max( 0, start )
        
        end = self.__getIndexByOffset(max(old_o1, new_o1) + self.viewSize)
        if end == -1:
            end = len(self._items) - 1            
        self._endIdx = min( len(self._items), end+1 )
        self.invoke('Offset Change')

    def __onMouseDown(self, x, y, flag):
        self.setFocus()

        idx = self._getIndexByPoint(x, y)
        if idx != -1:
            self.focusIdx = idx

    def __onMouseMove(self, x, y, arg):
        self.highlitIdx = self._getIndexByPoint(x, y)
    
    def __onMouseWheel(self, delta):
        old_o1 = -self.o1.QueryValue()
        #o1 = -self.o1
        new_o1 = old_o1 - delta * (self.cellSize + self.cellMargin)
        new_o1 = clamp( 0, new_o1, max(0, self._full - self.viewSize) )
        self.o1.Reset( self.animTime, -new_o1 )
        self.__resetDisplayRange(old_o1, new_o1)
        if self._full:
            self.invoke('Fix Scroll', -self.o1 / self._full)

    def onCellSize(self):    
        # cell size
        if self.vertical:
            self._cellWidth = self.width - self.margin[0] * 2
        else:            
            self._cellHeight = self.height - self.margin[1] * 2
            
    def onSize(self):
        self.onCellSize()
        
        # full size (self._full) and view size (self.width)
        self._full = (self.cellSize + self.cellMargin) * len(self._items) + self.cellMargin
        
        #
        old_o1 = -self.o1.QueryValue()
        if self._full > self.viewSize:
            new_o1 = clamp( 0, old_o1, max(self._full - self.viewSize, self.viewSize) )
        else:
            new_o1 = 0
        self.o1.Reset( self.animTime, -new_o1 )
        self.__resetDisplayRange(old_o1, new_o1)
        if self._full:
            self.invoke('Fix Scroll', -self.o1 / self._full)

    def onKey(self, key):
        if self.vertical:
            if key == 'UP':
                self.onPrev()
                return True
            elif key == 'DOWN':
                self.onNext()
                return True            
        else:
            if key == 'LEFT':
                self.onPrev()
                return True
            elif key == 'RIGHT':
                self.onNext()
                return True        
        if key == 'HOME':
            self.onHome()
            return True
        elif key == 'END':
            self.onEnd()
            return True
        elif key == 'PAGEUP':
            self.onPrevPage()
            return True
        elif key == 'PAGEDOWN':
            self.onNextPage()
            return True
            
        return super(ListView, self).onKey(key)




if __name__ == '__main__':
    from window import Window
    from pprint import pprint
    import color

    class MyComponent(Component):
        def __init__(self, parent = None):
            Component.__init__(self, parent) 
            
            self.bind('Mouse Enter', self.trace, 'Mouse Enter')
            self.bind('Mouse Leave', self.trace, 'Mouse Leave')
            self.bind('Mouse Down', self.trace, 'Mouse Down')
            self.bind('Mouse Up', self.trace, 'Mouse Up')
            self.bind('Mouse RDown', self.trace, 'Mouse RDown')
            self.bind('Mouse RUp', self.trace, 'Mouse RUp')
            self.bind('Click', self.trace, 'Click')
            self.bind('Dbl Click', self.trace, 'Dbl Click')
            self.bind('RDbl Click', self.trace, 'RDbl Click')
            
        def trace(self, *argv, **argd):
            print self, argv
            
    koan.init()
    
    w = Window()    
    w.create(0, 0, 800, 600, caption = True)
    w.bgColor = color.darkblue
    
    from dialog import Dialog
    from pprint import pprint
    w.d = Dialog(w)
    w.d.bind('Mouse Enter', pprint, 'Mouse Enter')
    w.d.bind('Mouse Leave', pprint, 'Mouse Leave')
    w.d.size = 400, 300
    w.d.bgColor = color.blue
    w.bind('Key', koan.action.PureAction(w.d.doModal))
    
    o = MyComponent(w.d)
    o.rect = 100, 50, 300, 100
    o.bgColor = color.yellow
    w.show()
    
    koan.run(1)    
    koan.final()
