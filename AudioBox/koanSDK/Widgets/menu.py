import koan
import color
from component import Component, Static, clamp
from panel import StackPanel, AutoLayout
from dialog import PopupBase
from text import TextBase
from button import CheckBase, RadioBase, GroupBase

def menuOnKey(self, key):
    if key == 'UP' or key == 'DOWN':
        children = []
        idx = -1 if key == 'DOWN' else 0
        for c in self.children:
            if isinstance(c, MenuGroup):
                for x in c.children:
                    if x.visible and x.enabled and not x.blind:                        
                        children.append(x)
                        if x.focus:
                            idx = len(children)-1
            elif c.visible and c.enabled and not c.blind:
                children.append(c)
                if c.focus:
                    idx = len(children)-1        
        if children:
            idx += 1 if key == 'DOWN' else -1
            idx = idx % len(children)
            children[idx].setFocus()
            return True
    return False

#-----------------------------------------------------------------------
# PopupMenu
#-----------------------------------------------------------------------
class PopupMenu(StackPanel, PopupBase):
    def __init__(self, parent = None):
        StackPanel.__init__(self, parent)
        PopupBase.__init__(self)
        self.clip = False
        self.visible = False
        self.autosize = True
        self.autofit = True
        self.expandImg = ''
        self.upImg = ''
        self.downImg = ''        
        self.expandMargin = 26, 1, 2, 2

        self.bind('Mouse Down', self.onMouseDown)
        self.bind('Mouse RDown', self.onMouseDown)
        self.bindCmd('Menu Return', self.modalRet)
        self.bind('Mouse Wheel', self.scroll)

        self.highLit = 'Empty'
        
        self.autoDirty(['sightRect', 'highLit'])
        self.subMenuIndent = 20
        self.subMenuOffsetIdx = 0
        # command routing
        self.cmdPath = None

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
            h = top + self.margin[1] * 2
            if h > self.window.height:
                h = self.window.height
            self.height = h
        self.fullSize = top + self.margin[1] * 2
        
    def relayout(self, *argv):
        super(PopupMenu, self).relayout(*argv)                
        window = self.window
        if window:
            self.xy = clamp(0, self.left, window.width - self.width), clamp(0, self.top, window.height - self.height)
        
    def getChildren(self):
        front = []
        back = []
        for i in self._children:
            if hasattr(i, 'subMenuExpand') and i.subMenuExpand:
                back.append(i)
            else:
                front.append(i)
        return front + back
    children = property(getChildren)
    
    def _invokeCmd(self, cmd, *arg):
        return PopupBase._invokeCmd(self, cmd, *arg)

    def _fireCmd(self, cmd, *arg):
        return PopupBase._fireCmd(self, cmd, *arg)
        
    def close(self):
        super(PopupMenu, self).close()
        self.cancel()

    def onMouseDown(self, x, y, flag):
        if x < 0 or x > self.width or y < 0 or y > self.height:
            self.onCancel()

    def hitTest(self, x, y):
        return True

    def onKey(self, key):
        if key == 'ALT':
            self.onCancel()
            return True
        if menuOnKey(self, key):
            return True
        return PopupBase.onKey(self, key)

    def setMenu(self, menu):
        '''
        menu = 
        {
            'Motion' : 'Motion',
            'Cell' : 'Motion',
        }
        '''
        pass

    def onMenuExpandChange(self):
        mySight = koan.Rectangle(*self.rect)
        for i in self.children:
            if hasattr(i, 'subMenuExpand') and i.subMenuExpand:
                mySight = i.expandSight(mySight, self.xy)
        self.sightRect = mySight

    @staticmethod
    def MenuDrawChild(self, render):
        map(lambda c: c.passDraw(render), filter(lambda c: not hasattr(c, 'subMenuExpand') or not c.subMenuExpand, self._children))
        map(lambda c: c.passDraw(render), filter(lambda c: hasattr(c, 'subMenuExpand') and c.subMenuExpand, self._children))
    
    def onDraw(self, render):
        if self.fullSize > self.height:
            render.PushMatrix()
            mw, mh = self.margin
            w, h = self.width + mw*2, self.height + mh*2
            render.Translate(-mw, -mh)            
            if self.drawEffect:
                self.drawEffect.draw(render, w, h)
            elif self.background:
                # texture
                t = render.GetTexture(self.background, gamma = self.gamma)
                render.SetTexture(t)
                render.DrawRect(0, 0, w, h)
            elif self.bgColor[0] > 0:
                # color
                render.SetTexture(None)
                render.SetColor(*self.bgColor)
                render.DrawRect(0, 0, w, h)
                render.SetColor(*color.white)
            render.PopMatrix()
        else:
            super(PopupMenu, self).onDraw(render)

    def drawChild(self, render):
        mw, mh = self.margin
        w, h = self.size
        # draw up / down button
        if self.fullSize > h:
            enableUp = self.highLit == 'Up' and float(self.scrollOffset) > 0
            enableDown = self.highLit == 'Down' and float(self.scrollOffset) < self.fullSize - h

            t = render.GetTexture(self.upImg)
            if t:
                render.SetTexture(t)
                if not enableUp:
                    render.PushAlpha(0.5)
                render.DrawUniformRect(t.GetSize(), (0, 0, w, mh))
                if not enableUp:
                    render.PopAlpha()
            
            t = render.GetTexture(self.downImg)
            if t:
                render.SetTexture(t)
                if not enableDown:
                    render.PushAlpha(0.5)
                render.DrawUniformRect(t.GetSize(), (0, self.window.height-mh, w, mh))
                if not enableDown:
                    render.PopAlpha()

        render.PushBound(mw, mh, w-mw, h-mh)
        render.Translate(mw, mh)
        render.Translate(0, self.invScrollOffset)
        map(lambda c: c.passDraw(render), filter(lambda c: not hasattr(c, 'subMenuExpand') or not c.subMenuExpand, self.children))
        render.PopBound()        
        map(lambda c: c.passDraw(render), filter(lambda c: hasattr(c, 'subMenuExpand') and c.subMenuExpand, self.children))

        
    def passMouseMsg(self, x, y, button, state, *args):
        if Component.mouseCapture is not self:            
            if self.passMouseMsgToChildren(x, y, button, state, *args):
                return True # mouse pass to child

            _x, _y = self.local2parent(x, y)
            if not self.hitTest(*Component.parent2local(self, _x, _y)):
                return False
        return self.handleMouseMsg(x, y, button, state, *args)

    def handleSubMenuMouseMsg(self, x, y, button, state, *args):
        if self.fullSize > self.height:
            dw, dh = self.window.size
            sw, sh = self.size
            mw, mh = self.margin
            self.highLit = 'Empty'
            if x > 0 and x < sw:
                if y > 0 and y < mh:
                    self.highLit = 'Up'
                elif y > dh - mh and y < dh:
                    self.highLit = 'Down'
            #print self.highLit
            if self.highLit in ['Up', 'Down']:
                if state in ['DOWN', 'DBCLICK'] and button == 'LEFT':
                    self.scroll(1 if self.highLit == 'Down' else -1)
                return True
        return False
        
    def passMouseMsgToChildren(self, x, y, button, state, *args):
        if self.fullSize > self.height:
            sw, sh = self.size
            dw, dh = self.window.size
            mw, mh = self.margin             
            _x, _y = x, y + mh - self.scrollOffset     # menu space (no scroll)
            if mw < _x and _x < sw - mw and mh < _y and _y < dh - mh:
                ret = super(PopupMenu, self).passMouseMsgToChildren(x, y, button, state, *args)
            else:
                ret = False
            if ret:
                self.highLit = 'Empty'
                return True
            else:
                y = y + mh - self.scrollOffset
                return self.handleSubMenuMouseMsg(x, y, button, state, *args)
        else:
            return super(PopupMenu, self).passMouseMsgToChildren(x, y, button, state, *args)
            
    def handleMouseMsg(self, x, y, button, state, *args):
        btn = button in ['LEFT', 'RIGHT']        
        db = state == 'DBCLICK'
        if btn and db:
            Component.mouseDblClk = True
        # do not handle double click in menu
        ret = super(PopupMenu, self).handleMouseMsg(x, y, button, state, *args)
        if btn and db:
            Component.mouseDblClk = False
        return not btn    # button down / up should pass through to others
        
    def passDraw(self, render):
        """
        overwritable: draw this component
        @rtype: None
        """
        if not self.sightDirty and self.sightframeNumber == render.frameNumber - 1:
            if self.sight == 0:
                print 'WA bug !!!'
            self.sight = render.ReuseSight(self.sight)
            self.sightframeNumber = render.frameNumber
        else:
            self.updateDirtyRect(render)
            if self.visible:
                if hasattr(self, 'sightRect'):
                    self.sight = render.PushSight(self.sightRect.left, self.sightRect.top, self.sightRect.width, self.sightRect.height, self.dirty or self.allSightDirty)
                    #print self.sightRect.rect
                else:
                    self.sight = render.PushSight(self.left, self.top, self.width, self.height, self.dirty or self.allSightDirty)
                self.sightframeNumber = render.frameNumber
                self.beginPassDraw(render)
                
                if self.updateView(render):
                    self.onDraw(render)
                self.drawChild(render)
                render.viewStack.pop()

                self.endPassDraw(render)
                
                render.PopSight()
            self.dirty = False
            self.sightDirty = False

    def scroll(self, z):
        if self.fullSize > self.height:
            self.subMenuOffsetIdx = clamp(0, self.subMenuOffsetIdx+z, len(self.children))
            sw, sh = self.width, self.fullSize
            dw, dh = self.window.size
            h = 0
            idx = 0
            for c in self.children[:self.subMenuOffsetIdx]:
                h += c.height
                if sh - h < dh:
                    h = sh - dh
                    self.subMenuOffsetIdx = idx
                    break
                idx += 1
            
            rh = 0      # remain height
            for c in self.children[self.subMenuOffsetIdx:]:
                rh += c.height
                c.dirty = True
                if rh > dh:
                    break

            self.onScroll(float(h) / self.fullSize)
            self.dirty = True
            return True
        return True
#-----------------------------------------------------------------------
# MenuItem
#-----------------------------------------------------------------------
class MenuItem(Component, TextBase, AutoLayout):
    def __init__(self, parent = None, header = ''):
        Component.__init__(self, parent)
        TextBase.__init__(self)
        AutoLayout.__init__(self)

        # default value
        self.tabStop = False
        self.height = 20
        self.clip = False

        # menu item
        self.header = header
        self.margin = 5, 2, 5, 2
        self.command = ''
        
        # icon
        self.icon = ''
        self.iconMargin = 0,3,5,3
        self.iconWidth = 28

        # sub menu
        self.subMenuSize = 10, 10
        self.subMenuPos = 0, 0
        self.sysMenuItem = False
        self.subMenuExpand = False
        self.subMenuOffset = 0
        self.highLit = 'Empty'

        self.changeEvent('header', self.onHeaderChange)
        self.changeEvent('font', self.onHeaderChange)
        self.changeEvent('fontSize', self.onHeaderChange)
        self.changeEvent('subMenuExpand', self.onSubMenuExpandChange, sync = False)
        self.bind('Click', self.onClick)
        self.bind('Mouse Enter', self.setFocus, postevent = False)
        self.bind('Mouse Wheel', self.scroll)
        self.bind('Focus Change', self.onFocusChange, postevent = False)
        self.bind('Mouse Enter', self.onMouseEnter, postevent = False)
        self.bind('Parent Change', self.onParentChange)
        self.onParentChange()
        
        self.autoDirty(['subMenuExpand', 'highLit', 'sightRect'])
        
    def onSubMenuExpandChange(self):
        if self.subMenuExpand:
            if self.isSubMenuNeedScroll():
                self.subMenuOffset.Assign(0)
            self.subMenuPos = self.__getSubMenuPos()

        popupMenu = self.popupMenu
        if popupMenu:
            popupMenu.onMenuExpandChange()
    
    def getChildren(self):
        front = []
        back = []
        for i in self._children:
            if hasattr(i, 'subMenuExpand') and i.subMenuExpand:
                back.append(i)
            else:
                front.append(i)
        return front + back
    children = property(getChildren)
    
    def __getPopupMenu(self):
        parent = self.parent
        while parent:
            if isinstance(parent, PopupMenu):
                return parent
            parent = parent.parent
        return None
    popupMenu = property(__getPopupMenu)

    def __getSubMenuPos(self):
        mw, mh = self.subMenuSize
        
        # calc the expect position
        if self.sysMenuItem:
            pos = 0, self.height
        else:
            # default sub menu is on the right side
            pm = self.popupMenu
            pos = self.width - (pm.subMenuIndent if pm else 0), -(mh-self.height)/2
            #return (pm.subMenuIndent if pm else 0) - self.subMenuSize[0], 0

            # fix position to prevent outside the window
            dw, dh = self.window.size
            l, t = self.local2global(*pos)
            if l+mw > dw:      # display sub menu on left side
                _l, _t = (pm.subMenuIndent if pm else 0) - mw, pos[1]
                l, t = self.local2global(_l, _t)               
            l = max(0, l)
            if mh > dh:
                t = 0
            else:
                t = clamp(0, t, dh-mh)
            pos = self.global2local(l, t)
        return pos
    #subMenuPos = property(__getSubMenuPos)
    
    def parent2local(self, x, y):
        """
        @param x, y: (x, y) in parent coordinate
        @return: (x, y) in local coordinate
        """
        if self.subMenuExpand:
            y -= self.subMenuOffset
        if self.parent and hasattr(self.parent, 'subMenuExpand') and self.parent.subMenuExpand:
            #assert self.parent.subMenuExpand
            posx, posy = self.parent.subMenuPos
            return x - self.left - posx, y - self.top - posy
        else:
            return x - self.left, y - self.top
        
    def local2parent(self, x, y):
        """
        @param x, y: (x, y) in local coordinate
        @return: (x, y) in parent coordinate
        """
        if self.subMenuExpand:
            y -= self.subMenuOffset
        if self.parent and hasattr(self.parent, 'subMenuExpand') and self.parent.subMenuExpand:
            #assert self.parent.subMenuExpand
            posx, posy = self.parent.subMenuPos
            return x + self.left + posx, y + self.top + posy
        else:
            return x + self.left, y + self.top
    
    def onFocusChange(self):
        if self.children:
            if not self.focus:
                self.subMenuExpand = False

    def onMouseEnter(self):
        if self.children:
            self.subMenuExpand = self.focus
                    
    def onParentChange(self):
        if self.parent and isinstance(self.parent, Menu):
            self.sysMenuItem = True
        else:
            self.sysMenuItem = False
        pass

    def calcMenuSize(self):
        w, h = 100, 0
        for c in self.children:
            w = max(w, c.width)
            h += c.height
        return w, h

    def isSubMenuNeedScroll(self):
        return isinstance(self.subMenuOffset, koan.anim.AnimTarget)

    def scroll(self, z):
        if self.isSubMenuNeedScroll():
            self.subMenuOffsetIdx = clamp(0, self.subMenuOffsetIdx+z, len(self.children))
            sw, sh = self.subMenuSize
            dw, dh = self.window.size
            h = 0
            idx = 0
            for c in self.children[:self.subMenuOffsetIdx]:
                h += c.height
                if sh - h < dh:
                    h = sh - dh
                    self.subMenuOffsetIdx = idx
                    break
                idx += 1
            
            rh = 0      # remain height
            for c in self.children[self.subMenuOffsetIdx:]:
                rh += c.height
                c.dirty = True
                if rh > dh:
                    break

            self.subMenuOffset.Reset(0.3, -h)
            self.dirty = True
            return True
        return hasattr(self, 'subMenuExpand') and self.subMenuExpand
        
    def relayout(self, *argv):
        self.subMenuSize = self.calcMenuSize()
        h = self.window.height
        if self.subMenuSize[1] > h:
            self.subMenuOffset = koan.anim.AnimTarget('decay', 0, 0, 0, self)            
            self.subMenuOffsetIdx = 0
            self.subMenuMaxOffset = self.subMenuSize[1] - h
        else:
            self.subMenuOffset = 0
        
        popupMenu = self.popupMenu
        if self.children:
            top = popupMenu.margin[1]
            for i in self.children:
                if i.visible:
                    i.top = top
                    i.left = popupMenu.margin[0]
                    i.width = self.subMenuSize[0]
                    top += i.height

        if popupMenu:
            self.subMenuSize = self.subMenuSize[0] + popupMenu.margin[0] * 2, self.subMenuSize[1] + popupMenu.margin[1] * 2

    def handleSubMenuMouseMsg(self, x, y, button, state, *args):
        pm = self.popupMenu
        if self.isSubMenuNeedScroll() and pm:
            dw, dh = self.window.size
            sw, sh = self.subMenuSize
            mw, mh = pm.margin
            self.highLit = 'Empty'
            if x > 0 and x < sw:
                if y > 0 and y < mh:
                    self.highLit = 'Up'
                elif y > dh - mh and y < dh:
                    self.highLit = 'Down'
            #print self.highLit
            if self.highLit in ['Up', 'Down']:
                if state in ['DOWN', 'DBCLICK'] and button == 'LEFT':                    
                    self.scroll(1 if self.highLit == 'Down' else -1)
                return True
        return False
        
    def passMouseMsgToChildren(self, x, y, button, state, *args):
        if self.subMenuExpand:
            needScroll = self.isSubMenuNeedScroll()
            if needScroll:
                px, py = self.subMenuPos
                sw, sh = self.subMenuSize
                dw, dh = self.window.size
                pm = self.popupMenu
                if pm:
                    mw, mh = pm.margin
                else:
                    mw, mh = 0, 0                
                _x, _y = x - px, y - py + self.subMenuOffset     # menu space (no scroll)
                if mw < _x and _x < sw - mw and mh < _y and _y < dh - mh:
                    ret = super(MenuItem, self).passMouseMsgToChildren(x, y, button, state, *args)
                else:
                    ret = False
                if ret:
                    self.highLit = 'Empty'
                    return True
                else:
                    if hasattr(self, 'subMenuExpand') and self.subMenuExpand:
                        posx, posy = self.subMenuPos
                        x, y = x - posx, y - posy + self.subMenuOffset
                        return self.handleSubMenuMouseMsg(x, y, button, state, *args)
                    else:
                        return False
            else:
                return super(MenuItem, self).passMouseMsgToChildren(x, y, button, state, *args)
        else:
            return False

    def passMouseMsg(self, x, y, button, state, *args):
        if Component.mouseCapture is not self:            
            if self.passMouseMsgToChildren(x, y, button, state, *args):
                return True # mouse pass to child

            _x, _y = self.local2parent(x, y)
            if not self.hitTest(*MenuItem.parent2local(self, _x, _y)):
                return False
        return self.handleMouseMsg(x, y, button, state, *args)
        
    def expandSight(self, parentSight, xy):
        mySight = koan.Rectangle(*self.rect)        # parent space
        if hasattr(self, 'subMenuExpand') and self.subMenuExpand:
            mySight = mySight.union(
                        koan.Rectangle( self.left + self.subMenuPos[0],
                                        self.top + self.subMenuPos[1],
                                        self.subMenuSize[0],
                                        self.subMenuSize[1]
                        )
                    )
            for i in self.children:
                if hasattr(i, 'subMenuExpand') and i.subMenuExpand:
                    mySight = i.expandSight(mySight, (self.left + self.subMenuPos[0], self.top + self.subMenuPos[1]))

        self.sightRect = mySight
        mySightInParent = koan.Rectangle(*mySight.rect)
        mySightInParent.offset(xy[0], xy[1])
        return parentSight.union(mySightInParent)

    def passDraw(self, render):
        """
        overwritable: draw this component
        @rtype: None
        """
        if not self.sightDirty and self.sightframeNumber == render.frameNumber - 1:
            if self.sight == 0:
                print 'WA bug !!!'
            self.sight = render.ReuseSight(self.sight)
            self.sightframeNumber = render.frameNumber
        else:
            self.updateDirtyRect(render)
            if self.visible:
                if hasattr(self, 'sightRect'): # and self.subMenuExpand:
                    self.sight = render.PushSight(self.sightRect.left, self.sightRect.top, self.sightRect.width, self.sightRect.height, self.dirty)
                else:
                    self.sight = render.PushSight(self.left, self.top, self.width, self.height, self.dirty)
                self.sightframeNumber = render.frameNumber
                
                self.beginPassDraw(render)
                self.onDraw(render)
                self.drawChild(render)
                self.endPassDraw(render)
                
                render.PopSight()
            self.dirty = False
            self.sightDirty = False

    def drawChild(self, render):
        if self.subMenuExpand and self.children:
            needScroll = self.isSubMenuNeedScroll()
            
            render.Translate(*self.subMenuPos)
            
            dw, dh = self.window.size
            sw, sh = self.subMenuSize
            # draw background
            pm = self.popupMenu
            if pm:
                if pm.background:
                    t = render.GetTexture(pm.background, gamma = pm.gamma)
                    render.SetTexture(t)
                elif pm.bgColor[0] > 0:
                    render.SetTexture(None)
                    render.SetColor(*self.bgColor)
                mw, mh = pm.margin
            else:
                render.SetTexture(None)
                mw, mh = 0, 0

            if needScroll:
                rect = 0, 0, sw, dh
                render.DrawRect(rect[0], rect[1]-mh, rect[2], rect[3]+mh)
            else:
                rect = 0, 0, sw, sh
                render.DrawRect(*rect)
            render.SetColor(*color.white)

            # draw up / down button
            
            if needScroll and pm:
                enableUp = self.highLit == 'Up' and -float(self.subMenuOffset) > 0
                enableDown = self.highLit == 'Down' and -float(self.subMenuOffset) < sh - dh
                
                t = render.GetTexture(pm.upImg)
                if t:
                    render.SetTexture(t)
                    if not enableUp:
                        render.PushAlpha(0.5)
                    render.DrawUniformRect(t.GetSize(), (0, 0, rect[2]-rect[1], mh))
                    if not enableUp:
                        render.PopAlpha()
                
                t = render.GetTexture(pm.downImg)
                if t:
                    render.SetTexture(t)
                    if not enableDown:
                        render.PushAlpha(0.5)
                    render.DrawUniformRect(t.GetSize(), (0, dh-mh, rect[2]-rect[1], mh))
                    if not enableDown:
                        render.PopAlpha()
            
            render.PushBound(rect[0]+mw, rect[1]+mh, rect[2]-mw, rect[3]-mh)            
            # translate if menu exceed the size of menu
            render.Translate(0, self.subMenuOffset)
            # draw menuitems
            #PopupMenu.MenuDrawChild(self, render)
            map(lambda c: c.passDraw(render), filter(lambda c: not hasattr(c, 'subMenuExpand') or not c.subMenuExpand, self.children))
            render.PopBound()
            
            map(lambda c: c.passDraw(render), filter(lambda c: hasattr(c, 'subMenuExpand') and c.subMenuExpand, self.children))

    def onHeaderChange(self):
        size = self.calTextSize(self.header, self.font, self.fontSize)
        
        # * 2 for expand icon
        self.size = size[0] + self.margin[0] + self.margin[2] + self.iconWidth * 2,\
                    size[1] + self.margin[1] + self.margin[3]
        pass

    def onClick(self):
        if not self.children and self.command:
            self.invokeCmd(self.command)
            self.invokeCmd('Menu Return', self.command)           

    def passKey(self, key, keymaps):
        if self.subMenuExpand:
            return super(MenuItem, self).passKey(key, keymaps)
        else:
            if not self.enabled or not self.visible or self.blind:
                return False
            return self.onKey(key)
            
    def onKey(self, key):
        if key == 'ENTER':
            self.onClick()
            return True
        elif key == 'RIGHT':
            if self.children:
                self.subMenuExpand = True
                return True
        elif key == 'LEFT':
            if self.children and self.subMenuExpand:
                self.subMenuExpand = False
                return True
        elif key == 'UP' or key == 'DOWN':
            if self.subMenuExpand:
                if menuOnKey(self, key):
                    return True
        return super(MenuItem, self).onKey(key)
        
    def onDraw(self, render):
        # draw background
        super(MenuItem, self).onDraw(render)

        # draw icon
        if self.icon:
            t = render.GetTexture(self.icon)
            render.SetTexture(t)
            pos = self.margin[0], self.iconMargin[1], self.iconWidth-self.iconMargin[2], self.height-self.iconMargin[1]-self.iconMargin[3]
            if t:
                render.DrawUniformRect(t.GetSize(), pos)
            else:
                render.DrawRect(*pos)

        # draw header
        render.DrawTextEx(  self.header,
                            (self.margin[0]+self.iconWidth, self.margin[1], self.width-self.margin[2], self.height-self.margin[3]),
                            self.align, self.fontSize, self.fontColor, self.font)

        # draw expand icon
        if self.children:
            pm = self.popupMenu
            if pm and pm.expandImg:
                m = pm.expandMargin
                pos = self.width-m[0], m[1], m[0]-m[2], self.height-m[3]-m[1]
                t = render.GetTexture(pm.expandImg, gamma = pm.gamma)
                if not self.enabled:
                    render.SetColor(*self.fontColor)
                render.SetTexture(t)
                render.DrawUniformRect(t.GetSize(), pos)
                if not self.enabled:
                    render.SetColor(*color.white)

    def setContent(self, data):
        self.header = data

#-----------------------------------------------------------------------
# CheckItem
#-----------------------------------------------------------------------
class CheckMenuItem(MenuItem, CheckBase):
    def __init__(self, parent = None, **argd):
        MenuItem.__init__(self, parent)
        CheckBase.__init__(self, **argd)

class SelectMenuItem(CheckMenuItem, RadioBase):
    def __init__(self, parent = None):
        CheckMenuItem.__init__(self, parent, check = False)
        RadioBase.__init__(self)

class MenuGroup(StackPanel, GroupBase):
    def __init__(self, parent = None):
        StackPanel.__init__(self, parent)
        GroupBase.__init__(self)
        self.autosize = True        

#-----------------------------------------------------------------------
# MenuSplitter
#-----------------------------------------------------------------------
class MenuSplitter(Static):
    def __init__(self, parent = None):
        Static.__init__(self, parent)
        self.height = 1

#-----------------------------------------------------------------------
# Menu
#-----------------------------------------------------------------------
class Menu(StackPanel):
    def __init__(self, parent = None):
        StackPanel.__init__(self, parent)
        self.orientation = 'Horizontal'
        self.bgColor = color.lightgray
        self.clip = False
        self.press = False



        
if __name__ == '__main__':
    import koan
    from window import Window
        
    koan.init()
    
    w = Window()
    w.create(0, 0, 800, 600, caption = True)
    w.bgColor = color.darkblue
    
    
    def popup(x, y, flag):
    
        import time
        t = time.time()
        m = PopupMenu(w)
        m.margin = 0, 10
        
        def createMenuItem(m, text):
            mi = MenuItem(m)
            mi.fontColor = color.white        
            mi.fontSize = 20
            mi.header = text
            mi.bgColor = color.gray        
            mi.bind('Mouse Enter', setattr, mi, 'bgColor', color.lightgray)
            mi.bind('Mouse Leave', setattr, mi, 'bgColor', color.gray)
            return mi

        for i in range(30):
            mi = createMenuItem(m, 'hello %d' %i)
        '''
        mi = m.children[5]
        mi.bgColor = color.red
        for i in range(50):
            mi2 = createMenuItem(mi, 'sub %d' %i)
            
        mi = m.children[15]
        for i in range(20):
            mi2 = createMenuItem(mi, 'small %d' %i)
                
        m.bgColor = color.purple
        m.xy = x, y
        '''
        print '--------', time.time() - t
        m.doModal()
    
    w.bind('Mouse RUp', popup)
    
    w.show()
    koan.run(1)
    koan.final()

