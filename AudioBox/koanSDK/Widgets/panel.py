import koan
import color
from koan.arrowctrl import ArrowControl, DMAP
from koan.rectangle import Rectangle
from koan.layout import LayoutManager
from component import Component, CaptureObject, Intersect, clamp
from button import GroupBase

class AutoLayout:
    def __init__(self):
        assert isinstance(self, Component)
        self.autoLayout([], ['Size Change', 'Child Visible Change', 'Child Size Change'])

    def autoLayout(self, attributes, events = []):
        for i in attributes:
            self.changeEvent(i, self.relayout, sync = False)
        for i in events:
            self.bind(i, self.relayout)

    def setChildSightDirty(self, comp):
        for c in comp.children:
            c.sightframeNumber = 0
            c.sight = 0
            self.setChildSightDirty(c)

    def relayout(self, *argv):
        #raise 'Panel is an abstract class !!!'
        pass
            
class AutoHide:
    ''' state transition: normal -> fadeout -> invisible
    '''
    def __init__(self):
        assert isinstance(self, Component)
        
        # dirty hack to handle key/mouse event when autohide
        self.passKey, self.__passKey_old = self.__passKey, self.passKey
        self.passMouseMsg, self.__passMouseMsg_old = self.__passMouseMsg, self.passMouseMsg

        # param
        self.hideCursor = True
        self.timeToFadeout = 2
        self.timeFadeout = 1
        self.timeFadein = 0.3
        self.autohide_allowKey = []

        # state
        self.__state = 'normal'
        self.enableAutoHide = True
        self.opacity = koan.anim.AnimTarget('linear', 0, 1, 1, self)

        # bind events
        self.autoRemove( self.window.changeEvent('preMousePos', self.__onMouseMove) )
        self.changeEvent('enableAutoHide', self.__onEnableChange)
        self.changeEvent('visible', self.__onEnableChange)
        self.bind('Visible Change', self.__onVisibleChange)
        if self.window:
            self.autoRemove( self.window.bind('Window Mouse Down', self.__onMouseMove) )
            self.autoRemove( self.window.bind('Window Mouse RDown', self.__onMouseMove) )
            self.autoRemove( self.window.bind('Auto Hide Appear', self.autohide_appear) )
            self.autoRemove( self.window.bind('Auto Hide Reset', self.autohide_reset) )

        # start to work
        self.__onEnableChange()

    def close(self):
        koan.anim.Cancel(self.__fadeout_state)
        koan.anim.Cancel(self.__invisible_state)
        self.passKey, self.__passKey_old = None, None
        self.passMouseMsg, self.__passMouseMsg_old = None, None

    def __isAutoHide(self):
        return self.isVisible() and self.enableAutoHide
        
    def __onEnableChange(self, *argv):
        if self.__isAutoHide():
            self.__normal_state()
        else:
            self.__state = 'normal'
            self.invokeVisibleChange()  # workaround for hide tooltips
            self.opacity.Reset(0, 1)
            if self.hideCursor:
                self.window.showCursor(True)
            koan.anim.Cancel(self.__fadeout_state)
            koan.anim.Cancel(self.__invisible_state)

    def __onVisibleChange(self, v):
        if not v:
            koan.anim.Cancel(self.__fadeout_state)
            koan.anim.Cancel(self.__invisible_state)
            if self.visible:
                self.window.showCursor(True)

    def __normal_state(self):
        if self.__state != 'normal':
            self.opacity.Reset(self.timeFadein, 1)
            if self.hideCursor:
                self.window.showCursor(True)
            self.invokeVisibleChange()  # workaround for hide tooltips

        self.__state = 'normal'
        koan.anim.Cancel(self.__fadeout_state)
        koan.anim.Cancel(self.__invisible_state)
        if self.__isAutoHide():
            koan.anim.Execute(self.timeToFadeout, self.__fadeout_state)

    def __fadeout_state(self):
        koan.anim.Cancel(self.__fadeout_state)
        self.__state = 'fadeout'
        self.opacity.Reset(self.timeFadeout, 0)
        if self.hideCursor:
            self.window.showCursor(False)
        koan.anim.Execute(self.timeFadeout, self.__invisible_state)

    def __invisible_state(self):
        koan.anim.Cancel(self.__invisible_state)
        self.__state = 'invisible'
        self.opacity.Assign(0)
        self.invokeVisibleChange()      # workaround for hide tooltips

    def __onMouseMove(self, *args):
        if not self.__isAutoHide():
            return
        self.__normal_state()

    def autohide_reset(self):
        if self.__state == 'invisible':
            return
        self.__normal_state()
    def autohide_appear(self):
        self.__normal_state()
    def autohide_fadeout(self):
        if not self.__isAutoHide():
            return
        self.__normal_state()   # don't jump into fadeout state directly
        self.__fadeout_state()
    def autohide_invisible(self):
        if not self.__isAutoHide():
            return
        self.__normal_state()   # don't jump into fadeout state directly
        self.__fadeout_state()
        self.__invisible_state()

    def __passMouseMsg(self, x, y, button, state, *args):
        if self.__state == 'invisible':
            return False
        return self.__passMouseMsg_old(x, y, button, state, *args)

    def __passKey(self, key, keymaps):
        if self.__state == 'invisible':
            # only hotkey and keys in whitelist can pass
            km = keymaps
            if hasattr(self, 'keymaps'):
                km = km.copy()
                km.update(self.keymaps)
            if key not in km and key not in self.autohide_allowKey:
                return False

        self.window.invoke('Auto Hide Appear')

        return self.__passKey_old(key, keymaps)

#-------------------------------------------------------------------------------
# class Panel
#-------------------------------------------------------------------------------
class Panel(Component, ArrowControl, AutoLayout):
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        ArrowControl.__init__(self)
        AutoLayout.__init__(self)
        self.tabStop = False

    def onKey(self, key):
        if key in DMAP:
            focusnow = self.getFocusControl()
            return self.trigger(focusnow, key)
        return super(Panel, self).onKey(key)

    def setCommandProperty(self, prop, **keyword):
        Component.setCommandProperty(self, prop, **keyword)
        ArrowControl.setCommandProperty(self, prop, **keyword)

#-------------------------------------------------------------------------------
# class StackPanel
#-------------------------------------------------------------------------------
class StackPanel(Panel):
    def __init__(self, parent = None, **argd):
        Panel.__init__(self, parent)
        self.orientation = 'Vertical'
        
        self.margin = 0, 0
        self.scrollOffset = koan.anim.AnimTarget('decay', 0, self.margin[1], self.margin[1], self)
        self.invScrollOffset = koan.anim.AnimTransform(self.scrollOffset, -1, 0)
        self.autosize = False   # True: panel height (vertical mode) will auto fit with sum of children size
        self.autofit = False    # True: panel width will fit into maximun of children
        self.center = False     # True: child will put in center, False: child will fit to stackpanel
        self.fullSize = 10
        self.changeEvent('dirty', self.__onDirty)        
        if argd.get('autofix', True):     # True: fullSize change will auto fix position
            self.changeEvent('fullSize', self.__onFullSizeChange)
        self.autoLayout(['orientation', 'margin', 'autosize', 'autofit'], [])

    def __onDirty(self):
        self.allSightDirty = True
        
    def parent2local(self, x, y):
        """
        @param x, y: (x, y) in parent coordinate
        @return: (x, y) in local coordinate
        """
        
        x -= self.left
        y -= self.top
        
        x -= self.margin[0]
        y -= self.margin[1]
        if self.orientation == 'Vertical':
            y += self.scrollOffset
        else:
            x += self.scrollOffset
        
        return x, y
        
    def local2parent(self, x, y):
        """
        @param x, y: (x, y) in local coordinate
        @return: (x, y) in parent coordinate
        """
        #return x + self.left, y + self.top
        x += self.left
        y += self.top
        
        x += self.margin[0]
        y += self.margin[1]
        if self.orientation == 'Vertical':
            y -= self.scrollOffset
        else:
            x -= self.scrollOffset
        
        return x, y
        
    def updateView(self, render):
    
        target = float(self.scrollOffset)
        now = self.scrollOffset.QueryValue()
        diff = target - now
    
        l, t, r, b = render.viewStack[-1]
        l, t = self.parent2local(l, t)
        r, b = self.parent2local(r, b)
        
        client = [0 + self.margin[0], 0 + self.margin[1], self.width + self.margin[0], self.height + self.margin[1]]
        
        if self.orientation == 'Vertical':
            client[1] += self.scrollOffset
            client[3] += self.scrollOffset
        else:
            client[0] += self.scrollOffset
            client[2] += self.scrollOffset

        local = list(Intersect((l, t, r, b), client))
            
        if self.orientation == 'Vertical':
            if diff > 0:
                local[1] -= diff
            else:
                local[3] -= diff
            
        else:
            if diff > 0:
                local[0] -= diff
            else:
                local[2] -= diff 
                            
        render.viewStack.append(local)
        return local[2] - local[0] > 0 and local[3] - local[1] > 0

    def drawChild(self, render):
        render.Translate(self.margin[0], self.margin[1])
        if self.orientation == 'Vertical':
            render.Translate(0, self.invScrollOffset)
        else:
            render.Translate(self.invScrollOffset, 0)
        super(Panel, self).drawChild(render)
    
    def onScroll(self, offset):        
        view = self.height if self.orientation == 'Vertical' else self.width
        full = self.fullSize
        if full > view:
            offset = clamp(0, offset, float(full - view) / full)
            self.scrollOffset.Reset(0.3, full * offset)

    def __getViewSize(self):
        return self.height if self.orientation == 'Vertical' else self.width
    viewSize = property(__getViewSize)
    
    def __onFullSizeChange(self):
        '''
        full size is change, we should reset the position
        '''
        offset = float(self.scrollOffset)
        if self.fullSize < self.viewSize:
            self.scrollOffset.Reset(0.3, 0)
        elif (offset + self.viewSize) > self.fullSize:
            self.scrollOffset.Reset(0.3, self.fullSize - self.viewSize)

    #@staticmethod
    def verticalLayout(self):
        top = 0
        if self.autofit:
            for i in self._children:
                if i.visible:
                    self.width = max(self.width, i.width)
                    
        for i in self._children:
            if i.visible:
                i.top = top
                if self.center:
                    i.left = (self.width - i.width) / 2.0 - self.margin[0]
                else:
                    i.width = self.width - self.margin[0] * 2
                top += i.height
        if self.autosize:
            self.height = top + self.margin[1] * 2
        self.fullSize = top + self.margin[1] * 2

    #@staticmethod
    def horizontalLayout(self):
        left = 0
        if self.autofit:
            for i in self._children:
                if i.visible:
                    self.height = max(self.height, i.height)
        for i in self._children:
            if i.visible:
                i.left = left
                if self.center:
                    i.top = (self.height - i.height) / 2.0 - self.margin[1]
                else:
                    i.height = self.height - self.margin[1] * 2
                left += i.width
        if self.autosize:
            self.width = left + self.margin[0] * 2
        self.fullSize = left

    def relayout(self, *argv):
        if self.orientation == 'Vertical':
            self.verticalLayout()
        else:
            self.horizontalLayout()


#-------------------------------------------------------------------------------
# class DockSplitter
#-------------------------------------------------------------------------------
class DockSplitter(Component, CaptureObject):
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        CaptureObject.__init__(self)
        self.useGlobalCapture = True
        self.tabStop = False

        self.bind('Mouse Enter', self.onChangeCursor, True)
        self.bind('Mouse Leave', self.onChangeCursor, False)
        self.parent.autoRemove( self.bind('Capture Begin', self.parent.invoke, 'Splitter Start', self, posetevent = False) )
        self.parent.autoRemove( self.bind('Capture Offset', self.parent.invoke, 'Splitter Move', self, posetevent = False) )

    def onChangeCursor(self, v):
        if v and hasattr(self, '_dock_'):
            if self._dock_ in ['left', 'right']:
                self.window.setCursor('size we')
            else:
                self.window.setCursor('size ns')
        else:
            self.window.setCursor('arrow')
            
#-------------------------------------------------------------------------------
# class DockPanel
#-------------------------------------------------------------------------------
class DockPanel(Panel):
    def __init__(self, parent = None):
        Panel.__init__(self, parent)
        self.defaultDock = 'top'
        self.lastFill = True
        
        self.bind('Splitter Start', self.onSplitterStart)
        self.bind('Splitter Move', self.onSplitterSize)

    def onSplitterStart(self, splt, x, y):
        assert splt
        try:
            _children = [c for c in self._children if c.visible]
            idx = _children.index(splt)
            o = _children[idx-1]
            splt.orgWidth = o.width
            splt.orgHeight = o.height
            #print 'Splitter start', split.orgWidth, split.orgHeight
        except:
            pass

    def onSplitterSize(self, splt, x, y):
        assert splt
        try:
            _children = [c for c in self._children if c.visible]
            idx = _children.index(splt)
            o = _children[idx-1]
            if o._dock_ == 'left':
                o.width = max(0, splt.orgWidth + x)
                if hasattr(o, 'maxWidth'):
                    o.width = min(o.width, o.maxWidth)
                if hasattr(o, 'minWidth'):
                    o.width = max(o.width, o.minWidth)
            elif o._dock_ == 'right':
                o.width = max(0, splt.orgWidth - x)
                if hasattr(o, 'maxWidth'):
                    o.width = min(o.width, o.maxWidth)
                if hasattr(o, 'minWidth'):
                    o.width = max(o.width, o.minWidth)
            elif o._dock_ == 'top':
                o.height = max(0, splt.orgHeight + y)
                if hasattr(o, 'maxHeight'):
                    o.height = min(o.height, o.maxHeight)
                if hasattr(o, 'minHeight'):
                    o.height = max(o.height, o.minHeight)
            elif o._dock_ == 'bottom':
                o.height = max(0, splt.orgHeight - y)
                if hasattr(o, 'maxHeight'):
                    o.height = min(o.height, o.maxHeight)
                if hasattr(o, 'minHeight'):
                    o.height = max(o.height, o.minHeight)
        except:
            pass
        
    def relayout(self, *argv):
        r = Rectangle(*self.localRect)
        
        _children = [c for c in self._children if c.visible]

        for c in _children[:-1]:
            if isinstance(c, DockSplitter):
                idx = _children.index(c)
                if idx > 0:
                    c._dock_ = _children[idx-1]._dock_
            elif not hasattr(c, '_dock_'):
                c._dock_ = self.defaultDock        # set default to top

            if c._dock_ == 'left':
                c.height, c.top, c.left = r.height, r.top, r.left
                r.innerOffset(c.width, 0 ,0, 0)
            elif c._dock_ == 'right':
                c.height, c.top, c.left = r.height, r.top, r.right - c.width
                r.innerOffset(0, 0 ,c.width, 0)
            elif c._dock_ == 'top':
                c.width, c.left, c.top = r.width, r.left, r.top
                r.innerOffset(0, c.height, 0, 0)
            elif c._dock_ == 'bottom':
                c.width, c.left, c.top = r.width, r.left, r.bottom - c.height
                r.innerOffset(0, 0, 0, c.height)
        #------------------------------------------
        # last object must fill the whole panel
        #------------------------------------------
        if _children:
            _children[-1].rect = r.rect

    def dock(self, obj, side):
        obj._dock_ = side

    def setAttachedProperty(self, prop, **argd):
        name = prop['name'].split('.')[-1]
        side = prop['data']
        obj = prop['child']
        if name.lower() == 'dock':
            side = side.strip().lower()
            if side not in ['left', 'top', 'right', 'bottom']:
                side = self.defaultDock
            self.dock(obj, side)

#-------------------------------------------------------------------------------
# class Canvas
#-------------------------------------------------------------------------------
class Canvas(Component, LayoutManager):
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        LayoutManager.__init__(self)
        self.tabStop = False

    def setAttachedProperty(self, prop, **argd):
        LayoutManager.setAttachedProperty(self, prop, **argd)

class AutoHideCanvas(Canvas, AutoHide):
    def __init__(self, parent = None):
        Canvas.__init__(self, parent)
        AutoHide.__init__(self)
    def close(self):
        AutoHide.close(self)
        Canvas.close(self)

class GroupCanvas(Canvas, GroupBase):
    def __init__(self, parent = None):
        Canvas.__init__(self, parent)
        GroupBase.__init__(self)
#-------------------------------------------------------------------------------
# class Viewbox
#-------------------------------------------------------------------------------
class Viewbox(Component):
    '''
    stretch mode:
    None
    Fill
    Uniform
    Uniform Fill
    '''
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        self.stretch = 'Fill'
        self.tabStop = False
        #self.scalemode = 'Both'        #wpf: StretchDirection
        self.__scale = 1, 1
        self.__offset = 0, 0
        self.autoStretch(['stretch'], ['Size Change', 'Child Add', 'Child Size Change'])

    def autoStretch(self, attributes, events = []):
        for i in attributes:
            self.changeEvent(i, self.__restretch, sync = False)
        for i in events:
            self.bind(i, self.__restretch)

    def __restretch(self, *argv):
        if self._children and self.stretch != 'None':
            c = self._children[0]
            if self.stretch == 'Fill':
                self.__scale = float(self.width) / c.width, float(self.height) / c.height
            elif self.stretch == 'Uniform':
                s1 = float(self.width)/ self.height
                s2 = float(c.width) / c.height
                if s1 < s2:
                    s = float(self.width) / c.width
                    self.__scale = s, s
                    self.__offset = 0, (self.height - c.height * self.__scale[1]) / 2
                else:
                    s = float(self.height) / c.height
                    self.__scale = s, s
                    self.__offset = (self.width - c.width * self.__scale[0]) / 2, 0
            elif self.stretch == 'Uniform Fill':
                s1 = float(self.width)/ self.height
                s2 = float(c.width) / c.height
                if s1 > s2:
                    s = float(self.width) / c.width
                    self.__scale = s, s
                    self.__offset = 0, (self.height - c.height * self.__scale[1]) / 2
                else:
                    s = float(self.height) / c.height
                    self.__scale = s, s
                    self.__offset = (self.width - c.width * self.__scale[0]) / 2, 0
            else:
                print '[Viewbox] Unknown stretch type %s !!!' %(self.stretch)
                self.__scale = 1, 1
        else:
            self.__scale = 1, 1

    def _addChild(self, c):
        if len(self._children) == 0:
            super(Viewbox, self)._addChild(c)
        else:
            print 'ViewBox already has a child and cannot add %s' %(c)
            raise Exception

    def getPixelUnit(self):
        x, y = self.parent.getPixelUnit() if self.parent else (1, 1)
        return x * self.__scale[0], y * self.__scale[1]

    def hitTest(self, x, y):
        return super(Viewbox, self).hitTest(x * self.__scale[0], y * self.__scale[1])

    def parent2local(self, x, y):
        return  (x - self.left - self.__offset[0]) / self.__scale[0],\
                (y - self.top  - self.__offset[1]) / self.__scale[1]

    def local2parent(self, x, y):
        return  x * self.__scale[0] + self.left + self.__offset[0],\
                y * self.__scale[1] + self.top + self.__offset[1]

    def drawChild(self, render):
        """
        overwritable: recursively draw it's children
        @rtype: None
        """
        if len(self._children):
            render.Translate(*self.__offset)
            render.Scale(*self.__scale)
            map(lambda c: c.passDraw(render), self._children)






if __name__ == '__main__':
    '''
    Please set koan path in PYTHONPATH
    '''
    from window import Window
    from component import Component
    
    def TestDockPanel(w):    
        d = DockPanel(w)
        d.bindData('width', w, 'width', dir = '<-')
        d.bindData('height', w, 'height', dir = '<-')
        
        s = StackPanel(d)
        s.bgColor = color.red
        s.width = 100
        
        p = DockSplitter(d)
        p.bgColor = color.darkgray
        
        s1 = StackPanel(d)
        s1.bgColor = color.green
        s1.height = 100    
        #d.dock(s1, 'top')
        
        p = DockSplitter(d)
        p.bgColor = color.darkgray
        
        s2 = StackPanel(d)
        s2.bgColor = color.blue
        s2.width = 100
        #d.dock(s2, 'right')
        
        p = DockSplitter(d)
        p.bgColor = color.darkgray
        
        s3 = StackPanel(d)
        s3.bgColor = color.yellow
        s3.height = 100
        #d.dock(s3, 'bottom')
        
        p = DockSplitter(d)
        p.bgColor = color.darkgray
        
        
        d.dock(s, 'left')
        d.dock(s1, 'top')
        d.dock(s2, 'right')
        d.dock(s3, 'bottom')
        
        d = DockPanel(d)
        
        s = StackPanel(d)
        s.bgColor = color.red
        s.width = 100
        
        p = DockSplitter(d)
        p.bgColor = color.darkgray
        
        s1 = StackPanel(d)
        s1.bgColor = color.green
        s1.height = 100    
        #d.dock(s1, 'top')
        
        p = DockSplitter(d)
        p.bgColor = color.darkgray
        
        s2 = StackPanel(d)
        s2.bgColor = color.blue
        s2.width = 100
        #d.dock(s2, 'right')
        
        p = DockSplitter(d)
        p.bgColor = color.darkgray
        
        s3 = StackPanel(d)
        s3.bgColor = color.yellow
        s3.height = 100
        #d.dock(s3, 'bottom')
        
        p = DockSplitter(d)
        p.bgColor = color.darkgray
        
        
        c = Canvas(d)
        c.bgColor = color.white
        #d.dock(c, 'left')
        
        o = Component(c)
        o.bgColor = color.darkblue    
        o.size = 200, 30
        
        o1 = Component(c)
        o1.bgColor = color.red    
        o1.size = 50, 50
        
        o2 = Component(c)
        o2.bgColor = color.green    
        o2.size = 50, 50
        
        o3 = Component(c)
        o3.bgColor = color.blue    
        o3.size = 50, 50
        
        o4 = Component(c)
        o4.bgColor = color.purple    
        o4.size = 50, 50
    
        d.dock(s, 'left')
        d.dock(s1, 'top')
        d.dock(s2, 'right')
        d.dock(s3, 'bottom')
        
        c.dock(o, {'horz':True, 'vert':True})
        c.dock(o1, {'left':10, 'top':10})
        c.dock(o2, {'right':10, 'top':10})
        c.dock(o3, {'right':10, 'bottom':10})
        c.dock(o4, {'left':10, 'bottom':10})

    def TestStackPanel(w):
        s = StackPanel(w)
        #s.orientation = 'Horizontal'
        s.center = True        
        s.bind('Mouse Wheel', s.onScroll)
        #s.autosize = True
        s.rect = 50, 50, 600, 170
        s.bgColor = color.gray

        c = Component(s)
        c.size = 250, 50
        c.bgColor = color.red
        
        c = Component(s)
        c.size = 300, 50
        c.bgColor = color.green
        
        c = Component(s)
        c.size = 300, 300
        c.bgColor = color.blue
        
    koan.init()
    
    w = Window()
    w.create(0, 0, 800, 600, True)    
    #TestDockPanel(w)
    TestStackPanel(w)
    w.show()
    
    koan.run(1)
    
    koan.final()
