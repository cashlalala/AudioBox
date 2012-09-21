import os, koan
from time import time
from grid import Grid


class CharAccumulator:
    startTime = time()
    timeExpire = 0.3
    str = ""

def getAccStr(key):
    t = time()
    bNext = True
    if t < CharAccumulator.startTime + CharAccumulator.timeExpire:
        CharAccumulator.str += key
        bNext = False
    else:
        CharAccumulator.str = key
    CharAccumulator.startTime = t
    return CharAccumulator.str, bNext

class ListCtrl(Grid):
    def __init__(self, parent):
        Grid.__init__(self, parent)
        self.spinCtrl = None
        self.changeEvent('spinCtrl', self.__setSpinControl)
        self.bind("Cell Reset", self.onCellReset)
        self.bind("Cell Focus Change", self.onCellFocusChange)
        self.changeEvent('visible', self.__onVisibleChange)
        # [What] PCM061503-0115 [Music] UI: Music list region is too short when music file playback (16:9 screen ratio)
        # [Why] The timing of resetCells is not current.
        # [How] The Size change should be the fornt of cell reset.
        self.unbind("Size Change", self.resetCells)
        self.bind("Size Change", self.__onSizeChange)
        self.bind('Size Change', self.resetCells)
        self.bind("Cell Reset", self.__onSizeChange)

        self.singleCol = False
        self.singleRow = False
        self.autoEnabled = True
        self.quickFindMode = 'Text'        # 'Index'

    def __onSizeChange(self):
        if self.singleCol:
            self.cellSize = self.width, self.cellSize[1]
        if self.singleRow:
            pass
        else:
            itemCount = self.getCellCount()
            self.colCount = (self.width + self.cellRegion[0]) / (self.cellSize[0] + self.cellRegion[0])
            if self.colCount == 0:
                self.colCount = 1
            self.rowCount = (itemCount + self.colCount - 1) / self.colCount
            self.lastRowCount = itemCount - (self.rowCount - 1) * self.colCount
        
    def setListCount(self, n):
        if self.singleRow:
            self.colCount = n
            self.lastRowCount = n
        else:
            self.colCount = (self.width + self.cellRegion[0]) / (self.cellSize[0] + self.cellRegion[0])
            if self.colCount == 0:
                self.colCount = 1
            self.rowCount = (n + self.colCount - 1) / self.colCount
            self.lastRowCount = n - (self.rowCount - 1) * self.colCount

    def shouldSpinVisible(self):
        return (self.getCellCount() > 0 and self.visible)

    def __onVisibleChange(self):
        #print self.parent.getChildName(self), 'visible', self.visible
        if self.spinCtrl:
            self.spinCtrl.visible = self.shouldSpinVisible()

    def onCellFocusChange(self):
        if self.getCellCount() == 0:
            if self.spinCtrl:
                self.spinCtrl.visible = False
            return

        if self.spinCtrl:
            self.spinCtrl.visible = self.shouldSpinVisible()
            self.spinCtrl.min = 1
            self.spinCtrl.max = self.getCellCount()
            self.spinCtrl.index = self.getCurrentSelect() + 1
            self.spinCtrl.addition = self.colCount * self.getVisibleRange()[1]

        if self.sa:
            if self.isFocused():
                self.sa.onStartScroll()
            else:
                self.sa.onStopScroll()

    def getCurrentSelect(self):
        if self.getCellCount() == 0:
            return -1

        if self.posY >=  self.rowCount:
            self.posY = self.rowCount - 1

        if self.posY < 0:
            self.posY = 0

        if self.posX >=  self.colCount:
            self.posX = self.colCount - 1

        if self.posX < 0:
            self.posX = 0

        idx = self.posY * self.colCount + self.posX
        return idx

    def __setSpinControl(self):
        if self.spinCtrl:
            #self.spinCtrl.bind("Value Change", self.onSpinChange)
            self.spinCtrl.bind("Click Down", self.onSpinClick, 'Down')
            self.spinCtrl.bind("Click Up", self.onSpinClick, 'Up')
            self.spinCtrl.visible = self.shouldSpinVisible()

    #-------------------------------------------------------------------
    def onSpinClick(self, dir):
        if dir == 'Down':
            self.onKey('PAGEDOWN')
        elif dir == 'Up':
            self.onKey('PAGEUP')

    def onSpinChange(self):
        if self.spinCtrl and self.getCellCount() > 0:
            x = (self.spinCtrl.index - 1) % self.colCount
            y = (self.spinCtrl.index - 1) / self.colCount
            self.focusCell(x, y)

    #-------------------------------------------------------------------
    def onCellReset(self):
        if not self.spinCtrl:
            return
        if self.getCellCount() == 0:
            if self.autoEnabled:
                self.enabled = False
            self.spinCtrl.visible = False
        else:
            if self.autoEnabled:
                self.enabled = True
            self.spinCtrl.visible = self.shouldSpinVisible()
            self.spinCtrl.min = 1
            self.spinCtrl.max = self.getCellCount()
            self.spinCtrl.index = self.getCurrentSelect() + 1
            self.spinCtrl.addition = self.colCount * self.getVisibleRange()[1]

    def onKey(self, key):
        if len(key) == 1 and hasattr(self, "getText"):
            if self.quickFindMode == 'Text':
                name, bNext = getAccStr(key)
                u, v = self.getCellPosByName(name, bNext)
                if u <> -1 and v <> -1:
                    return self.focusCell(u, v)
            elif self.quickFindMode == 'Index':
                try:
                    vKey = int(key)
                    name, bNext = getAccStr(key)
                    u, v = self.getCellPosByIndex(int(name)-1)
                    if u <> -1 and v <> -1:
                        return self.focusCell(u, v)
                except:
                    CharAccumulator.str = ''
        return Grid.onKey(self, key)


    def getCellPosByIndex(self, idx):
        #print name
        if idx < 0 or idx >= self.getCellCount():
            return -1, -1
        v = idx / self.colCount
        u = idx - v * self.colCount
        return u, v

    def getCellPosByName(self, name, bNext):
        #print name
        idx = self.getCellIndex(name, bNext)
        if idx == -1:
            return -1, -1
        v = idx / self.colCount
        u = idx - v * self.colCount
        return u, v

    def getCellIndex(self, name, nNext):
        return -1
        

