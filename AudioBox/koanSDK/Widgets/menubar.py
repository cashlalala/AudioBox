import koan
import color
import weakref
from koan.rectangle import Rectangle

from component import Component
from text import TextBase
from button import Button
from panel import StackPanel, DockPanel
from toolbar import Toolbar
from image import ImageBase

#-----------------------------------------------------------------------
# Menubar
#-----------------------------------------------------------------------
class Menubar(StackPanel):
    def __init__(self, parent = None):
        StackPanel.__init__(self, parent)
        self.tabStop = False
        self.orientation = 'Horizontal'
        self.lastFocus = None
        self.bind('Child Visible Change', self.__onChildVisibleChange, postevent = False)

    def __onChildVisibleChange(self, v):
        if self.isVisible():
            self.guestFocusChild()

    def onKey(self, key):
        if key == 'ALT':
            '''
            focusObj = self.window.focusObject
            if focusObj is not self and not self.isDescendant(focusObj):
                self.lastFocus = weakref.ref(focusObj)
                self.setFocus()
                return True
            elif self.lastFocus and self.lastFocus():
                self.lastFocus().setFocus()
                return True
            '''
            pass
        elif key == 'ESC':
            if self.lastFocus and self.lastFocus():
                self.lastFocus().setFocus()
                return True
        elif key.startswith('ALT '):
            if self.focus:
                self.invokeCmd('AltCmd', key)
            else:
                key = key[4:].strip().upper()
                for c in self.children:
                    if hasattr(c, 'altCmd') and c.altCmd == key:
                        focusObj = self.window.focusObject
                        if focusObj is not self and not self.isDescendant(focusObj):
                            self.lastFocus = weakref.ref(focusObj)
                        c.setFocus()
                        return True
            return False
        elif self.focusChild:
            try:
                if key == 'LEFT' or key == 'RIGHT':
                    children = filter(lambda x: x.visible and x.enabled and not x.blind, self.children)
                    idx = children.index(self.focusChild)
                    idx += 1 if key == 'RIGHT' else -1
                    idx = idx % len(children)
                    children[idx].setFocus()
                    return True
            except:
                pass        
        return super(Menubar, self).onKey(key)
#-----------------------------------------------------------------------
# Tray
#-----------------------------------------------------------------------
class PageTray(Component):
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        self.tabStop = False
        self.bind('Child Add', self.__onAddChild)
        
    def __onAddChild(self, c):
        self.bindData('width', c, 'width', dir = '->')
        self.bindData('height', c, 'height', dir = '->')

    def onChangeToolbar(self, page):
        page = getattr(self, page) if hasattr(self, page) else None
        for c in self._children:
            if c is page:
                c.visible = True
            else:
                c.visible = False

#-----------------------------------------------------------------------
# ToolbarTray
#-----------------------------------------------------------------------
class ToolbarTray(StackPanel):
    def __init__(self, parent = None):
        StackPanel.__init__(self, parent, autofix = False)
        self.orientation = 'Horizontal'

    def onChangeToolbar(self, toolbar):
        toolbars = [getattr(self, t) for t in toolbar.split('|') if hasattr(self, t)]
        for c in self._children:
            if not isinstance(c, Toolbar):
                c.visible = True
            elif c in toolbars:
                c.visible = True
            else:
                c.visible = False

    def onAltCmd(self, key):
        children = self.tabChildren
        for c in children:
            if c.onKey(key):
                return
#-----------------------------------------------------------------------
# LabelToolbar
#-----------------------------------------------------------------------
class LabelToolbar(Toolbar):
    def __init__(self, parent = None):
        Toolbar.__init__(self, parent)
        self.label = 'toolbar'
        self.background = ''

#-----------------------------------------------------------------------
# LabelToolbar
#-----------------------------------------------------------------------
class LabelButton(Button, TextBase, ImageBase):
    def __init__(self, parent = None):
        Button.__init__(self, parent)
        TextBase.__init__(self)
        ImageBase.__init__(self)
        self.imgSize = 16, 16
        self.textGap = 0
        self.margin = 5, 5, 5, 5
        self.altCmd = ''
        self.changeEvent('text', self.onResize)
        self.changeEvent('textGap', self.onResize)
        self.changeEvent('imgSize', self.onResize)

    def Init(self):
        self.image = ''

    def onResize(self):
        tw, th = self.textSize
        iw, ih = self.imgSize
        self.width = max(tw, iw) + self.margin[0] + self.margin[2]
        self.height = max(th, th + self.textGap + ih) + self.margin[1] + self.margin[3]

    def onKey(self, key):
        if self.command and key.startswith('ALT '):
            key = key[4:].strip().upper()
            if key in self.altCmd:
                self.invokeCmd(self.command)
                return True
        return super(LabelButton, self).onKey(key)
        
    def onDraw(self, render):        
        iw, ih = self.imgSize
        margin = self.margin

        # draw hight light
        super(LabelButton, self).onDraw(render)

        # draw image
        t = render.GetTexture(self.image)
        render.SetTexture(t)        
        if self.imageColor != color.white:
            render.SetColor(*self.imageColor)        
        x = (self.width - iw)/2
        render.DrawRect(x, margin[1], x+iw, ih+margin[1])
        if self.imageColor != color.white:
            render.SetColor(*color.white)
        # draw text
        tw, th = self.textSize
        render.Translate(margin[0], min(margin[1] + ih + self.textGap, self.height - th - margin[3]))
        TextBase.onDraw(self, render, (0, 0, max(iw, tw), th))
        
#-----------------------------------------------------------------------
# MenubarItem
#-----------------------------------------------------------------------
class MenubarItem(Component, TextBase):
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        TextBase.__init__(self)
        # default value
        self.tabStop = False
        self.height = 20

        # menu item
        self.header = ''
        self.margin = 5, 2, 5, 2
        self.autosize = True
        self.toolbar = ''
        
        self.selected = False

        self.changeEvent('header', self.onHeaderChange)
        self.changeEvent('font', self.onHeaderChange)
        self.changeEvent('fontSize', self.onHeaderChange)
        self.bind('Click', self.setFocus)
        self.autoRemove( self.parent.bind('Focus Child Change', self.onSelectChange) )
        self.bind('Visible Change', self.onSelectChange)
        self.onSelectChange()

    def __getTexPosition(self):
        return self.margin[0], self.margin[1], self.width - self.margin[2], self.height - self.margin[3]
    textPos = property(__getTexPosition)
    
    def onSelectChange(self, *argv, **argd):
        self.selected = self.parent.focusChild == self
        if self.selected:
            self.invokeCmd('Toolbar Change', self.toolbar)

    def onHeaderChange(self):
        header = self.header
        if '_' in header:
            pos = header.find('_')
            if pos < len(header) - 1:
                cmd = header[pos+1]
                if cmd.isalpha():
                    self.altCmd = cmd.upper()
                object.__setattr__(self, 'header', self.header.replace('_','', 1) )        
        if self.autosize:
            size = self.calTextSize(self.header, self.font, self.fontSize)
            self.size = size[0] + self.margin[0] + self.margin[2], size[1]

    def onDraw(self, render):
        super(MenubarItem, self).onDraw(render)
        render.DrawTextEx(self.header, self.textPos, self.align, self.fontSize, self.fontColor, self.font)

    def setContent(self, data):
        self.header = data



if __name__ == '__main__':
    from window import Window
    from panel import Canvas
    from pprint import pprint
    import color

    koan.init()
    
    w = Window()    
    w.create(0, 0, 800, 600, caption = True)
    w.bgColor = color.darkblue
    
    p = Canvas(w)
    p.bindData('width', w, 'width', dir = '<-')
    p.bindData('height', w, 'height', dir = '<-')
    
    m = Menubar(p)
    m.bindData('width', p, 'width', dir = '<-')
    m.height = 30
    
    def focusChange(i):
        i.bgColor = color.white if i.focus else color.gray
            
    i = MenubarItem(m)
    i.header = 'Cr_eate'
    i.height = 30
    i.bgColor = color.white
    i.changeEvent('focus', focusChange, i)
    
    i = MenubarItem(m)
    i.header = '_Home'
    i.height = 30
    i.bgColor = color.white
    i.changeEvent('focus', focusChange, i)
    
    i = MenubarItem(m)
    i.header = 'E_dit'
    i.height = 30
    i.bgColor = color.white
    i.changeEvent('focus', focusChange, i)

    i = MenubarItem(m)
    i.header = 'Tes_t'
    i.height = 30
    i.bgColor = color.white
    i.changeEvent('focus', focusChange, i)
    
    l = LabelButton(p)
    l.rect = 200, 200, 100, 100
    l.altCmd = '5,'
    l.tips = 'Rotate counter-clockwise'
    w.show()
    
    koan.run(1)    
    koan.final()