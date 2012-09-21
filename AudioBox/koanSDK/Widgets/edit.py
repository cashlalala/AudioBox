import koan
import color
from time import time
from component import Component
from text import TextBase

NUMBER_FILTER       = (u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'-')
NUMBER_FILTER_EUR   = (u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'-')
FILENAME_FILTER     = (u'/', u':', u'*', u'?', u'"', u'<', u'>', u'|', u'\\')
RC_DIGITLETTER_MAP = [[u'0', u' '],
                      [u'1', u'/', u'.', u'+', u'_', u'@'],
                      [u'2', u'a', u'b', u'c'],
                      [u'3', u'd', u'e', u'f'],
                      [u'4', u'g', u'h', u'i'],
                      [u'5', u'j', u'k', u'l'],
                      [u'6', u'm', u'n', u'o'],
                      [u'7', u'p', u'q', u'r', u's'],
                      [u'8', u't', u'u', u'v'],
                      [u'9', u'w', u'x', u'y', u'z'],
                     ]


class Edit(Component, TextBase):
    """
    Event:
        Text Change
        Input Finish
        Invalid FileName Char
    
        @ivar _grawBound: bound for the text part
        @ivar decimal: the decimal point representation        
        @ivar cursorPos: the position of the cursor (in offset of char)
        @ivar cursorShow: variable to control the blink of cursor
        
        @ivar beginOffset: offset of the first visible char
        @ivar editrect: the visible editing region
        @ivar maxlen: maximal length of the edited text
        @ivar numbersOnly: if this edit can contains numbers only
        @ivar legalFileNameOnly: if this edit can contains legal filename only
        
        @ivar unit: ratio of the logical and phisical unit
    """

    def __init__(self, parent = None):
        Component.__init__(self, parent)
        TextBase.__init__(self)

        # cursor
        self.cursorColor = color.black
        self.cursorWidth = 1
        self.cursorPos = 0
        self.cursorShow = self.focus
        self.cursorShowAlways = False
        self.changeEvent('cursorPos', self.Regular)        
        
        # blink effect for cursor
        self.cursorAlpha = koan.anim.AnimLinear(1.0, (0, 0.45, 0.55, 1), (1, 1, 0, 0), loop = True)
        #koan.anim.IntervalExecute(0.5, self.onCursorShowChange)
        
        self.password = ''
        self.changeEvent('text', self.__onCheckCursorPos, sync = False)
        self.changeEvent('text', self.invoke, 'Value Change', self)

        self.margin = (2, 2, 2, 2)
        self.editrect = (0, 0, 0, 0)
        self._grawBound = (0, 0, 0, 0)
        self.spaceWidth = 10
               
        self.unit = 1, 1
        self.maxlen = 255
        self.beginOffset = 0

        self.autoDirty(['text', 'cursorPos', 'beginOffset', 'cursorShow'])
        
        self.bind('Size Change', self.onSize)
        self.bind('Mouse Down', koan.action.PureAction(self.setFocus))
        self.bind('Focus Change', self.onCursorShowChange)

        # file name input
        self.legalFileNameOnly = False
        
        # number        
        self.numbersOnly = False     
        self.autoadddecimal = True
        import locale
        self.decimal = locale.localeconv()['decimal_point']
        
        # 10 key input
        self.EnableDigitLetter = koan.config.getBool('Misc', 'EnableDigitLetter', True)  
        self.RCExpireTime = 1.5
        self.RCKeyTimer = 0
        self.RCKeyValue = -1
        self.RCKeyIndex = 0        
       
    def onCursorShowChange(self):
        self.cursorShow = self.isFocused() or self.cursorShowAlways

    def __onCheckCursorPos(self):
        if not self.text:
            self.cursorPos = 0
            self.beginOffset = 0

    def onKey(self, key):
        self.cursorShow = True
        if key == 'ENTER':
            self.invoke('Input Finish')
            return True

        elif key == 'LEFT':
            if self.cursorPos > 0:
                self.cursorPos -= 1
                return True
            else:
                return False
                
        elif key == 'RIGHT':
            if self.cursorPos < len(self.text):
                self.cursorPos += 1
                return True
            else:
                return False
                
        elif key == 'HOME':
            self.cursorPos = 0
            return True
            
        elif key == 'END':
            self.moveCursorPosToEnd()
            return True
            
        elif key == 'DEL':
            self.DeleteChar()
            return True
            
        elif key == 'BACK':
            if self.cursorPos > 0:
                self.cursorPos -= 1
                self.DeleteChar()
            return True
        
        elif key == 'CTRL V':
            '''
            from Common import SWCommunicator
            if SWCommunicator.objSWCommunicator:
                wstrClipboard = koan.ToUnicode(SWCommunicator.objSWCommunicator.GetClipboardUnicodeString())
                self.InsertString(wstrClipboard)
            '''
            return True
            
        # RC input number and character
        elif self.EnableDigitLetter and not self.numbersOnly and \
             key in [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']:
            if self.RCKeyValue <> key or (time() - self.RCKeyTimer > self.RCExpireTime):
                self.RCKeyValue = key
                self.RCKeyIndex = 0
            else:
                self.cursorPos -= 1
                self.DeleteChar()
            
            self.InsertChar(RC_DIGITLETTER_MAP[int(key)][(self.RCKeyIndex) % len(RC_DIGITLETTER_MAP[int(key)])], 1)
            self.RCKeyIndex += 1
            self.RCKeyTimer = time()
            return True
        
        elif len(key) == 1 and (key >= "\x20") and len(self.text) < self.maxlen:
            key = koan.ToUnicode(key)
            
            if self.legalFileNameOnly and key in FILENAME_FILTER:
                self.invoke('Invalid FileName Char')
                return True
            
            if self.numbersOnly and key in NUMBER_FILTER:
                if len(self.text)==1 and self.text[0] <> u'1':
                    if self.autoadddecimal:
                        key += self.decimal
                        self.InsertChar(key , 2)
                    else:
                        self.InsertChar(key , 1)
                    return True
                
                elif len(self.text)==2 and self.text[0] == u'1':
                    if self.autoadddecimal:
                        key += self.decimal
                        self.InsertChar(key, 2)
                    else:
                        self.InsertChar(key , 1)
                    return True
            
            self.InsertChar(key)
            return True
        else:
            keys = key.split(' ')
            if len(keys) > 2:
                if keys[0] == 'ALT' and keys[1] == 'CTRL':
                    self.InsertChar(koan.ToUnicode(keys[2]))
                    return True

        return super(Edit, self).onKey(key)

    # ------------------------------------------------------------------------------
    # public methods to manipulate edit state

    def moveCursorPosToEnd(self):
        self.cursorPos = len(self.text)

    def InsertChar(self, key , shiftCursor = 1):
        self.text = self.text[:self.cursorPos] + key + self.text[self.cursorPos:]
        self.invoke('Insert Char', key, self.cursorPos)
        self.cursorPos += shiftCursor

    def InsertString(self, string):
        nLength = len(string)
        if (len > 0):
            self.text = self.text[:self.cursorPos] + string + self.text[self.cursorPos:]
            self.cursorPos += nLength
        pass

    def DeleteChar(self):
        self.text = self.text[:self.cursorPos] + self.text[self.cursorPos + 1:]

    def ClearText(self):
        self.text = u''
        self.cursorPos = 0
        self.beginOffset = 0
    # ------------------------------------------------------------------------------

    def onSize(self):
        # Default edit rect
        gap = self.margin[0] + self.height / 2
        margin = (self.height - self.fontSize) / 2
        self.editrect = (gap, margin, self.width - gap, self.height - margin)

        r = self.editrect
        #self.fontSize = (r[3] - r[1]) * 4 / 5
        self.spaceWidth = self.fontSize / 3
        #self._grawBound = r# + (gap, margin, gap, margin)
        #self._grawBound = (gap, 0, self.width - gap, self.height)
        self._grawBound = self.editrect
        self.Regular()

    def getCharWidth(self, c):
        if self.password:
            c = self.password

        if c == ' ':
            return self.spaceWidth

        text, size = self.window.render.GetStringTexture(
            c,
            int(self.fontSize * self.unit[1]),
            color.white, #.focusColor,
            self.font
        )
        size = size[0]/self.unit[0], size[1]/self.unit[1]
        return size[0]

    def Regular(self):
        if self.text == u'':
            self.cursorPos = 0
            self.beginOffset = 0
            return
        
        if 'C' in self.align.upper():
            width = 0
            for i in range(0, len(self.text)):
                width += self.getCharWidth(self.text[i])-1
            if width < self.editrect[2] - self.editrect[0]:
                self.beginOffset = 0
        
        if self.cursorPos < self.beginOffset:
            self.beginOffset = self.cursorPos
            
        begin = self.editrect[0]
        for i in range(self.beginOffset, self.cursorPos):
            begin += self.getCharWidth(self.text[i])
            
        if begin <= self.editrect[2]:
            return
            
        while begin > self.editrect[2] and self.beginOffset < len(self.text):
            begin -= self.getCharWidth(self.text[self.beginOffset])
            self.beginOffset += 1
        
        
    def onDraw(self, render):
        # draw background
        super(Edit, self).onDraw(render)
        
        # Draw text
        fontColor = self.fontColor
        
        render.PushBound(*self._grawBound)

        unit = self.unit = self.window.currentPixelUnit
        
        tex, size = render.GetStringTexture(
            'ALFfgy',
            int(self.fontSize * unit[1]),
            fontColor,
            self.font
        )
        tex = None
        adp = size[2]
        size = size[0]/unit[0], size[1]/unit[1]
        allh = size[1]
        #top = self.editrect[1] + (self.editrect[3] - self.editrect[1] - size[1] * adp[1]) / 2
        
        start = self.editrect[0]
        
        if 'C' in self.align.upper():
            # get total width of text
            width = 0
            for i in range(0, len(self.text)):
                width += self.getCharWidth(self.text[i])-1
            
            if width < self.editrect[2] - self.editrect[0]:
                start = self.editrect[0] + (self.editrect[2] - self.editrect[0] - width) / 2
        
        begin = start
        
        top = self.editrect[1] + (self.editrect[3] - self.editrect[1] - size[1]) / 2
        
        if self.beginOffset <> 0:
            c = self.text[self.beginOffset - 1]
            if self.password:
                c = self.password
            
            if c <> u'':
                text, size = render.GetStringTexture(
                    c,
                    int(self.fontSize * unit[1]),
                    fontColor,
                    self.font
                )
                size = size[0]/unit[0], size[1]/unit[1]
                
                render.SetTexture(text)
                render.DrawRect(begin - size[0], top, begin, top + size[1])
        
        for i in range(self.beginOffset, len(self.text)):
            c = self.text[i]
            if self.password:
                c = self.password

            if c == ' ':
                begin += self.spaceWidth-1
                continue
                
            tex, size = render.GetStringTexture(
                c,
                int(self.fontSize * unit[1]),
                fontColor,
                self.font
            )
            size = size[0]/unit[0], size[1]/unit[1]

            render.SetTexture(tex)
            render.DrawRect(begin, top, begin + size[0], top + size[1])
            begin += size[0]-1

        # Draw Cursor
        if (self.isFocused() or self.cursorShowAlways) and self.cursorShow :
            begin = start
            
            for i in range(self.beginOffset, self.cursorPos):
                begin += self.getCharWidth(self.text[i])-1

            render.PushAlpha(self.cursorAlpha)
            render.SetTexture(None)
            render.SetColor(*self.cursorColor)
            render.DrawRect(begin, top, begin + self.cursorWidth, top + allh)
            render.SetColor(*color.white)
            render.PopAlpha()
            
        render.PopBound()


class RichEdit(Component, TextBase):
    '''
    events:
     - Paste
    '''
    def __init__(self, parent = None):        
        Component.__init__(self, parent)
        TextBase.__init__(self)
        self.vscroll = False
        self.hscroll = False
        self.maxlen = -1
        self.bgColor = color.white

        self.margin = (2, 2, 2, 2)
        self.bind('Mouse Down', koan.action.PureAction(self.setFocus))

        self.__edit = koan.platform.CreateEdit(callback = self.callback)
        self.changeEvent('text', self.__onTextChanged, sync = False)
        self.changeEvent('text', self.invoke, 'Value Change', self)
        self.changeEvent('align', self.__onEditStyleChange)
        self.changeEvent('vscroll', self.__onEditStyleChange)
        self.changeEvent('hscroll', self.__onEditStyleChange)
        self.changeEvent('maxlen', self.__onEditMaxlenChange, sync = False)
        
        # font
        self.changeEvent('font', self.__onFontChanged, sync = False)
        self.changeEvent('fontSize', self.__onFontChanged, sync = False)
        self.changeEvent('fontColor', self.__onFontColorChange, sync = False)
        self.changeEvent('bgColor', self.__onBgColorChange, sync = False)
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
        self.closeEdit()
        super(RichEdit, self).close()

    def closeEdit(self):
        if self.__edit:
            self.window._window.DetachChild( self.__edit.GetHWND() )
        self.__edit = None      # cut off the circular reference (by self.callback)

    def __onFontChanged(self):
        assert self.__edit
        self.__edit.SetFont(self.font, self.fontSize)

    def __onEditMaxlenChange(self):        
        self.__edit.SetLimit(self.maxlen)
        
    def __onEditStyleChange(self):
        #self.__edit.SetMultiLine('M' in self.align.upper())
        self.closeEdit()
        
        align = self.align.upper()
        if 'C' in align:        a = 'C'
        elif 'R' in align:      a = 'R'
        else:                   a = 'L'
        
        self.__edit = koan.platform.CreateEdit(
            callback = self.callback,
            text = koan.ToUnicode(self.text),
            multiline = 'M' in align, align = a,
            vscroll = self.vscroll, hscroll = self.hscroll
        )
        self.__onEditMaxlenChange()
        self.__onBgColorChange()
        self.__onFontColorChange()
        self.window._window.AttachChild( self.__edit.GetHWND(), 1000 )

    def callback(self, *argv, **argd):
        #print argv, argd
        if argv[0] == 'text' and self.text != argv[1]:
            self.text = argv[1]
        elif argv[0] == 'paste':
            return any( self.fire('Paste', argv[1]) )

    def __onTextChanged(self):
        if self.text != self.__edit.GetText():
            self.__edit.SetText(koan.ToUnicode(self.text))

    def __onBgColorChange(self):
        self.__edit.SetBgColor(*self.bgColor)

    def __onFontColorChange(self):
        self.__edit.SetFontColor(*self.fontColor)

    def __onEditVisibleChange(self, *argv):
        visible = self.isVisible() and self.focus
        if visible:
            self.__updateEditWndPos()
            koan.anim.PostEvent(self.__edit.Focus)
        else:
            self.window._window.Focus()
        if self.__edit:
            self.__edit.Show( visible )
        self.dirty = True

    def __updateEditWndPos(self):
        if self.__edit:
            l, t = self.local2global(self.margin[0], self.margin[1])
            r, b = self.local2global(self.width - self.margin[2], self.height - self.margin[3])
            self.window._window.SetChildPos(self.__edit.GetHWND(), int(l), int(t), int(r-l), int(b-t))

    def onDraw(self, render):
        super(RichEdit, self).onDraw(render)
        if not self.focus:
            TextBase.onDraw(self, render, pos = (self.margin[0], self.margin[1], self.width - self.margin[2], self.height - self.margin[3]))

    def ClearText(self):
        self.text = u''
        
    def InsertString(self, string):
        self.text = string

    def onKey(self, key):
        if 'ALT' in key or 'CTRL' in key or key in ['F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12']:
            return False
        if key == 'ENTER':
            if 'M' not in self.align.upper():
                self.invoke('Input Finish')
                return True
        return super(RichEdit, self).onKey(key)
        
            
Edit = RichEdit

if __name__ == '__main__':
    from window import Window
    from pprint import pprint

    koan.init()

    w = Window()
    w.create(0, 0, 640, 480, caption = True)
    w.bgColor = color.darkgray
    w.bind('Key', pprint)
    
    e = Edit(w)
    e.rect = 10,10,300,200
    e.align = 'MTL'
    e.vscroll = False
    e.font = 'Segoe UI'
    e.hscroll = False
    #e.bgColor = color.lightgray
    e.bgColor = color.darkblue
    e.fontColor = color.green
    #koan.anim.PostEvent(setattr, e, 'text', 'Testing, hello world')
    e.maxlen = 5    
    e.text = 'Hello world'
   
    def trace(self):
        print self.text
    e.bind('Value Change', trace)
    
    e = Edit(w)
    e.rect = 10,250,300,40
    e.font = 'Arial'
    e.bgColor = color.lightgray
    #e.legalFileNameOnly = True
    '''
    e = Edit(w)
    e.rect = 10,290,300,30
    e.bgColor = color.white
    e.numbersOnly = True     
    e.autoadddecimal = True
    
    # password
    e = Edit(w)
    e.rect = 10,330,300,30
    e.bgColor = color.white
    e.password = '*'
    '''
   
    w.show()
    e = None
    w = None
    
    koan.run(1)
    
    koan.final()
    
    koan.traceLeak()
    
