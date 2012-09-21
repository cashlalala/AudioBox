# -*- coding: cp950 -*-
import koan
import color
from koan.container import List
from koan.action import PureAction
from component import Component
from text import TextBase, Text
from image import ImageBase
from tooltips import TipBase

class PressBase:
    def __init__(self):
        self.pressed = False
        self.bind('Mouse Down', PureAction(setattr, self, 'pressed', True))
        self.bind('Dbl Click', PureAction(setattr, self, 'pressed', True))
        self.bind('Mouse Up', PureAction(setattr, self, 'pressed', False))

#----------------------------------------------------------------
# Button
#----------------------------------------------------------------
class Button(Component, PressBase, TipBase):
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        PressBase.__init__(self)
        TipBase.__init__(self)
        self.command = ''
        self.bind('Click', self.onClick, postevent = False)

    def onClick(self):
        if self.command:            
            self.invokeCmd(self.command)
    
    def onKey(self, key):
        if key == 'SPACE' or key == ' ' or key == 'ENTER':
            self.onClick()
            return True
        return super(Button, self).onKey(key)

#----------------------------------------------------------------
# TextButton
#----------------------------------------------------------------
class TextButton(Button, TextBase):
    def __init__(self, parent = None):
        Button.__init__(self, parent)
        TextBase.__init__(self)
        #self.bindData('text', self, 'info', dir = '->')

    def onDraw(self, render):
        super(TextButton, self).onDraw(render)
        TextBase.onDraw(self, render)

#----------------------------------------------------------------
# ImageButton
#----------------------------------------------------------------
class ImageButton(Button, ImageBase):
    def __init__(self, parent = None):
        Button.__init__(self, parent)
        ImageBase.__init__(self)

    def onDraw(self, render):
        super(ImageButton, self).onDraw(render)
        ImageBase.onDraw(self, render)

#----------------------------------------------------------------
# CheckBase
#----------------------------------------------------------------
class CheckBase:
    def __init__(self, **argd):
        self.checked = False
                
        assert isinstance(self, Component)
        if argd.get('check', True):
            self.bind('Click', self.__onClick, postevent = False)
        else:
            self.bind('Click', setattr, self, 'checked', True,  postevent = False)
        #self.autoDirty( ['checked'] )

    def __onClick(self):
        self.checked = not self.checked
        
#----------------------------------------------------------------
# CheckTextButton
#----------------------------------------------------------------
class CheckTextButton(Component, TextBase, CheckBase, TipBase):
    def __init__(self, parent):
        Component.__init__(self, parent)
        TextBase.__init__(self)
        CheckBase.__init__(self)
        TipBase.__init__(self)
        self.command = ''
        self.changeEvent('checked', self.__onCheckChanged, postevent = False)

    def __onCheckChanged(self):
        if self.command:
            self.invokeCmd(self.command, self.checked)

    def onDraw(self, render):
        super(CheckTextButton, self).onDraw(render)
        TextBase.onDraw(self, render)


#----------------------------------------------------------------
# CheckImageButton
#----------------------------------------------------------------
class CheckImageButton(ImageButton, CheckBase):
    def __init__(self, parent):
        ImageButton.__init__(self, parent)
        CheckBase.__init__(self)
        self.changeEvent('checked', self.__onCheckChanged, postevent = False)

    def __onCheckChanged(self):
        if self.command:
            self.invokeCmd(self.command, self.checked)
        
#----------------------------------------------------------------
# Checkbox
#----------------------------------------------------------------
class Checkbox(Component, TextBase, CheckBase, TipBase):
    def __init__(self, parent = None, **argd):
        Component.__init__(self, parent)
        TextBase.__init__(self)
        CheckBase.__init__(self, **argd)
        TipBase.__init__(self)
        
        # property
        self.checkImg = ''
        self.autosize = False
        self.margin = 5
        self.onAutoSize()     # self.checkPos

        self.changeEvent('text', self.onAutoSize)
        self.changeEvent('margin', self.onAutoSize)
        self.bind('Size Change', self.onAutoSize)
        self.autoDirty( ['checkImg', 'margin'] )     

    def __getTexPosition(self):
        return self.height, 0, self.width, self.height
    textPos = property(__getTexPosition)
    
    def onAutoSize(self):
        if self.autosize:
            w, h = self.textSize
            self.size = w + h, h
        m = self.margin
        self.checkPos = m, m, self.height - m, self.height - m

    def hitTest(self, x, y):
        #if x < self.checkPos[0] or self.checkPos[2] < x or y < self.checkPos[1] or self.checkPos[3] < y:
        #    return False
        if not super(Checkbox, self).hitTest(x, y) or x > self.height + self.textSize[0]:
            return False
        return True

    def onDraw(self, render):
        super(Checkbox, self).onDraw(render)
        
        # draw check icon
        t = render.GetTexture(self.checkImg)
        render.SetTexture(t)
        render.DrawRect(*self.checkPos)
        
        # draw text
        pos = self.height, 0, self.width, self.height
        TextBase.onDraw(self, render)

    def onKey(self, key):
        if key == ' ':
            self.checked = not self.checked
            return True
        return super(Checkbox, self).onKey(key)
#----------------------------------------------------------------
# RadioButton
#----------------------------------------------------------------
class RadioBase:
    """ 
    Mixin for components with radio-button like behavior.
    """
    def __init__(self):
        self.changeEvent('checked', self.__onCheckedChanged, postevent = False)
        self.autoRemove( self.parent.bind('Select Changed', self.__onSyncGroup) )
    
    def __onCheckedChanged(self):
        if self.checked:
            self.parent.invoke('Radio Changed', self)
    
    def __onSyncGroup(self, o):
        if self is not o:
            self.checked = False

class RadioButton(Checkbox, RadioBase):
    def __init__(self, parent = None):
        Checkbox.__init__(self, parent, check = False)
        RadioBase.__init__(self)        

    def onKey(self, key):
        if key == ' ':
            if not self.checked:
                self.checked = True
            return True
        return super(RadioButton, self).onKey(key)
#----------------------------------------------------------------
# Group
#----------------------------------------------------------------
class GroupBase(object):
    def __init__(self):
        self.tabStop = False
        self.bind('Radio Changed', self.__onSomeoneChanged, postevent = False)
    def __onSomeoneChanged(self, obj):
        self.invoke('Select Changed', obj)

class Group(Component, GroupBase):
    '''
    event:
        Select Changed
    '''
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        GroupBase.__init__(self)

#----------------------------------------------------------------
# Combobox
#----------------------------------------------------------------
class Combobox(Text, PressBase):
    '''
    events:
       - Select Changed (index)
       - Data Changed
       
    ex:
    combobox = Combobox(self)
    combobox.removeItems()
    combobox.addItems(['Hello', 'World'])
    combobox.addItem('New item 1')
    combobox.removeItem('Wrold')
    '''
    def __init__(self, parent = None):
        Text.__init__(self, parent)
        PressBase.__init__(self)
        self.tabStop = 1000
        self.blind = False        
        self.margin = 0, 0, 0, 0
        
        self.index = -1
        self.__data = List()
        self.autoRemove( self.data.bind('Change', self.invoke, 'Data Changed', postevent = False) )
        
        self.menuStyle = None
        self.itemStyle = None
        
        self.changeEvent('index', self.__onChangeSelect, postevent = False, sync = True)
        self.changeEvent('text', self.__onTextChanged, postevent = False, sync = True)
        self.bind('Data Changed', self.__onDataChanged, postevent = False)
        self.bind('Click', self.__onCombolist)

    #---------------------------------------------
    # property
    #---------------------------------------------
    def getTextPosition(self):
        return self.margin[0], self.margin[1], self.width - self.margin[2], self.height - self.margin[3]
    textPos = property(getTextPosition)

    def getData(self):
        return self.__data
    data = property(getData)
    
    def getSelectedData(self):
        if 0 <= self.index and self.index < len(self.data):
            return self.data[self.index]
        else:
            return None
    selectedData = property(getSelectedData)
    #---------------------------------------------
    # override function
    #---------------------------------------------    
    def close(self):
        self.__data.close()
        self.__data = None
        super(Combobox, self).close()

    #---------------------------------------------
    # operation
    #---------------------------------------------
    def addItem(self, i):
        self.data.append(i)
    
    def addItems(self, i):
        self.data.extend(i)
                
    def removeItems(self):
        del self.data[:]
            
    def removeItem(self, i):
        if i in self.data:
            self.data.remove(i)
            
    #---------------------------------------------
    # KXML syntax
    #---------------------------------------------
    def setContent(self, data, **keyword):
        parser = keyword.get('parser', None)
        d = eval(data, keyword)
        t = type(d)
        if t is tuple or t is list:
            for s in d:
                if len(s) > 3 and s[:2] == '_(' and s[-1] == ')' and parser:
                    s = parser.trans(s[2:-1])
                self.data.append(s)
        else:
            if len(d) > 3 and d[:2] == '_(' and d[-1] == ')' and parser:
                d = parser.trans(d[2:-1])
            self.data.append(d)

    def setAttribute(self, name, strValue, **keyword):
        n = name.lower()
        if n == 'menustyle' or n == 'itemstyle':
            cls = strValue.strip()
            styles = keyword['parser'].stkAutoStyle[-1][2]['name']
            if cls in styles:
                styleCmd = styles[cls]
                styleCmd.macro = keyword['parser'].macro
                setattr(self, name, styleCmd)
        elif n == 'data' or n == 'list':
            self.setContent(strValue.strip(), **keyword)
        else:
            super(Combobox, self).setAttribute(name, strValue, **keyword)    
    
    #---------------------------------------------
    # private function
    #---------------------------------------------     
    def __onDataChanged(self):
        if self.data:
            if not self.selectedData:
                #self.index = 0
                object.__setattr__(self, 'index', 0)
        else:
            #self.index = -1
            object.__setattr__(self, 'index', -1)            
        self.__onChangeSelect()
        
    def __onChangeSelect(self):
        self.text = koan.ToUnicode(self.selectedData) if self.selectedData else ''
        if self.selectedData:
            self.invoke('Select Changed', self.index)

    def __onTextChanged(self):
        try:
            id = self.data.index(self.text)
            object.__setattr__(self, 'index', id)
        except:
            object.__setattr__(self, 'index', -1)
            
    def __onCombolist(self):
        if len(self.data):            
            from menu import PopupMenu, MenuItem
            m = PopupMenu(self.window)
            m.applyStyle(self.menuStyle)
            w = self.width
            for o in self.data:
                itm = MenuItem(m)
                itm.applyStyle(self.itemStyle)
                itm.align = self.align
                itm.iconWidth = 0
                itm.header = koan.ToUnicode(o)
                try:
                    itm.enabled = o.enabled
                except:
                    pass
                itm.command = str(self.data.index(o))
                itm.width = w
                if o == self.data[self.index]:
                    itm.setFocus()
            m.xy = self.local2global(0, self.height)
            m.width = w
            ret = m.doModal()
            self.setFocus()            
            if type(ret) is str or type(ret) is unicode:
                try:
                    self.index = int(ret)
                except:
                    pass

    #-------------------------------------------------
    # keyboard
    #-------------------------------------------------
    def onKey(self, key):
        if key == ' ':
            self.__onCombolist()
            return True
        elif key == 'UP':
            self.index = max( self.index - 1, 0 )
            return True
        elif key == 'DOWN':
            self.index = min( self.index + 1, len(self.data) - 1 )
            
        
        return super(Combobox, self).onKey(key)
    #-------------------------------------------------
    # display
    #-------------------------------------------------
    def onDraw(self, render):
        super(Combobox, self).onDraw(render)
        TextBase.onDraw(self, render)


if __name__ == '__main__':
    from window import Window
    from panel import StackPanel
    
    koan.init()
    
    w = Window()
    w.create(0, 0, 400, 600, True)
    w.bgColor = color.darkgray
    
    p = StackPanel(w)
    p.bindData('width', w, 'width', dir = '<-')
    p.bindData('height', w, 'height', dir = '<-')
    
    # button
    b = Button(p)
    b.tips = 'Button'
    b.bgColor = color.darkblue
    b.height = 30

    # text button
    tb = TextButton(p)
    tb.bgColor = color.darkred
    tb.fontColor = color.white
    tb.height = 30
    tb.text = 'TextButton'
    tb.tips = 'Tooltips'
        
    # image button
    ib = ImageButton(p)
    ib.height = 30
    ib.background = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Common\Media\button\btn_h.png|(3,3,3,3)'
    ib.image = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Media\icon_ap.png'
    ib.stretch = 'Uniform'
    
    # checkbox
    cb = Checkbox(p)
    cb.height = 30
    cb.bgColor = color.green
    cb.text = 'This is Checkbox'
    cb.checkImg = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Common\Media\checkbox\checkbox_c_h.png'
        
    # combobox
    c = Combobox(p)
    c.height = 30
    c.addItems(['Gmail', 'Outlook', 'Hello', 'World', 'Test'])
    c.removeItems()
    c.addItems(['Hello', 'World'])
    c.addItem('New item 1')
    c.removeItem('Wrold')    
    c.bgColor = color.lightgray
    c.fontColor = color.white
    
    # radio button
    g = Group(p)
    g.height = 60
    g.bgColor = color.translucent
    r1 = RadioButton(g)
    r1.text = 'RadioButton 1'
    r1.size = 300, 30
    r1.checkImg = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Common\Media\checkbox\checkbox_c_h.png'
    r2 = RadioButton(g)
    r2.text = 'RadioButton 2'
    r2.checkImg = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Common\Media\checkbox\checkbox_c_h.png'
    r2.rect = 0, 30, 300, 30
    
    w.show()
    
    koan.run(1)
    
    koan.final()