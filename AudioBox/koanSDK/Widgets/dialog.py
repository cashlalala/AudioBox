import koan
import color
from component import Component, CaptureObject, clamp
from panel import Canvas
from image import Image

#-----------------------------------------------------------------------
# PopupBase
#-----------------------------------------------------------------------
class PopupBase:
    def __init__(self):
        assert isinstance(self, Component)
        from window import Window
        if not isinstance(self.parent, Window):
            raise 'the parent of PopupBase must be a window !!!'
        self.puncture = True
        self.breakLoop = True
        self.retValue = False
        self.retClose = True

        self.closeDuration = 0

    def show(self):
        koan.anim.Execute(self.closeDuration, self.invoke, 'Show Popup')
        
    def closePopup(self):
        self.invoke('Close Popup')
        if self.closeDuration > 0:
            self.blind = True            
            koan.anim.Execute(self.closeDuration, self.close if self.retClose else self.cancel)            
        else:
            koan.anim.PostEvent(self.close if self.retClose else self.cancel)

    def _invokeCmd(self, cmd, *arg):
        if cmd in self.events:
            self.invoke(cmd, *arg)
            return True
        elif self.cmdPath and self.cmdPath():
            return self.cmdPath()._invokeCmd(cmd, *arg)
        elif self.parent:
            return self.parent._invokeCmd(cmd, *arg)

    def _fireCmd(self, cmd, *arg):
        if cmd in self.events:
            self.fire(cmd, *arg)
            return True
        elif self.cmdPath and self.cmdPath():
            return self.cmdPath()._fireCmd(cmd, *arg)
        elif self.parent:
            return self.parent._fireCmd(cmd, *arg)

    def onOk(self):
        self.modalRet('Ok')
    
    def onCancel(self):
        self.modalRet('Cancel')
            
    def cancel(self):
        if not self.breakLoop:
            koan.leaveloop(id(self))
            self.breakLoop = True

    def modalRet(self, value = False):
        self.retValue = value
        self.closePopup()

    def doModal(self, close = True):
        assert self.parent and self.window is self.parent and self.breakLoop
        self.retValue = False
        self.breakLoop = False
        self.setFocus()
        self.show()
        
        window = self.window
        window.hideToolTips()
        # set popup
        popupPool = window._popups
        popupPool.append(self)

        self.retClose = close
        window.prohibitSizing.set(self)
        koan.run(id(self))
        window.prohibitSizing.reset(self)
        
        # relese popup
        popupPool.remove(self)
        if popupPool:
            for i in popupPool[-1::-1]:
                if not i.dead:
                    i.setFocus()
                    break
        
        return self.retValue

    def onKey(self, key):    
        if (key == 'ESC' or key == 'ALT F4'):
            if not self.breakLoop:
                self.onCancel()
            return True
        return False

class Sizer(Image, CaptureObject):
    def __init__(self, parent = None):
        Image.__init__(self, parent)
        CaptureObject.__init__(self)
        self.blind = False
        self.useGlobalCapture = True
        self.bind('Mouse Enter', self.onChangeCursor, True)
        self.bind('Mouse Leave', self.onChangeCursor, False)
        
    def onChangeCursor(self, v):
        if v:
            self.window.setCursor('size nwse')
        else:
            self.window.setCursor('arrow')

#-----------------------------------------------------------------------
# Dialog
#-----------------------------------------------------------------------
class Dialog(Canvas, PopupBase, CaptureObject):
    def __init__(self, parent = None):
        Canvas.__init__(self, parent)
        PopupBase.__init__(self)
        CaptureObject.__init__(self)
        
        self.visible = False
        self.minSize = 100, 50  # minimal dialog size
        
        # margin
        self.__lm = 0   # left margin
        self.__tm = 0   # top margin
        self.__rm = 0   # right margin
        self.__bm = 0   # bottom margin
                
        # border
        '''
        self.border = '3,3,3,3'
        self.bind('Capture Begin', self.onSizeStart)
        self.bind('Capture Offset', self.onSizeMove)
        self.bind('Mouse Enter', self.onChangeCursor, True)
        self.bind('Mouse Leave', self.onChangeCursor, False)
        '''
        # sizer in right bottom
        self.sizable = False        
        self.changeEvent('sizable', self.onSizableChange, postevent = False)

        # command routing
        self.cmdPath = None

    def passMouseMsg(self, x, y, button, state, *args):
        """
        pass mouse message to children, and then process the mouse message
        @param x: mouse pos x in local coordinate
        @param y: mouse pos y in local coordinate
        @rtype: True if mouse over myself or one of my children
        """
        
        if state == 'DOWN' and self.hitTest(x, y) and self.visible and not self.blind and self.enabled:
            self.setFocus()
        
        return super(Dialog, self).passMouseMsg(x, y, button, state, *args)

    def show(self):
        super(Dialog, self).show()
        PopupBase.show(self)
        
    def setFocus(self, hint = ''):
        super(Dialog, self).setFocus(hint)
        window = self.parent  
        if self in window._dialogs:      
            window._dialogs.remove(self)
            window._dialogs.append(self)
        window.dirty = True

    def _invokeCmd(self, cmd, *arg):
        return PopupBase._invokeCmd(self, cmd, *arg)

    def _fireCmd(self, cmd, *arg):
        return PopupBase._fireCmd(self, cmd, *arg)
            
    def setMargin(self, m):
        s = self.clientSize
        self.__lm, self.__tm, self.__rm, self.__bm = m
        self.clientSize = s
    def getMargin(self):
        return self.__lm, self.__tm, self.__rm, self.__bm
    margin = property(getMargin, setMargin)
    
    def __setClientSize(self, s):
        self.width = s[0] + self.__lm + self.__rm
        self.height = s[1] + self.__tm + self.__bm
    def __getClientSize(self):
        return self.width - self.__lm - self.__rm, self.height - self.__tm - self.__bm
    clientSize = property(__getClientSize, __setClientSize)   

    def getClientPos(self):
        return self.__lm, self.__tm, self.width - self.__rm, self.height - self.__bm
    clientPos = property(getClientPos)
        
    def setAttachedProperty(self, prop, **argd):
        name = prop['name'].split('.')[-1].lower()
        data = prop['data']
        if name == 'dock' and data.lower() == 'client':            
            child = prop['child']
            self.dock(child, {'left':self.__lm, 'top':self.__tm, 'right':self.__rm, 'bottom':self.__bm})
        else:
            super(Dialog, self).setAttachedProperty(prop, **argd)

    '''
    def captureTest(self, x, y):
        if not self.hitTest(x, y):
            return False
        return  x < self.left + self.border[0] and \
                y < self.top + self.border[1] and \
                self.right - self.border[2] < x and \
                self.bottom - self.border[3] < y
  
    def onChangeCursor(self, v):
        if v:
            if x < self.left + self.border[0]:
                self.window.setCursor('size ne')
            self.window.setCursor('size nwse')
        else:
            self.window.setCursor('arrow')
    '''
        
    def onSizableChange(self):
        if self.sizable:
            self.sizer = Sizer(self)
            self.dock(self.sizer, {'right':0, 'bottom':0})
            self.sizer.bind('Capture Begin', self.onSizeStart)
            self.sizer.bind('Capture Offset', self.onSizeMove)
        else:
            if hasattr(self, 'sizer'):
                self.sizer.close()
                self.sizer = None

    def onSizeStart(self, x, y):
        self.__capWidth = self.width
        self.__capHeight = self.height

    def onSizeMove(self, x, y):
        self.width = clamp(self.minSize[0], self.__capWidth + x, self.parent.width)
        self.height = clamp(self.minSize[1], self.__capHeight + y, self.parent.height)

    def close(self):
        super(Dialog, self).close()
        self.cancel()

    '''
    def passKey(self, key):
        if key == 'TAB' or key == 'SHIFT TAB':
            if not self.enabled or not self.visible or self.blind:
                return False

            children = self.tabChildren
            if children:
                children.sort(lambda x, y: cmp(x.tabOrder, y.tabOrder))
                idx = -1
                for c in children:
                    if c.focus:
                        idx = children.index(c)
                idx += 1 if key == 'TAB' else -1
                idx = idx % len(children)
                children[idx].setFocus()
                return True
        return super(Dialog, self).passKey(key)
    '''
    def onKey(self, key):
        if PopupBase.onKey(self, key):        
            return True
        return super(Dialog, self).onKey(key)
            

if __name__ == '__main__':
    from window import Window
    koan.init()

    class MyWindow(Window):
        def onKey(self, key):
            if key == 'F1':
                dlg = Dialog(self)
                dlg.bgColor = color.darkgray
                dlg.rect = 100, 100, 400, 300
                ret = dlg.doModal()
                print dlg.children
                return True
            elif key == 'F2':
                dlg = Dialog(self)
                dlg.bgColor = color.darkgray
                dlg.rect = 100, 100, 400, 300
                ret = dlg.doModal(close = False)
                print dlg.children
                dlg.close()         # you should call close by yourself
                return True
            return super(MyWindow, self).onKey(key)
            
    w = MyWindow()
    w.create(0, 0, 640, 480, caption = True)
    w.bgColor = color.black
   
    w.show()
    e = None
    w = None
    
    koan.run(1)
    
    koan.final()
    
    koan.traceLeak()
    
