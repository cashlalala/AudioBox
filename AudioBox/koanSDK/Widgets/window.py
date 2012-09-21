"""
koan Engine

The koan package is used for building the architecture of an uien world.

Use Init() to init this module and Destory() to free that

after Init(), some global read only variables are ready:
          clrWhite: (255, 255, 255, 255)

<img src='../images/image.jpg'>
"""

import sys
import os
import time
import types
import weakref

import traceback
import koan
#from koan.event         import EventManager
from koan.resourcemgr   import ResourceManager
from koan.texmng        import StringTextureManager, ImageTextureManager
from koan.meshmng       import MeshManager
from koan.effectmgr     import EffectManager
from koan.puncture      import PunctureManager
from koan.container     import List

from component          import Component
from dialog             import PopupBase
from menu               import PopupMenu

if koan.isDebug:
    import profile, hotshot, hotshot.stats

#########################################################
#
#   Window
#
#########################################################
import threading

class Window(Component):
    """
    Window -- The window of Koan

    a Singleton Class

    Event:
        -Input Method Change
        - Device Lost
        - Device Restore
        - Page Change
        - Close
        - Window Size Change
        - Console Connect     -> remote desktop connect
        - Enter KoanBox
        - Leave KoanBox
        - Create              -> window has been created
        - Idle                -> window is without input for 500ms

        - Window Mouse Wheel(z)        
        - Window Mouse Down(x, y, *args)
        - Window Mouse Up(x, y, *args)
        - Window Mouse RDown(x, y, *args)
        - Window Mouse RUp(x, y, *args)
        - Window Dbl Click(x, y, *args)  (double click)
        - Window RDbl Click(x, y, *args)
        - Window Mouse Move (x, y, flag)
    """
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        self.tabStop = False
        self.__weakref = {}
        
        self._window = None

        self.punctureManager = None
        self.allowClose     = True
        
        # MCE key map
        self.mceKeyMap = {
            166 : 'BACK',
            8 : 'BACK',
            38: 'UP',
            40: 'DOWN',
            37: 'LEFT',
            39: 'RIGHT',
            13: 'ENTER'
        }
        
        self.render = None
                
        self.clip = False
        self.currentPixelUnit = 1, 1
        
        # dialogs
        self._popups = List()     # all domodal dialog will save here
        self._dialogs = List()
        
        # resource manager
        if not self.parent:
            self.stringTextureManager = None
            self.imageTextureManager = None
            self.meshManager = None
            self.effectManager = None

            self.minimized = False
            self.activated = False
            self.isFullScreen = False
            self.preDrawTime = time.time()
    
            #self.changeEvent('activated', self.resetExclusive, postevent = False, sync = False)
            self.changeEvent('activated', self.resetExclusive, sync = False)
            self.changeEvent('minimized', self.resetExclusive, postevent = False, sync = False)
    
            self.frameNumber = 0
    
            self.ending = False
            self.deviceLosting = True
            self.restoreDelay = 0.01
    
            self.prohibitIdle = koan.Switch()
            self.prohibitSizing = koan.Switch()
            
            self.prohibitExclusive = koan.Switch()
            self.prohibitExclusive.bind("Value Change", self.resetExclusive, postevent = False)
    
            self.defaultUseExclusive = True
            self.isExclusiveNow = False
            
            if koan.isKoanBox:
                self.prohibitExclusive.set(self)
                self.koanbox_activated = False
                self.koanbox_visible = False
                self.changeEvent('koanbox_visible', self.onKoanBoxVisibleChange, postevent = False, sync = False)
    
            # input method
            self.inputmethod = 'KEYBOARD'
            self.changeEvent('inputmethod', self.__inputmethodChange)
            self.__preuseMouseTime = koan.GetTime()
            self.__preuseKeyboardTime = koan.GetTime()
    
            self.preMousePos = -1, -1
            self.useMouseTimeout = 5
            self.useKeyboardTimeout = 5
            #self.wheel_disableMouse = False
            #self.wheel_disableMouseAnim = None
    
            self.vRamNotEnough = False
    
            self.cmdRet = ''
            self.invalid = True
    
            self.autoHideCursor = False
            self.changeEvent('autoHideCursor', self.onChangeAutoHideCursor, sync = False)
            self.changeEvent('invalid', self.onInvalid)
    
            #-------------------------------------------
            # only for Touchstone to maintain busy state
            self.isBusy = False
    
            self.__keyBusy = False
            
            #-------------------------------------------
            # for drag drop
            self.preDragDropComponent = None    # click left button down and prepare to dragdrop (start after mouse moving for a large range)
            self.dragDroping = False    # in drag drop mode
            self.dragDropUp = False      # is drag drop button up
            self.dragDropStartPos = -1, -1
            self.cursor = 'wait'
            self.changeEvent('cursor', self.onChangeCursor, postevent = False)
            '''
            class DropData:
                def __init__(self):
                    self.type = 'files'
                    self.sender = None
                    self.data = []
            self.dropFiles = DropData()
            '''
            self.dropFiles = []
            self.__draggingThumb = None
            self.__draggingThumbX = koan.anim.AnimTarget('decay', 0, 0, 0, self)
            self.__draggingThumbY = koan.anim.AnimTarget('decay', 0, 0, 0, self)
        
            #-------------------------------------------------
            # tool tips
            from tooltips import Tooltips
            self.tooltips = Tooltips()

            #-------------------------------------------------
            # waiting cursor
            self.waitImage = None
            self.changeEvent('waitImage', self.__onResetWaitPosition)
            self.bind('Window Size Change', self.__onResetWaitPosition)
            
            self.autoDirty(['dragDroping'])
            self.bind('close window', self.closeWindow)

    def __onResetWaitPosition(self):
        if self.waitImage:
            self.waitImage.left = (self.width - self.waitImage.width) / 2
            self.waitImage.top = (self.height - self.waitImage.height) / 2
            
    def showWait(self, visible, info = ''):
        koan.peekmessage()
        if self.waitImage and self.waitImage.visible != visible or self.waitImage.info != info:
            print '[window.py] showWait', visible, info
            self.waitImage.visible = visible
            self.waitImage.info = info
            self.waitImage.sightDirty = True
            self.waitImage.sight = 0
            self.PaintWait()
            self.invalid = True

    def setGlobalName(self, name, obj):
        if name not in self.__weakref:            
            self.__weakref[name] = weakref.ref(obj)
        else:
            print '[KXML] window already has a global name (%s) !!!' %(name)

    def getGlobalName(self, name):
        refobj = self.__weakref.get(name, None)
        if refobj:
            return refobj()
        return None

    def getWindow(self):
        return self
    window = property(getWindow)
            
    def onChangeAutoHideCursor(self):
        if self.autoHideCursor is False:
            if self.inputmethod != 'MOUSE':
                self._window.ShowCursor(True)
        else:
            if self.inputmethod != 'MOUSE':
                self._window.ShowCursor(False)

    def enableHideCursor(self, v):
        self.autoHideCursor = v
        
    def showCursor(self, show):
        self._window.ShowCursor(show)
        
    def setCursor(self, cur):
        self.cursor = cur
        
    def onChangeCursor(self):
        if self._window:
            self._window.SetCursor(unicode(self.cursor))

    def setCapture(self, v):
        if self._window:
            self._window.SetCapture(v)
    
    def onInvalid(self):
        if self.invalid and self._window:
            self._window.Dirty()
            
    def show(self):
        if self._window:
            self._window.Show()
            
    def closeWindow(self):
        if self._window:
            self._window.SetCore(None)
            self._window.Close()
            self._window = None
        
    def IsBusy(self):
        """
        query if koan kernel is busy

        @rtype: boolean
        """
        #-------------------------------------------
        # Touchstone Busy state
        if self.isBusy or self.__keyBusy:
            return True
        #-------------------------------------------
        return False

    def GetRenderTime(self):
        return self.render.GetRenderTime()

    def GetFrameNumber(self):
        return self.frameNumber

    def GetCommandReturn(self):
        t = self.cmdRet
        self.cmdRet = u''

        if type(t) == types.UnicodeType:
            return t

        if type(t) == types.StringType:
            return koan.ToUnicode(t)

        if type(t) == types.IntType:
            return unicode(t)
            
        return u''

    def __inputmethodChange(self):
        #print '[window] inputmethodChange : ' + self.inputmethod
        if self._window and self.autoHideCursor:
            self._window.ShowCursor((self.inputmethod == 'MOUSE'))

        self.invoke('Input Method Change')

    def __useMouse(self, x, y, force = True):
        if not force and self.inputmethod != 'MOUSE':
            if abs(self.preMousePos[0] - x) < 10 and abs(self.preMousePos[1] - y) < 10:
                return

        self.inputmethod = 'MOUSE'
        
        if not force and (x, y) == self.preMousePos:
            return

        self.__preuseMouseTime = koan.GetTime()
        self.preMousePos = x, y

    def checkMouseStatus(self):
        if self.inputmethod == 'MOUSE' and self.__preuseMouseTime + self.useMouseTimeout <= koan.GetTime():
            self.inputmethod = ''
        if self.inputmethod == 'KEYBOARD' and self.__preuseKeyboardTime + self.useKeyboardTimeout <= koan.GetTime():
            self.inputmethod = ''

    def CanClose(self):
        ret = self.fire('Want Close')
        if False not in ret:
            if self._window and self.allowClose:
                return True
        return False
        
    def exit(self, *argv):
        """
        to exit window

        @return: if exit succeeded
        @rtype: bool
        """
        print 'Window Exiting ....'        
        if self.CanClose():
            self.ending = True
            self._window.Hide()
            self._window.NotifyClose()
            self.close()
            return True
        print 'Some one deny to close app !!!'
        return False

    def __queryAllowExclusive(self):
        if sys.platform == 'win32':
            if not koan.is3D or not self.isFullScreen or self.minimized or not self.activated:
                return False

            if self.prohibitExclusive:
                return False

            return self.defaultUseExclusive
        else:
            if not koan.is3D or not self.isFullScreen or self.minimized:
                return False
            return self.defaultUseExclusive

    def resetExclusive(self, force = None):
        if force == None:
            canExclusive = self.__queryAllowExclusive()
        else:
            canExclusive = force
        #print 'resetExclusive:', canExclusive
        self.__setExclusive(canExclusive)

    def __setExclusive(self, v):
        #print '__setExclusive', v
        if self.isExclusiveNow != v:
            print 'real set exclusive', v
            self.render.Pause(True)
            print 'after render.Pause(True)'
            self.handleDeviceLost(True)
            if not self.ending and self.render:
                self.render.ToggleFullScreen(v)
                self.handleDeviceLost(False)
                self.isExclusiveNow = v
                self.dirtyAll()

    def toggleFullscreen(self):
        self.fullScreen(not self.isFullScreen)
        
    def fullScreen(self, v):
        """
        toggle full screen mode

        @param v: true -> Full Screen Mode, false -> window mode
        @type v: boolean
        @rtype: None
        """
        if koan.isKoanBox:
            return
            
        print 'fullScreen:', v
        #self.DefaultWinCallback('MOUSEMOVE', -10000, -10000)
        self.onMouseMove(-10000, -10000, '')

        if self.isFullScreen <> v:
            self.isFullScreen = v

            if v:
                self._window.FullScreen(True)
                self.resetExclusive()
            else:
                self.resetExclusive(False)
                self._window.FullScreen(False)

    def minimize(self, v = True):
        print 'want minimize' , v

        if v != self.minimized:
            self.minimized = v
            if v:
                self.resetExclusive(False)
                self._window.MinimizeScreen(True)
            else:
                self.resetExclusive()
                self._window.MinimizeScreen(False)

    def RemoveDevice(self):
        if self.render:
            self.render.Pause(True)
            ResourceManager._clearAll()
            self.render.Close()
            self.render.window = None
            self.render = koan.Null
        
        if self.stringTextureManager:
            self.stringTextureManager.close()
            self.stringTextureManager = koan.Null

        if self.imageTextureManager:
            self.imageTextureManager.close()
            self.imageTextureManager = koan.Null

        if self.meshManager:
            self.meshManager.close()
            self.meshManager = koan.Null
        
        if self.effectManager:
            self.effectManager.close()
            self.effectManager = koan.Null

    def freeDialogs(self):
        self.dirty = True
        while self._dialogs:
            c = self._dialogs[-1]
            if c:
                c.close()        
        self._dialogs = []
        
    def freeChildren(self):
        super(Window, self).freeChildren()
        self.freeDialogs()
        
    def close(self):
        """
        uninitial the koan lib.

        @rtype: None
        """
        if Component.mouseOver:
            Component.mouseOver.invoke('Mouse Leave')
        Component.mouseOver = None
        
        Component.tabStopObj = None
        
        if not self.parent:
            if hasattr(self, 'tooltips') and self.tooltips:
                self.tooltips.close()
                self.tooltips = None
                
            if hasattr(self, 'waitImage') and self.waitImage:
                self.waitImage.close()
                self.waitImage = None
    
            if self.__draggingThumb:
                self.__draggingThumb.close()
                self.__draggingThumb = None
       
            self.handleDeviceLost(True)
            self.RemoveDevice()
            self.prohibitIdle.close()
            self.prohibitExclusive.close()
    
            self.punctureManager.close()
            self.punctureManager = koan.Null
    
            print '[Window.py] Before Fire Close'
            self.fire('Close')
            koan.animManager.pooling()
    
            self.invoke('close window')
            
            koan.windows.remove(self)            
        super(Window, self).close()
        
    def _removeChild(self, c):
        if c.parent == self:
            c._parent = None

        if self.focusChild == c:
            self.focusChild = None

        children = self._dialogs if isinstance(c, PopupBase) else self._children
        
        if c in children:
            self.invoke('Child Remove', c)
            children.remove(c)
            
        if self.focusChild is None and self.isFocused():
            self.guestFocusChild()

    def _addChild(self, c, **argd):
        if c in self._children or c in self._dialogs:
            raise TypeError

        children = self._dialogs if isinstance(c, PopupBase) else self._children
        
        if argd.get('front', False):
            children.insert(0, c)
        else:
            children.append(c)

        if not self.focusChild:
            self.focusChild = c
        self.invoke('Child Add', c)

    def getChildren(self):
        return self._children + self._dialogs
    children = property(getChildren)
    
    def getTabChildren(self):
        children = []
        if self._popups:
            children = self._popups[-1].tabChildren
        else:
            dialogs = filter(lambda x: x.focus and x.visible and x.enabled and not x.blind, self._dialogs)
            if dialogs:
                children = dialogs[-1].tabChildren
            else:
                for c in self._children:
                    if c.visible and c.enabled and not c.blind:
                        if c.tabStop:
                            children.append(c)
                        children += c.tabChildren
        return children
    tabChildren = property(getTabChildren)
    
    def passMouseMsgToChildren(self, x, y, button, state, *args):
        #---------------------------------------------
        # check if any child is focus
        #---------------------------------------------
        for c in self.children[::-1]:
            # 1. last time is over or mouse down, we should focus to recheck again
            # 2. check only if child pass hitTest
            #if c not in self._popups and c.visible and c.enabled and not c.blind:
            if c not in self._popups and c.visible and not c.blind:   # disabled control still should pass mouse event to child
                _x, _y= c.parent2local(x, y)
                if c.passMouseMsg(_x, _y, button, state, *args):
                    return True
        return False

    def passMouseMsg(self, x, y, button, state, *args):
        if self._popups:
            for c in self._popups[::-1]:
                _x, _y= c.parent2local(x, y)
                ret = c.passMouseMsg(_x, _y, button, state, *args)
                if ret or not isinstance(c, PopupMenu):
                    return ret
        return super(Window, self).passMouseMsg(x, y, button, state, *args)

    def DispatchMessage(self, func, *arg):
        """
        dispatch messages

        @param func: message type, one of:
                    1. mouse message
                    2. key event
                    3. command
        @type func: string
        @param arg: additional arguments
        @rtype: None
        """
        if func == 'passMouseMsg':
            Component.mouseDblClk = False
            
            if Component.mouseCapture:
                x, y = self.local2global(arg[0], arg[1])
                x, y = Component.mouseCapture.global2local(x, y)
                return Component.mouseCapture.passMouseMsg(x, y, *arg[2:])
            else:
                pt = self.global2local(arg[0], arg[1])
                return self.passMouseMsg(pt[0], pt[1], *arg[2:])
        elif func == 'passKey':
            return self.passKey(arg[0], {})
        elif func == 'passQueryDrop':
            pt = self.global2local(arg[0], arg[1])
            return self.passQueryDrop(pt[0], pt[1], *arg[2:])
        else:
            f = getattr(self, func)
            f(*arg)
            return
            for c in self._children[::-1]:
                f = getattr(c, func)
                f(*arg)

    def ForcePaint(self):
        #print '[window] ForcePaint'
        koan.animManager.pooling()
        self.dirtyAll()
        self.PaintScreen()

    def prepareDragDrop(self, x, y, obj, draggingThumb = None):
        #print '[window.py] prepareDragDrop', obj
        self.preDragDropComponent = obj
        self.dragDropStartPos = x, y
        if draggingThumb != None:
            if self.__draggingThumb != None:
                self.__draggingThumb.close()
            self.__draggingThumb = draggingThumb
            #self.__draggingThumbX.ForceAssign(x)
            #self.__draggingThumbY.ForceAssign(y)
            self.setDirty()

    def isDragDropUp(self):
        return self.dragDropUp
    
    def beginDragDrop(self):
        if self.preDragDropComponent:
            self.preDragDropComponent.fire('Set Drop Files', self.dropFiles)
            dropMode = self.preDragDropComponent.dropMode
            self.preDragDropComponent = None
            self.dragDroping = True
            self.dragDropUp = True
            
            #print '[window.py] beginDragDrop', self.preDragDropComponent
            if dropMode != 'ole':
                self.setCursor('query')
            else:
                files = u''
                if len(self.dropFiles):
                    for f in self.dropFiles:
                        files += (koan.ToUnicode(f)+u'\0')
                    files += u'\0'
                    self._window.DoDragDrop(files, len(files))
                #else:
                #    self._window.DoDragDrop(u'', 0)
                self.endDragDrop()

    def endDragDrop(self):
        assert self.preDragDropComponent == None
        self.setCursor('arrow')
        self.dragDroping = False
        self.dropFiles = []
        if self.__draggingThumb != None:
            if self.__draggingThumb != None:
                self.__draggingThumb.close()
            self.__draggingThumb = None
            self.__draggingThumbX.ForceAssign(-10000)
            self.__draggingThumbY.ForceAssign(-10000)
        #print '[window.py] endDragDrop'

    def onMoveWindow(self):
        if not self.isFullScreen:
            self._window.EnterMovingMode()
            self.onMouseLUp(0, 0, '')

    def __getFocusObject(self):
        c = self.focusChild
        while c and c.focusChild:
            c = c.focusChild
        return c
    focusObject = property(__getFocusObject)
    
    def onVScroll(self, wParam, lParam):
        if self.focusChild == None:
            print 'warning: no focused child'
            return
        c = self.focusObject
        if c:
            c.passScrollMsg('V', wParam, lParam)
    
    def onHScroll(self, wParam, lParam):
        if self.focusChild == None:
            print 'warning: no focused child'
            return
        c = self.focusObject
        if c:
            c.passScrollMsg('H', wParam, lParam)
        
    def onMouseWheel(self, x, y, z):
        """
        send Mouse wheel message

        @param x, y: position of mouse
        @param z: wheel position?
        @rtype: None
        """
        self.invoke('Window Mouse Wheel', z)
        
        if self.focusChild == None:
            print 'warning: no focused child'
            return
        c = self.focusObject
        if c:
            c.passWheelMsg(z)

        self.__useMouse(x, y)

        #if self.wheel_disableMouseAnim:
        #    self.wheel_disableMouseAnim.remove()
        #    self.wheel_disableMouseAnim = None
        #self.wheel_disableMouse = True
        #self.wheel_disableMouseAnim = koan.anim.Execute(0.1, setattr, self, "wheel_disableMouse", False)

    def onMouseMove(self, x, y, flag):
        """
        send Mouse move message

        @param x, y: position of mouse
        @rtype: None
        """
        #print '[window] onMouseMove', x, y
        #if self.wheel_disableMouse:
        #    return
        self.invoke('Window Mouse Move', x, y, flag)
        
        if self.preDragDropComponent:
            if abs(self.dragDropStartPos[0] - x) > 10 or abs(self.dragDropStartPos[1] - y) > 10:
                self.beginDragDrop()
        elif self.dragDroping:
            pass # query drag drop
            
        self.__useMouse(x, y, False)

        if self.inputmethod == 'MOUSE':
            if self.dragDroping:
                self.DispatchMessage('passQueryDrop', x, y, 'QUERY')
            else:
                ret = self.DispatchMessage('passMouseMsg', x, y, '', '', flag)
                if ret == False and Component.mouseOver:
                    Component.mouseOver.isMouseOver = False
                    Component.mouseOver.invoke('Mouse Leave')                    
                    Component.mouseOver = None

        # support dragging thumb
        if self.__draggingThumb != None:
            if self.dragDroping:
                self.__draggingThumbX.ForceAssign(x)
                self.__draggingThumbY.ForceAssign(y)
            else:
                self.__draggingThumbX.ForceAssign(-10000)
                self.__draggingThumbY.ForceAssign(-10000)

    def onMouseRDown(self, x, y, flag):
        """
        send Mouse R Button down message

        @param x, y: position of mouse
        @rtype: None
        """
        self.invoke('Window Mouse RDown', x, y, flag)
        self.__useMouse(x, y)
        self.DispatchMessage('passMouseMsg', x, y, 'RIGHT', 'DOWN', flag)

    def onMouseRUp(self, x, y, flag):
        """
        send Mouse R Button up message

        @param x, y: position of mouse
        @rtype: None
        """
        self.invoke('Window Mouse RUp', x, y, flag)
        self.__useMouse(x, y)
        self.DispatchMessage('passMouseMsg', x, y, 'RIGHT', 'UP', flag)

        if Component.mouseRDownIn:
            #print '[window] State error, fix it\n'
            Component.mouseRDownIn = None
        
    def onMouseLDown(self, x, y, flag):
        """
        send Mouse L Button down message

        @param x, y: position of mouse
        @rtype: None
        """
        #print '[window] onMouseLDown'
        self.invoke('Window Mouse Down', x, y, flag)
        self.__useMouse(x, y)
        self.DispatchMessage('passMouseMsg', x, y, 'LEFT', 'DOWN', flag)

    def onMouseLUp(self, x, y, flag):
        """
        send Mouse L Button up message

        @param x, y: position of mouse
        @rtype: None
        """
        #print '[window] onMouseLUp'
        self.invoke('Window Mouse Up', x, y, flag)
        self.__useMouse(x, y)

        if Component.mouseDownIn:
            _x, _y = self.local2global(x, y)
            _x, _y = Component.mouseDownIn.global2local(_x, _y)
            Component.mouseDownIn.invoke('Mouse Up', _x, _y, flag)
            Component.mouseDownIn = None
    
        if Component.mouseRDownIn:
            _x, _y = self.local2global(x, y)
            _x, _y = Component.mouseRDownIn.global2local(_x, _y)
            Component.mouseRDownIn.invoke('Mouse RUp', _x, _y, flag)
            Component.mouseRDownIn = None

        if self.dragDroping:
            #self.DispatchMessage('passMouseMsg', x, y, 'DROP', 'UP')
            self.DispatchMessage('passQueryDrop', x, y, 'DROP', self.dropFiles)
            self.endDragDrop()
        else:
            if self.preDragDropComponent:
                assert self.dragDroping == False
                self.preDragDropComponent = None
            self.DispatchMessage('passMouseMsg', x, y, 'LEFT', 'UP', flag)

        if Component.mouseDownIn:
            #print '[window] State error, fix it\n'
            Component.mouseDownIn = None

        self.dragDropUp = False

    def onMouseLDblClk(self, x, y, flag):    
        self.invoke('Window Dbl Click', x, y, flag)        
        self.DispatchMessage('passMouseMsg', x, y, 'LEFT', 'DBCLICK', flag)

    def onMouseRDblClk(self, x, y, flag):
        self.invoke('Window RDbl Click', x, y, flag)
        self.DispatchMessage('passMouseMsg', x, y, 'RIGHT', 'DBCLICK', flag)

    def onDropFiles(self, x, y, f):
        self.DispatchMessage('passQueryDrop', x, y, 'DROP', [f])
        pass

    def queryDropEffect(self, x, y):
        '''
        querty drop effect
        @param x: cursor x position
        @param y: cursor y position
        @rtype 0: none effect, 1: copy effect
        '''
        return self.DispatchMessage('passQueryDrop', x, y, 'QUERYEX')
           
    def canSizing(self):
        return not self.prohibitSizing      
        
    def onSize(self, w, h):
        """
        sent the window resize message

        @param w: the new width
        @param h: the new height
        @rtype: None
        """
        self.width = w
        self.height = h
        
        if self.render:
            if koan.isRUI:
                self.render.OnSize(w, h)

            self.render.NotifyMove()

        if self.isFullScreen:
            if (w, h) <> self._window.GetClientSize():
                print '[koan] WA.... why in fullscreen but window mode is not equ screen size', (w, h), self._window.GetClientSize()
            w, h = self._window.GetClientSize()

        #for c in self._children:
        #   i.width, i.height = w, h
        self.invoke('Window Size Change')

        self.dirtyAll()

        if not self.deviceLosting:
            self.ForcePaint()

    def dirtyAll(self):
        self.invalid = True
        self.dirty = True
        self.frameNumber += 1
        map(lambda x: x.setDirty(), self._children)

    def onKoanBoxVisibleChange(self):
        if self.koanbox_visible:
            print '[window] Enter KoanBox'
            self.fire('Enter KoanBox')
        else:
            print '[window] Leave KoanBox'
            self.fire('Leave KoanBox')

    def onActivateKoanBox(self, active):
        print '[window] onActiveKoanBox %s' %(str(active))
        if active:
            # restore device
            self.koanbox_activated = True
            self.handleDeviceLost(True)
            if self.render.PauseDevice(False):
                self.handleDeviceLost(False, self.restoreDelay)
                self.koanbox_visible = True
                self.ForcePaint()
        else:
            # pause device
            self.koanbox_activated = False
            self.koanbox_visible = False
            self.handleDeviceLost(True)
            self.render.PauseDevice(True)

    def translateMCEKey(self, key):
        try:
            return self.mceKeyMap[key]
        except:
            return 'MCE_'+str(key)

    def onMCERemoteEvent(self, mce_keycode):
        if mce_keycode == 166 or mce_keycode == 8:
            key = self.translateMCEKey(mce_keycode)
            if self.keyin(key) is False:
                print '[window] MCE onRemoteEvent return False'
                self._window.OnCloseKoanBox()
                return False
            return True
           
        key = self.translateMCEKey(mce_keycode)
        print '[window] MCE onRemoteEvent ' + key
        self.keyin(key)
        return True

    def onKoanBoxCommand(self, key, pm):
        self.cmdRet = 0
        if key == 'IsKoanReady':
            if self.IsBusy():
                return 0
            return 1
        return 0
        
    def DefaultWinCallback(self, msg, pm1 = 0, pm2 = 0):
        """
        the default window procedual

        @param msg: the window message
        @type msg: string
        @param pm1: additional parameter
        @param pm2: additional parameter
        @return: if this window should be closed
        @rtype: boolean
        """ 
        # Others
        if msg == 'MOVE':
            if self.render:
                self.render.NotifyMove()

        elif msg == 'IDLE':
            if not self.prohibitIdle:
                self.invoke('Idle', pm1 / 1000.0)

        elif msg == 'REFRESH':
            koan.animManager.pooling()
            if koan.is3D:
                if self.render:
                    self.render.NotifyMove()
            else:
                if pm1 == 1:
                    self.dirtyAll()
                self.invalid = True
            self.PaintScreen()
            pass

        elif msg == 'CHAR':
            self.inputmethod = 'KEYBOARD'
            self.__preuseKeyboardTime = koan.GetTime()
            self.keyin(pm1)

        elif msg == "TASK SWITCH":
            print "[koan] TASK SWITCH"
            self.activated = False

        elif msg == "ACTIVATE":
            print "[koan] ACTIVATE", pm1
            self.activated = pm1
            self.invoke('Activate App', self.activated)

        elif msg == "TIME CHANGE":
            pass
            
        elif msg == 'COMMAND':
            if pm1 == 'General':
                r = self.onCommand(pm1, pm2)
                if not r:
                    koan.anim.PostEvent(self.DispatchMessage, 'passCommand', pm1, pm2)
                else:
                    self.cmdRet = r
            else:
                koan.anim.PostEvent(self.DispatchMessage, 'passCommand', pm1, pm2)

        elif msg == 'KOANBOX':
            r = self.onKoanBoxCommand(pm1, pm2)
            self.cmdRet = r

        elif msg == 'CLOSE':
            if self.exit():
                return 1
            return 0

        elif msg == 'FORCE CLOSE':
            self.close()
            self.ending = True
            return 1
            
        elif msg == 'ACTIVEX':
            r = self.onAxCommand(pm1, pm2)
            self.cmdRet = r

        elif msg == 'TOGGLE FULLSCREEN':
            print "TOGGLE FULLSCREEN"
            self.fullScreen(not self.isFullScreen)

        elif msg == 'MINIMIZED':
            self.minimized = pm1

        elif msg == 'MAXIMIZED':
            koan.anim.PostEvent(self.fullScreen, True)

        elif msg == 'DEVICE LOST' or msg == 'DISPLAY_CHANGE':
            print "[koan] Receive DEVICE LOST message " + str(pm1)
            if pm1 == 0:
                self.doDeviceLost()
            else:
                koan.anim.Cancel(self.doDeviceLost)
                koan.anim.Execute(pm1/1000.0, self.doDeviceLost)

        elif msg == 'DEVICE FAILED':
            print "[koan] Receive DEVICE FAILED message"
            self.ChangeDevice(device = 'gdi')
            
        elif msg == 'CHILD WINDOW ATTACH' \
            or msg == 'CHILD WINDOW POSITION CHANGE' \
            or msg == 'CHILD WINDOW DETACH' \
            or msg == 'CHILD WINDOW VISIBLE CHANGE':
            self.punctureManager.invoke('Reset')

        elif msg == 'ENTER SIZEMOVE':
            #print 'ENTER SIZEMOVE'
            self.render.SetIsMoving(True)
        elif msg == 'EXIT SIZEMOVE':
            #print 'LEAVE SIZEMOVE'
            self.render.SetIsMoving(False)

        else:
            print 'Invoke platform message', msg, pm1, pm2
            self.invoke(msg, pm1, pm2)
        return 1

    def __resetKeyBusy(self):
        self.__keyBusy = False

    def keyBusy(self):
        self.__keyBusy = True

        koan.anim.Cancel(self.__resetKeyBusy)
        koan.anim.Execute(0, self.__resetKeyBusy)

    def keyin(self, key):
        #print '[window] key in %s' %(key)
        if self.__keyBusy:
            return True
        ret = self.DispatchMessage('passKey', key)
        if (key == 'ESC' or key == 'BACK') and koan.isKoanBox and ret is False:
            print '[window] KoanBox keyin "ESC" return False, will close application !!!'
            self._window.OnCloseKoanBox()
        return ret

    def PaintWait(self):    
        assert self.waitImage
        render = self.render
        render.viewStack.append(self.rect)
        self.frameNumber += 1
        render.frameNumber = self.frameNumber
        try:
            render.BeginRender()
            if not self.deviceLosting:
                render.IdentityWorld()
                if self.sight != 0:
                    self.sight = render.ReuseSight(self.sight)
                    self.sightframeNumber = 0
                # draw wait 
                if not self.parent:
                    self.waitImage.passDraw(render)
            render.EndRender(False)
        except:
            print '[window] PaintWait failed!!!'
            traceback.print_exc()
        
        render.viewStack.pop()
        assert len(render.viewStack) == 0, 'render.viewStack is not sync'

    def PaintScreen(self):
        render = self.render

        if not render or self.ending:
            if koan.animManager:
                koan.animManager.fireExecuteTasks()
            return

        if self.invalid:
            render.viewStack.append(self.rect)
            render.forceSightDirty = None
            self.frameNumber += 1
            render.frameNumber = self.frameNumber
            try:
                render.BeginRender()
                if not self.deviceLosting:
                    render.IdentityWorld()
                    self.passDraw(render)

                # draw tooltips
                if not self.parent:
                    self.tooltips.passDraw(render)

                # draw wait 
                if not self.parent and self.waitImage:
                    self.waitImage.passDraw(render)

                render.EndRender()
            except:
                print '[window] PaintScene failed!!!'
                traceback.print_exc()
            
            render.viewStack.pop()
            assert len(render.viewStack) == 0, 'render.viewStack is not sync'

            self.invalid = False
            self.preDrawTime = time.time()
            
        koan.animManager.fireExecuteTasks()

    # override drawChild to draw the dragging thumb
    def drawChild(self, render):
        map(lambda c: c.passDraw(render), self._children)
        map(lambda c: c.passDraw(render), self._dialogs)

        if not self.parent:
            if self.dragDroping and self.__draggingThumb != None:
                render.PushMatrix()
                render.Translate(self.__draggingThumbX, self.__draggingThumbY)
                self.__draggingThumb.beginPassDraw(render)
                self.__draggingThumb.onDraw(render)
                self.__draggingThumb.endPassDraw(render)
                render.PopMatrix()

    def resetToolTipsPosition(self, (x, y)):
        ox, oy = 0, 10          # offset x, y
        if hasattr(self, 'tooltips') and self.tooltips:
            w, h = self.tooltips.size
            if y+oy+h < self.height:    self.tooltips.top = y+oy
            else:                       self.tooltips.bottom = y-oy
            if x+oy+w < self.width:     self.tooltips.left = x+ox
            else:                       self.tooltips.right = x-ox
        
    def showToolTips(self, text, xy):
        if hasattr(self, 'tooltips') and self.tooltips and not self.tooltips.visible:
            #print '----------- show tips', text
            self.tooltips.text = text
            koan.anim.PostEvent(self.resetToolTipsPosition, xy)
            self.tooltips.visible = True
            self.invalid = True

    def hideToolTips(self):
        if hasattr(self, 'tooltips') and self.tooltips and self.tooltips.visible:
            #print '----------- hide tips'
            self.tooltips.text = ''
            self.tooltips.visible = False
            self.invalid = True
        
    def doDeviceLost(self):
        print "[koan] doDeviceLost"
        self.handleDeviceLost(True)
        self.dirtyAll()        
        if self.render.Restore():
            self.handleDeviceLost(False, self.restoreDelay)
            self.ForcePaint()
            if koan.isKoanBox and self.koanbox_activated:
                self.koanbox_visible = True

    def doDeviceRestore(self):
        self.fire('Device Restore')

    def handleDeviceLost(self, lose, restoreDelay = 0):
        """
        @rtype: None
        """
        print 'handleDeviceLost', lose
        if not lose:
            # ok, device is ready to use
            if self.deviceLosting and self.render:
                print '[handle DeviceLost] Start Device Restore'
                self.deviceLosting = False
                if restoreDelay == 0:
                    self.fire('Device Restore')
                else:
                    koan.anim.Cancel(self.doDeviceRestore)
                    koan.anim.Execute(restoreDelay, self.doDeviceRestore)
                # after devise lost in 3DLP mode, force to repaint all
                if koan.useAnimation:
                    self.render.NotifyMove()
                print '[handle DeviceLost] End Device Restore'
        else:
            if not self.deviceLosting:
                self.deviceLosting = True
                print '[handle DeviceLost] Start Device Lost'
                koan.anim.Cancel(self.doDeviceRestore)
                self.fire('Device Lost')
                print '[handle DeviceLost] End Device Lost'

    def ChangeDevice(self, **argd):
        """
        Change Device to dname

        @kwparam dname: the device type, one of auto, 2D, 3D, default is auto
        @kwparam force:
        @rtype: None
        """
        self.handleDeviceLost(True)
        self.RemoveDevice()

        from koan.renderer import render3d

        class KoanRender(render3d.CRender, koan.draw.UtilRender):
            pass

        self.render = KoanRender()
        self.render.window = self
        self.render.viewStack = []
        self.render.forceSightDirty = None

        self.render.CBufferTexture = render3d.CBufferTexture
        self.render.CAnimatedTexture = render3d.CAnimatedTexture
        self.render.CDynamicTexture = render3d.CDynamicTexture
        self.render.CMovieTexture = render3d.CMovieTexture
        self.render.CFileTexture = render3d.CFileTexture
        self.render.CFontTexture = render3d.CFontTexture
        self.render.CDynTexture = render3d.CDynTexture
        self.render.CRenderTexture = render3d.CRenderTexture
        self.render.CAutoPackTexture32 = render3d.CAutoPackTexture32
        self.render.CMesh = render3d.CMesh
        self.render.CEffect = render3d.CEffect

        device_type = {
            'dx9': render3d.DX9_RENDER,
            'dx7': render3d.DX7_RENDER,            
            'gdi': render3d.GDI_RENDER,
            'gdi+': render3d.GDIPLUS_RENDER,
        }

        device = argd.get('device', 'dx9')
        if 'DX9' in sys.argv or 'dx9' in sys.argv:
            device = 'dx9'
        elif 'DX7' in sys.argv or 'dx7' in sys.argv:
            device = 'dx7'
        elif 'GDI' in sys.argv or 'gdi' in sys.argv:
            device = 'gdi'
        elif 'GDI+' in sys.argv or 'gdi+' in sys.argv:
            device = 'gdi+'
       
        #if not koan.platform.CanUse3D():
        #device, detectResult = koan.platform.AutoDetectRenderer()

        device = device.lower()
        
        isok = False
        try_devices = [device]
        if argd.get('fallback', False):
            try_devices += filter(lambda d: d != device, device_type.keys())
            
        deviceID = 0
        while not isok and deviceID < len(try_devices):
            isok = self.render.Create( self._window.GetWnd(),
                                       koan.clock,                                       
                                       device_type[try_devices[deviceID]],
                                       argd.get('fullBuffer', True),
                                       argd.get('zBuffer', True),
                                       argd.get('vsync', True),
                                       koan.isKoanBox
                                      )
            if isok and self.render.Is3D():
                from koan.renderer import allocator
                self.render.allocator = allocator           # preload for dll path issue
                try:
                    import ctypes
                    ver = ctypes.windll.kernel32.GetVersion()
                    majver = ver & 0xff
                    minver = (ver & 0xff00) > 8
                    if majver < 6:
                        raise Exception
                    from koan.renderer import presenter
                    self.render.presenter = presenter       # preload for dll path issue
                except:
                    print '[window.py] do not support evr presenter !!!'
            else:
                print '[window.py] Can not create %s !!!' %(try_devices[deviceID])
                deviceID += 1

        if not isok:            
            if koan.error:
                koan.error()
            sys.exit(0)               
            return False

        self.stringTextureManager = StringTextureManager(window = self)
        self.imageTextureManager = ImageTextureManager(window = self)
        self.meshManager = MeshManager(window = self)
        self.effectManager = EffectManager(window = self)
        
        self.dirtyAll()

        self.render.SetHint('Background Render', argd.get('bgRender', False))
        self.render.SetHint('Frame Control', koan.frameControl)
        koan.is3D = self.render.Is3D()
        if argd.has_key('useAnimation'):
            koan.useAnimation = argd['useAnimation']
        else:
            koan.useAnimation = self.render.Is3D()

        self.handleDeviceLost(False)
        self.deviceLosting = False
        self.vRamNotEnough = False

        print '---------------------------'
        print 'Change Device:'
        print self.render.GetRenderName()
        print '---------------------------'
        return True

    def create(self, l, t, w, h,
               caption = False, border = True, resize = True, minmax = False,
               frame = False, blur = False,
               fullscreen = False,
               **argd):
        """
        Init koan lib.

        @rtype: None
        """
        # following is waiting function

        self._window = koan.platform.CreateWindow()
        koan.windows.append(self)
        self.punctureManager = PunctureManager(self)

        if koan.isKoanBox:
            try:
                # run parameter
                import getopt
                optlist, args = getopt.gnu_getopt(sys.argv, 'w:h:W:H:')
                for o, a in optlist:
                    if o.lower() == '-w':
                        w = int(a)
                    if o.lower() == '-h':
                        h = int(a)
            except:
                pass

        dw, dh = self._window.GetDesktopSize()
        if w > dw or h > dh:
            w, h = 800, 600

        window_classname = unicode(argd.get('classname', 'Koan'))
        window_title = unicode(argd.get('title', 'CyberLink'))
        window_defaultMaximize = argd.get('defaultMaximize', False)
        window_layeredWindow = argd.get('layeredWindow', False)
        window_visible = argd.get('windowvisible', True)
        self._window.SetCore(self)
        
        self._window.Create(
            window_classname, window_title,
            int(w), int(h),
            caption, border, resize, minmax,
            blur, frame,
            window_defaultMaximize,
            window_layeredWindow,
            koan.isKoanBox, koan.isRUI
        )
        if not koan.isKoanBox and window_visible:
            self._window.SetWindowPos(l, t)

        if fullscreen:
            print '[window] default use Fullscreen'
            self.isFullScreen = True
            self._window.FullScreen(True, False)            
        else:
            print '[window] default use window mode'            

        if hasattr(self, "CustomChangeDevice"):
            ret = self.CustomChangeDevice(**argd)
        else:
            ret = self.ChangeDevice(**argd)
        if not ret:
            return False
        
        self.defaultUseExclusive = koan.config.getBool("RENDER", "DefaultUseExclusive", False)

        if self.defaultUseExclusive:
            print '[window] Default use Exclusive mode'

        koan.anim.PostEvent(self.resetExclusive)

        # check mouse status
        self.autoRemove( koan.anim.IntervalExecute(2, self.checkMouseStatus) )

        self.invoke('Create')
        return True
            
    def onKey(self, key):
        if koan.isDebug and key == 'CTRL F8':
            self.trace('rect:r', 'visible:v', 'focus:f', 'focusChild:fc', 'isActive:a', id = False, fullname = False)
            return True
        
        if key == 'ALT F4' and not self.parent:
            self.exit()
            return True

        if key.startswith('ALT'):
            from menubar import Menubar
            if self._popups:
                o = self._popups[-1].find(Menubar, visible = True)
                if o:
                    return o.onKey(key)
            else:
                for c in self._children:
                    o = c.find(Menubar, visible = True)
                    if o:
                        return o.onKey(key)
        return super(Window, self).onKey(key)
    
#########################################################
#
#   Test This Module
#
#########################################################
if __name__ == '__main__':
    from window import Window
    from panel import StackPanel
    from image import Image
    import color

    class WaitInfo(Image):
        def __init__(self, parent = None):
            Image.__init__(self, parent)
            self.stretch = 'Uniform'
            self.info = ''
            
        def onDraw(self, render):
            super(WaitInfo, self).onDraw(render)
            render.DrawTextEx(self.info, self.localRect, 'C', 18, color.white, 'Segoe UI*bold&effect = Broad&amp;depth = 1&bgcolor = 255, 0, 0, 0')

    class MyWindow(Window):
        def __init__(self, parent = None):
            Window.__init__(self, parent)
            self.animTime = 1.0
            self.a = koan.anim.AnimLinear(self.animTime, (0, 0.6, 1), (0, 1, 1))
            self.a2 = koan.anim.AnimLinear(self.animTime, (0, 0.3, 1), (0, 0, 1))
            self.off = 0.5
            self.effect = 'OpenFadeEffect'
            self.autoDirty(['off', 'effect'])
            self.waitImage = WaitInfo()
            self.waitImage.visible = False
            self.waitImage.image = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\scan\scan.xml'
            self.waitImage.size = 400, 70
        
        def testFlash(self, render):
            for i in range(50):
                t = render.GetTexture(r'C:\Users\chunming_su\Pictures\Welcome Scan.jpg')
                render.SetTexture(t)
                render.DrawRect(*self.localRect)

        def testFloatingIssue(self, render):
            #t = render.GetTexture( r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\seekbar\seek_btn_p.png|(2,2,2,2,"linear")' )
            #t = render.GetTexture( r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\seekbar\seek_btn_p.png|(2,2,2,2)' )
            #t = render.GetTexture( r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\scrollbar\scroll_slider_horz_n.png|(3 3 3 3 "linear")' )
            #t = render.GetTexture( r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\scrollbar\scroll_slider_p.png|(5,2,5,2)' )
            t = render.GetTexture( r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\seekbar\seek_btn_p.png|(1,1,1,1)' )
            render.SetTexture(t)
            off = self.off
            render.DrawRect(100+off, 100+off, 200+off, 200+off)

        def testMultiTexture(self, render):
            self.time = koan.anim.AnimLinear(self.animTime, (0, 1), (0, 1))
            self.a = koan.anim.AnimLinear(self.animTime, (0, 0.6, 1), (0, 1, 1))
            self.a2 = koan.anim.AnimLinear(self.animTime, (0, 0.3, 1), (0, 0, 1))
                        
            t = render.GetTexture(r'C:\Users\chunming_su\Pictures\Welcome Scan.jpg')
            t2 = render.GetTexture(r'C:\Users\chunming_su\Pictures\Blue hills.jpg')
            e = render.GetEffect(r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Common\Media\fx\transition.fx')
            render.SetEffectTechnique(e, self.effect);
            render.SetTexture(t)
            render.DrawRect(*self.localRect)
            #render.SetTextureEx(1, t2)
            render.SetTexture(t2)
            
            render.SetEffectFloat(e, 'time', self.time)            
            #render.SetEffectFloat(e, 'blend', self.a)
            #render.SetEffectFloat(e, 'blend2', self.a2)
            render.PushEffect(e)
            render.DrawRect(*self.localRect)
            render.PopEffect()

        def testATINonPow2(self, render):
            tex = render.GetTexture(r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\content\bg_content.png')
            render.SetTexture(tex)
            render.DrawRect(0, 0, self.width, self.height)
            
        def onDraw(self, render):
            render.Clear(*self.bgColor)
            #self.testFlash(render)
            #self.testFloatingIssue(render)
            #self.testMultiTexture(render)
            self.testATINonPow2(render)

        def onKey(self, key):
            if key == 'F5':
                from random import randint
                self.bgColor = 255, randint(0,255), randint(0,255), randint(0, 255)
                self.dirty = True
            elif key == 'F12':
                self.toggleFullscreen()
            elif key == 'F1':
                import time
                a = 0.5
                self.showWait(True, 'start')
                time.sleep(a)
                self.showWait(True, 'hello')
                time.sleep(a*3)
                self.showWait(True, 'kanten')
                time.sleep(a)
                self.showWait(True, 'testing......hello')
                time.sleep(a)
                self.showWait(True, 'go.....')
                time.sleep(a)
                self.showWait(False)
            elif key == 'LEFT':
                effect = ['OpenFadeEffect', 'BlendEffect', 'NoiseEffect']
                self.effect = effect[(effect.index(self.effect)+1) % len(effect)]
                print self.off
            elif key == 'UP':
                self.off += 0.1
                print self.off
            elif key == 'DOWN':
                self.off -= 0.1
                print self.off
            return super(MyWindow, self).onKey(key)
                
    koan.init()
    
    w = MyWindow()
    w.bgColor = color.darkblue
    w.create(0, 0, 320, 240,
            render = 'dx9',                 # dx7, dx9, gdi
            caption = True,                 # use window caption bar
            border = True,                  # use window border
            blur = True,                    # use vista aero effect (must turn off captionbar)
            frame = True,                   # use vista aero frame
            defaultMaximize = True,         # window maximize or koan fullscreen when click window maximized button
            classname = 'Koan',             # window class name
            title = 'Koan Engine',          # window title
            vsync = True,                   # vertical sync with monitor frequence
            fullBuffer = True,              # create backbuffer with fullscreen size
            zBuffer = True                  # create z buffer for 3d models
    )
    w.show()
    
    koan.run(1)
    w = None
    koan.final()
    koan.traceLeak()


