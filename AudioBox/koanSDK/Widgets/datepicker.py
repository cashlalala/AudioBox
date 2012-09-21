import koan
from component import Component
from text import TextBase
import time
import subsys

class DatePicker(Component, TextBase):
    def __init__(self, parent = None, longFormat = False):        
        Component.__init__(self, parent)
        TextBase.__init__(self)

        self.iPlatform = subsys.GetLatestInterface('IPlatform')
        self.date = 2007, 1, 1
        self.margin = (2, 2, 2, 2)
        self.longFormat = longFormat
        self.bind('Mouse Down', koan.action.PureAction(self.setFocus))

        self.__datePicker = koan.platform.CreateDatePicker(callback = self.callback, longFormat = self.longFormat)
        self.window._window.AttachChild2( self.__datePicker.GetHWND() )

        #self.__datePicker.Show( False )
        self.changeEvent('text', self.invoke, 'Value Change', self)
        self.changeEvent('date', self.__onDateChange)
        self.changeEvent('font', self.__onFontChanged, sync = False)
        self.changeEvent('fontSize', self.__onFontChanged, sync = False)
        #koan.anim.Execute(0.3, self.__datePicker.Show, True)
        
        # font
        self.bind('Visible Change', self.__onEditVisibleChange)        
        self.bind('Size Change', self.__updateEditWndPos)
        self.bind('Position Change', self.__updateEditWndPos)
        self.bind('Parent Position Change', self.__updateEditWndPos)
        self.bind('Focus Change', self.__onEditVisibleChange)
        
        child = self
        while parent != None:
            child.autoRemove(parent.bind('Parent Position Change', child.invoke, 'Parent Position Change', postevent = False))
            child = parent
            parent = child.parent

    def close(self):
        self.syncDate()
        self.closeDatePicker()
        super(DatePicker, self).close()

    def closeDatePicker(self):
        if self.__datePicker:
            self.window._window.DetachChild( self.__datePicker.GetHWND() )
        self.__datePicker = None      # cut off the circular reference (by self.callback)

    def callback(self, *argv, **argd):
        pass

    def __onFontChanged(self):
        if self.__datePicker:
            #self.__datePicker.SetFont(self.font, self.fontSize)
            pass

    def __onDateChange(self):
        y, m, d = self.date
        stime = time.strptime('%d/%d/%d'%(y,m,d), '%Y/%m/%d')
        if self.longFormat:
            self.text = self.iPlatform.strftime('%#x', stime)
        else:
            self.text = self.iPlatform.strftime('%x', stime)
        if self.__datePicker:
            self.__datePicker.SetDate(*self.date)

    def __onEditVisibleChange(self, *argv):
        visible = self.isVisible() and self.focus
        if visible:
            self.__updateEditWndPos()
            koan.anim.PostEvent(self.__datePicker.Focus)
        else:
            self.window._window.Focus()
        if self.__datePicker:
            self.__datePicker.Show( visible )
            if not visible:
                self.date = self.__datePicker.GetDate()
        self.dirty = True

    def __updateEditWndPos(self):
        #margin = 0, 0, 0, 0
        margin = 2, 2, 2, 2
        l, t = self.local2global(margin[0], margin[1])
        r, b = self.local2global(self.width - margin[2], self.height - margin[3])
        self.window._window.SetChildPos(self.__datePicker.GetHWND(), int(l), int(t), int(r-l), int(b-t))

    def onDraw(self, render):
        super(DatePicker, self).onDraw(render)
        if not self.focus:
            TextBase.onDraw(self, render, pos = (self.margin[0], self.margin[1], self.width - self.margin[2], self.height - self.margin[3]))

    def hideControl(self):
        if self.__datePicker:
            self.__datePicker.Show( False )

    def syncDate(self):
        self.date = self.__datePicker.GetDate()

    def onKey(self, key):
        if key == 'ENTER':
            self.invoke('Input Finish')
            return True
        return True
