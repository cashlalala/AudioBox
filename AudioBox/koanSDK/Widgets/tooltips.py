import koan
from text import Text, TextBase
from component import Component
import color


class TipBase:
    def __init__(self):
        assert isinstance(self, Component)
        self.tips = ''
        self.bind('Enable Change', self.hideTips)
        self.bind('Mouse Move', self.postShowTips)
        self.bind('Mouse Leave', self.hideTips)
        self.bind('Mouse Down', self.hideTips)
        self.bind('Mouse RDown', self.hideTips)
        self.bind('Visible Change', koan.action.PureAction(self.hideTips))

    def postShowTips(self, x, y, flag):
        if self.tips and not self.dead and self.window:        
            koan.anim.Cancel(self.showTips)
            koan.anim.Execute(0.5, self.showTips, x, y)

    def showTips(self, x, y):
        if self.tips and not self.dead and self.window:
            tips = self.tips
            
            if hasattr(self, 'command') and self.command:
                command = '<'+self.command+'>'
    
                # got accelerator
                parent = self.parent
                objs = []
                keymaps = {}
                while parent:
                    if hasattr(parent, 'keymaps') and parent.keymaps:
                        objs.append(parent)
                        #keymaps.update(parent.keymaps)
                    parent = parent.parent
    
                if objs:
                    for obj in objs[::-1]:
                        keymaps.update(obj.keymaps)
    
                subTips = ''
                for key, cmd in keymaps.items():
                    if command in cmd:
                        if key == ' ':
                            key = 'SPACE'
                        if subTips:     subTips += ', %s' %key
                        else:           subTips += '%s' %key
                
                if subTips:
                    tips = tips + '  (%s)' %(subTips)
            
            self.window.showToolTips(tips, self.local2global(x, y))

    def hideTips(self, *argv):        
        if self.tips and not self.dead and self.window:
            koan.anim.Cancel(self.showTips)
            self.window.hideToolTips()




class Tooltips(Text):
    def __init__(self, parent = None):
        Text.__init__(self, parent)
        self.autosize = True
        self.bgColor = color.paper
        self.fontColor = color.black
        self.border = 30, 15
        self.align = 'C'
        self.visible = False
        
    def onAutoSize(self):
        if self.autosize:
            self.size = self.textSize[0] + self.border[0], self.textSize[1] + self.border[1]
            
    def onDraw(self, render):
        # draw background
        super(Text, self).onDraw(render)
        
        # draw border
        if not self.background:
            self.drawBorder(render, 1, color.black)
        
        # draw text
        TextBase.onDraw(self, render)