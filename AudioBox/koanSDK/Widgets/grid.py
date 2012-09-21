import time, math, koan, color

from component import Component
from scrollanim import ScrollAnim
from animctl import AnimCtl


#########################################################
#
#   Object Declare
#
#########################################################

class GridBase(Component):
    """
    overwritable:
      - getSelectAction
      - onDrawCell
      - getBackgroundIndex
      - getBackgroundCount
      - changeContent
      - changeContentByBack
      - canBack
      - createAnimCtl
      - onMouseLeave

    binded events:
      - Mouse Move
      - Mouse Leave
      - Mouse Wheel
      - Size Change
      - Click
      - Enter
      - Enable Change
      - Active Change
      - Focus Change

    change events:
      - colCount
      - rowCount
      - cellSize
      - lastRowCount
      - cellRegion
      - posX
      - posY

    @ivar __topX: (negative) position of the visible left top grid item (unit: item)
    @ivar __topY: (negative) position of the visible left top grid item (unit: item)
    @ivar __capW: number of visible items in a row
    @ivar __capH: number of visible items in a column
    @ivar _targetX: position of the focused grid item (unit: pixel)
    @ivar _targetY: position of the focused grid item (unit: pixel)
    @ivar posX: position of the focused grid item (unit: item)
    @ivar posY: position of the focused grid item (unit: item)
    @ivar colCount: count of columns
    @ivar rowCount: count of rows
    @ivar cellSize: size of each cell (unit: pixel)
    @ivar cellRegion: the margin between each cell (unit: pixel)
    @ivar animCtl: list of animation control

    @type posX: int
    @type posY: int
    @type colCount: int
    @type rowCount: int
    @type cellSize: int, int
    @type cellRegion: int, int

    @group overridable: onDrawCell getBackgroundIndex getBackgroundCount
                        changeContent changeContentByBack canBack createAnimCtl
    """
    def __init__(self, parent):
        Component.__init__(self, parent)

        self.__topX = 0
        self.__topY = 0
        self.__capW = 1
        self.__capH = 1
        self._targetX = koan.anim.AnimTarget('spring', 0, 0, 0, self)
        self._targetY = koan.anim.AnimTarget('spring', 0, 0, 0, self)
        self.posX = 0
        self.posY = 0

        self.colCount = 10
        self.rowCount = 1
        self.lastRowCount = self.colCount
        self.cellSize = (100, 40)
        self.cellRegion = (10, 8)
        self.bound = (0, 0, 0, 0, 0, 0, 0, 0)
        self.localbound = (0, 0, 0, 0, 0, 0, 0, 0)
        self.resetCells()

        self.bind('Mouse Enter', self.setFocus)

        self.bind('Mouse Move', self.onMouseMove)
        self.bind('Mouse Leave', self.onMouseLeave)
        self.bind('Mouse Wheel', self.onMouseWheel)
        self.bind('Size Change', self.resetCells)
        self.bind('Click', self.onClick)
        self.bind('Enter', self.onEnterKey)

        self.changeEvent('colCount', self.resetCells2)
        self.changeEvent('rowCount', self.resetCells2)
        self.changeEvent('posX', self.invoke, "Cell Focus Change")
        self.changeEvent('posY', self.invoke, "Cell Focus Change")
        self.changeEvent('rowCount', self.onRowCountChanged, postevent = False)

        self.bind('Enable Change', self.onStateChange)
        self.bind('Active Change', self.onStateChange)
        self.bind('Focus Change', self.onStateChange)

        self.backgroundCount = self.getBackgroundCount()
        self.animCtl = []
        self.resetAnimCtl()
        self.sa = ScrollAnim(self)

        self._changeEffectAlpha = 1
        self._changeEffectScale = 1
        self.autoDirty(['_targetX', '_targetY', 'posX', 'posY', '_changeEffectAlpha', '_changeEffectScale'])
        self.__maxAnimRange = 2000

    def get_topY(self):
        return self.__topY
    _topY = property(get_topY)
    
    def get_topX(self):
        return self.__topX
    _topX = property(get_topX)

    def get_capW(self):
        return self.__capW
    _capW = property(get_capW)
    
    def get_capH(self):
        return self.__capH
    _capH = property(get_capH)
    
    def getTop(self):
        return self.__topX, self.__topY
        
    def setTop(self, newtopX, newtopY):
        self.__topX = newtopX
        self.__topY = newtopY
        self._targetX.Assign(-self.__topX*self.cellWidth())
        self._targetY.Assign(-self.__topY*self.cellHeight())       

    def onRowCountChanged(self):
        pass

    def free(self):
        # overrode Component.free
        super(GridBase, self).free()
        self.sa.free()
        self.sa = None
        for i in self.animCtl:
            i.close()

    def hitTest(self, x, y):
        # overrode Component.hitTest
        if not super(GridBase, self).hitTest(x, y):
            return False
        return self.pt2cell(x, y) <> (-1, -1)

    def resetAnimCtl(self):
        """
        reset all the animation control
        """
        for i in self.animCtl:
            i.close()
        self.animCtl = []
        for i in range(self.backgroundCount):
            self.setAnimCtl(i, self.createAnimCtl(i), self.createAnimCtl(i))

    def getSelectAction(self, x, y):
        """
        getCellClickAction(x, y) -> return what kind of action to take when mouse clicked

        return 0 : select this item
        return 1 : enter sub folder
        return 2 : leave current folder

        if return 1 and 2: changeContent(x, y) will be call later
        """
        return 0

    def getSelectActionEnter(self, x, y):
        """
        return what kind of action to take when mouse clicked

        return 0 : select this item
        return 1 : enter sub folder
        return 2 : leave current folder

        if return 1 and 2: changeContent(x, y) will be call later
        """
        return 0

    def getCellCount(self):
        """
        get the total amount of cells
        """
        return self.colCount * self.rowCount - (self.colCount - self.lastRowCount)

    def getBackgroundCount(self):
        return 0

    def getBackgroundIndex(self, x, y):
        return -1

    def changeContent(self, x, y):
        """
        change content by select cell x, y
        """
        pass

    def changeContentByBack(self):
        """
        change content by key back
        """
        pass

    def canBack(self):
        """
        return if back is useable now
        """
        return False

    def createAnimCtl(self, idx):
        """
        get new animation control
        override this to provide new anim function
        """
        return AnimCtl() # this AnimCtl do nothing

    def setAnimCtl(self, idx, focus, noFocus):
        for a in (focus, noFocus):
            a.pressed = False
            a.enabled = self.enabled
            a.actived = self.isActive
            a.mouseOver = self.isMouseOver
            a.focused = False

        if len(self.animCtl) == idx*2:
            self.animCtl.append(focus)
            self.animCtl.append(noFocus)
        else:
            if self.animCtl[idx*2]:
                self.animCtl[idx*2].close()
                self.animCtl[idx*2] = None
            if self.animCtl[idx*2 + 1]:
                self.animCtl[idx*2 + 1].close()
                self.animCtl[idx*2 + 1] = None

            self.animCtl[idx*2] = focus
            self.animCtl[idx*2 + 1] = noFocus

    def onStateChange(self):
        v = self.isFocused()
        for i in range(self.backgroundCount):
            if i >= len(self.animCtl):
                break
            self.animCtl[i * 2].enabled = self.enabled
            self.animCtl[i * 2].actived = self.isActive
            self.animCtl[i * 2].focused = v

            self.animCtl[i * 2 + 1].enabled = self.enabled
            self.animCtl[i * 2 + 1].actived = self.isActive
            self.animCtl[i * 2 + 1].focused = False # always False

        if self.sa:
            if self.isFocused():
                self.sa.onStartScroll()
                
                if self.posX < self.__topX or self.posX >= (self.__topX + self.__capW):
                    self.posX = self.__topX

                if self.posY < self.__topY or self.posY >= (self.__topY + self.__capH):
                    self.posY = self.__topY
            else:
                self.sa.onStopScroll()

    def __afterContentEffect(self, act):
        self.blind = False
        self._targetX.Assign(0)
        self._targetY.Assign(0)
        if koan.useAnimation:
            if act == 1:
                self._changeEffectScale = koan.anim.AnimLinear(0.25, (0, 1), (0, 1))
                self._changeEffectAlpha = koan.anim.AnimLinear(0.25, (0, 1), (0, 1))
            elif act == 2:
                self._changeEffectScale = koan.anim.AnimLinear(0.25, (0, 1), (2, 1))
                self._changeEffectAlpha = koan.anim.AnimLinear(0.25, (0, 1), (0, 1))
        #-------------------------------------------
        # End TouchStone busy state
        koan.core.isBusy = False
        #-------------------------------------------

    def __beforeContentEffect(self, act):
        self.blind = True
        if koan.useAnimation:
            if act == 1:
                self._changeEffectScale = koan.anim.AnimLinear(0.25, (0, 1), (1, 2))
                self._changeEffectAlpha = koan.anim.AnimLinear(0.25, (0, 1), (1, 0))
            elif act == 2:
                self._changeEffectScale = koan.anim.AnimLinear(0.25, (0, 1), (1, 0))
                self._changeEffectAlpha = koan.anim.AnimLinear(0.25, (0, 1), (1, 0))

    def onClick(self):
        for i in range(self.backgroundCount):
            self.animCtl[i*2].pressed = True

        cur = self.posX, self.posY
        ret = self.getSelectAction(*cur)
        if ret > 0:
            self.blind = True
            #-------------------------------------------
            # Set TouchStone busy
            koan.core.isBusy = True
            #-------------------------------------------
            self.__beforeContentEffect(ret)
            if koan.useAnimation:
                koan.anim.Execute(0.25, self.changeContent, *cur)
                koan.anim.Execute(0.25, self.__afterContentEffect, ret)
            else:
                self.changeContent(*cur)
                self.__afterContentEffect(ret)

    def onEnterKey(self):
        for i in range(self.backgroundCount):
            self.animCtl[i*2].pressed = True

        cur = self.posX, self.posY
        ret = self.getSelectActionEnter(*cur)

        if ret > 0:
            self.__beforeContentEffect(ret)
            koan.anim.Execute(0.25, self.changeContent, *cur)
            koan.anim.Execute(0.25, self.__afterContentEffect, ret)

    def resetCells(self):
        """
        reset grid status
        """
        rw = self.cellWidth()
        rh = self.cellHeight()

        self.dirty = True

        self.__capW = int((self.width + self.cellRegion[0]) / rw)
        self.__capH = int((self.height + self.cellRegion[1]) / rh)

        self.posX, self.posY = 0, 0
        self.__topX, self.__topY = 0, 0
        self._targetX.Assign(0)
        self._targetY.Assign(0)

        self.bound = (
                0, 0, self.width, min(self.__capH * rh, self.height) - 12,
                0,
                12,
                0,
                12)
                
        self.localbound = (
                0,
                0,
                self.cellSize[0] + self.cellRegion[0],
                self.cellSize[1] + self.cellRegion[1],
                0,
                0,
                0,
                0)

        self.__capH = int( math.ceil((self.height + self.cellRegion[1]) / float(rh)) )
        
        if self.__capW < 1:
            self.__capW = 1

        if self.__capH < 1:
            self.__capH = 1

        self.invoke('Cell Reset')
        self.invoke('Select Change', self.posX, self.posY)
        self.invoke("Cell Focus Change")

    def resetCells2(self):
        """
        reset grid status
        """
        self.focusCell(self.posX, self.posY)
        self.invoke('Cell Reset')

    def resetCellSize(self, cellSize, regionSize = None):
        if cellSize != None:
            self.cellSize = cellSize
        if regionSize != None:
            self.cellRegion = regionSize
        rw = self.cellWidth()
        rh = self.cellHeight()

        self.dirty = True

        self.__capW = int((self.width + self.cellRegion[0]) / rw)
        self.__capH = int((self.height + self.cellRegion[1]) / rh)
        if koan.is3D:
            self.bound = (
                0, 0, self.width, min(self.__capH * rh, self.height),
                0,
                12,
                0,
                12)
        else:
            self.bound = (
                0, 0, self.width, min(self.__capH * rh, self.height),
                0,
                0,
                0,
                12
            )

        self.localbound = (
                0,
                0,
                self.cellSize[0] + self.cellRegion[0],
                self.cellSize[1] + self.cellRegion[1],
                0,
                0,
                0,
                0)

        if self.__capW < 1:
            self.__capW = 1

        if self.__capH < 1:
            self.__capH = 1

    def cellWidth(self):
        """
        @return: the width of a whole cell, included margin
        """
        return self.cellSize[0] + self.cellRegion[0]

    def cellHeight(self):
        """
        @return: the height of a whole cell, included margin
        """
        return self.cellSize[1] + self.cellRegion[1]

    def cellPosition(self,u, v):
        """
        cell position (item) to point position (pixel)
        inverse: pt2cell
        """
        x = u * (self.cellWidth()) + self._targetX
        y = v * (self.cellHeight()) + self._targetY
        return x, y

    def cellLocalPos(self):
        return self.posX - self.__topX, self.posY - self.__topY

    def pt2cell(self, x, y):
        """
        point position (pixel) to cell position (item)
        inverse: cellPosition
        """
        x -= self._targetX
        y -= self._targetY
        u = int(x / self.cellWidth())
        v = int(y / self.cellHeight())
        if x % self.cellWidth() > self.cellSize[0] or y % self.cellHeight() > self.cellSize[1]:
            return -1, -1
        if u >= self.colCount or v >= self.rowCount or u < 0 or v < 0:
            return -1, -1
        return u, v

    def focusCell(self, u, v, **argd):
        """
        change focused cell to (u, v), and show the moving animation
        """
        if u >= self.colCount:
            u = self.colCount - 1

        if v >= self.rowCount:
            v = self.rowCount - 1

        if v == self.rowCount - 1 and u >= self.lastRowCount:
            u = self.lastRowCount - 1

        if u < 0:
            u = 0

        if v < 0:
            v = 0

        if (u == self.posX) and (v == self.posY):
            return True

        pre = self.posX, self.posY
        preTop = self.__topX, self.__topY

        self.posX = u
        self.posY = v

        if self.posX < self.__topX:
            self.__topX = self.posX

        if self.posX - self.__topX >= self.__capW:
            self.__topX = self.posX - self.__capW + 1

        if self.posY < self.__topY:
            self.__topY = self.posY

        if self.posY - self.__topY >= self.__capH:
            self.__topY = self.posY - self.__capH + 1

        if pre <> (self.posX, self.posY):
            self.invoke('Select Change', self.posX, self.posY)

        if (preTop <> (self.__topX, self.__topY) ) or \
            (self._targetX != self.__topX * self.cellWidth() ) or \
            (self._targetY != self.__topY * self.cellHeight() ):
            topx = self.__topX * self.cellWidth()
            topy = self.__topY * self.cellHeight()

            if koan.useAnimation and argd.get('anim', True):
                self._targetX.Reset(0.5, -topx)

                y1 = self._targetY.QueryValue()
                if y1 < -topy - 2000:
                    self._targetY.Assign(-topy - self.__maxAnimRange)
                if y1 > -topy + 2000:
                    self._targetY.Assign(-topy + self.__maxAnimRange)
                self._targetY.Reset(0.5, -topy)

            else:
                self._targetX.Assign(-topx)
                self._targetY.Assign(-topy)

        return True

    def onMouseWheel(self, delta):
        self.focusCell(self.posX, self.posY-delta)
        return True

    def onKey(self, key):
        if key in ['ENTER']:
            self.invoke('Enter')
            return True
        elif key == 'BACK' or key == 'BACKPAGE':
            if self.canBack():
                self.__beforeContentEffect(2)
                koan.anim.Execute(0.25, self.changeContentByBack)
                koan.anim.Execute(0.25, self.__afterContentEffect, 2)
                return True
            return False
        elif key == 'HOME':
            return self.focusCell(self.posX, 0)
        elif key == 'END':
            return self.focusCell(self.posX, self.rowCount-1)
        elif key == 'LEFT':
            if self.posX == 0:
                return False
            return self.focusCell(self.posX-1, self.posY)
        elif key == 'RIGHT':
            if self.posY == self.rowCount - 1:
                if self.posX == self.lastRowCount - 1:
                    return False
            elif self.posX == self.colCount - 1:
                return False
            return self.focusCell(self.posX+1, self.posY)
        elif key == 'UP':
            if self.posY == 0:
                return False
            return self.focusCell(self.posX, self.posY-1)
        elif key == 'DOWN':
            if self.posY == self.rowCount - 1:
                return False
            return self.focusCell(self.posX, self.posY+1)
        elif key == 'PAGEUP':
            # windows explorer like pageup
            # if focused item was not at top of screen, move focus to top
            # if focused item was at top, move one page up
            if self.posY > self.__topY:
                newposY = self.__topY
            elif self.posY == self.__topY:
                newposY = max(0, self.__topY - self.__capH + 1)
            else:
                assert False
            return self.focusCell(self.posX, max(0, newposY))
        elif key == 'PAGEDOWN':
            # windows explorer like pagedown
            # if focused item was not at bottom of screen, move focus to bottom
            # if focused item was at bottom, move one page down
            if self.posY < self.__topY + self.__capH - 1:
                newposY = self.__topY + self.__capH - 1
            elif self.posY == self.__topY + self.__capH - 1:
                newposY = min(self.rowCount - self.__capH, self.__topY + self.__capH - 1) + self.__capH -1
            else:
                assert False
            u, v = self.posX, min(self.rowCount-1, newposY)
            return self.focusCell(u, v)
        elif key == 'VSCROLL_PAGEUP':
            self.__topY = max(0, self.__topY - self.__capH)
            self._targetY.Assign(-self.__topY*self.cellHeight())
            return True
        elif key == 'VSCROLL_PAGEDOWN':
            newtopY = self.__topY + self.__capH
            if newtopY < self.rowCount:
                self.__topY = newtopY
                self._targetY.Assign(-self.__topY*self.cellHeight())
        elif key == 'HSCROLL_PAGEUP':
            self.__topX = max(0, self.__topX - self.__capW)
            self._targetX.Assign(-self.__topX*self.cellWidth())
            return True
        elif key == 'HSCROLL_PAGEDOWN':
            newtopX = self.__topX + self.__capW
            if newtopX < self.colCount:
                self.__topX = newtopX
                self._targetX.Assign(-self.__topX*self.cellWidth())
            return True
        return super(GridBase, self).onKey(key)

    def onDrawCellEx(self, render, xIndex, yIndex, rect):
        """
        function to draw one cell with its decoration
        overridable
        """
        v = self.getBackgroundIndex(xIndex, yIndex)
        if v != -1:
            if yIndex == self.posY and xIndex == self.posX:
                self.animCtl[v*2].draw(render, rect)
            else:
                self.animCtl[v*2 + 1].draw(render, rect)

        render.PushBound(*self.localbound)
        self.onDrawCell(render, xIndex, yIndex, rect)
        render.PopBound()

    def onDrawCell(self, render, xIndex, yIndex, rect):
        """
        function to draw one cell
        overridable
        """
        pass

    def _drawChangeEffect(self, render):
        render.Scale(self._changeEffectScale, self._changeEffectScale)
        render.PushAlpha(self._changeEffectAlpha)

    def isCellVisible(self, x, y):
        """
        check if a cell is visible on screen
        """
        return (x >= self.__topX and x <= self.__topX + self.__capW
            and y >= self.__topY and y <= self.__topY + self.__capH)

    def getCellVisibleRange(self):
        cellWidth = self.cellWidth()
        cellHeight = self.cellHeight()

        x1 = self._targetX.QueryValue()
        x2 = float(self._targetX)

        if x2 > x1:
            x1, x2 = x2, x1

        xBegin = max( int((-x1) / cellWidth), 0)
        xEnd = min( int((-x1 + self.width + cellWidth - 1) / cellWidth), self.colCount)

        y1 = self._targetY.QueryValue()
        y2 = float(self._targetY)
        if y1 > y2 + self.__maxAnimRange:
            y1 = y2 + self.__maxAnimRange
        if y1 < y2 - self.__maxAnimRange:
            y1 = y2 - self.__maxAnimRange

        if y2 > y1:
            y1, y2 = y2, y1

        yBegin = max( int((-y1) / cellHeight), 0)
        yEnd = min( int((-y2 + self.height + cellHeight - 1) / cellHeight), self.rowCount)
        return xBegin, xEnd, yBegin, yEnd

    def onDraw(self, render):
        super(GridBase, self).onDraw(render)
        
        cellWidth = self.cellWidth()
        cellHeight = self.cellHeight()

        render.PushMatrix()
        render.PushBound(*self.bound)

        self._drawChangeEffect(render)

        render.Translate(self._targetX, self._targetY)

        xBegin, xEnd, yBegin, yEnd = self.getCellVisibleRange()
        r = (0, 0, self.cellSize[0], self.cellSize[1])
        self.onDrawGrid(render, xBegin, xEnd, yBegin, yEnd, cellWidth, cellHeight, r)

        render.PopAlpha() # the pairing PushAlpha was in _drawChangeEffect()

        render.PopBound()
        render.PopMatrix()

    def onDrawGrid(self, render, xBegin, xEnd, yBegin, yEnd, cellWidth, cellHeight, rect):
        for i in range(yBegin, yEnd):
            if i == self.rowCount - 1:
                tempXEnd = self.lastRowCount
            else:
                tempXEnd = xEnd
            for j in range(xBegin, tempXEnd):
                render.PushMatrix()
                render.Translate(j * cellWidth, i * cellHeight)
                self.onDrawCellEx(render, j, i, rect)
                render.PopMatrix()

    def onMouseMove(self, x, y, flag):
        self.setFocus()
        pos = self.pt2cell(x, y)
        if pos <> (-1, -1):
            self.focusCell(*pos)

    def onMouseLeave(self):
        """
        process the mouse leave event
        can be overridden
        """
        pass

    def getVisibleRange(self):
        return self.__capW, self.__capH

class GridAnimItem:
    def __init__(self):
        animType = 'decay'
        self.__xPos = koan.anim.AnimTarget(animType, 0, 0, 0)
        self.__yPos = koan.anim.AnimTarget(animType, 0, 0, 0)

    def setTarget(self, x, y):
        #animDuration = 0.5
        animDuration = 0.3
        # the animation duration is function of the distance that it moved
        xDiff = x - self.__xPos.QueryValue()
        yDiff = y - self.__yPos.QueryValue()
        factor = ( (float(xDiff * xDiff + yDiff * yDiff) ) ** 0.5 ) / 640.0 + 0.25
        #factor = 1
        self.__xPos.Reset(animDuration * factor, x)
        self.__yPos.Reset(animDuration * factor, y)

    def assignPos(self, x, y):
        self.__xPos.Assign(x)
        self.__yPos.Assign(y)

    def getPosAnim(self):
        return self.__xPos, self.__yPos

class Grid(GridBase):
    def __init__(self, parent):
        GridBase.__init__(self, parent)
        self.__animPool = {}

    def resetCellSize(self, cellSize, regionSize = None, instantChange = False):
        # return if the new assigned size is the same as current size
        if self.cellSize == cellSize and self.cellRegion == regionSize:
            return

        # save grid status
        previousLocalPosY =  self.cellLocalPos()[1]
        previousTopY = self.posY - self.cellLocalPos()[1]
        previousIndex = self.posY * self.getVisibleRange()[0] + self.posX
        previousCapX = self.getVisibleRange()[0]
        previousCellWidth = self.cellWidth()
        previousCellHeight = self.cellHeight()

        # do reset cell size
        GridBase.resetCellSize(self, cellSize, regionSize)

        # update grid status
        n = self.getCellCount()
        self.colCount = self.getVisibleRange()[0]
        self.rowCount = (n + self.colCount - 1) / self.colCount
        self.lastRowCount = n - (self.rowCount - 1) * self.colCount

        # focus cell to the proper position
        newX = previousIndex % self.getVisibleRange()[0]
        newY = previousIndex / self.getVisibleRange()[0]
        self._GridBase__topY = max(newY - previousLocalPosY, 0)
        if newY > self.rowCount - 2:
            self._GridBase__topY = newY - self.getVisibleRange()[1]
        self.focusCell(newX, newY)
        self._targetY.Assign(self._targetY)

        # calculate the animations
        self.__animPool.clear()
        if instantChange:
            return
        cellWidth = self.cellWidth()
        cellHeight = self.cellHeight()
        xBegin, xEnd, yBegin, yEnd = self.getCellVisibleRange()
        visibleX = self.getVisibleRange()[0]
        currentTopY = self.posY - self.cellLocalPos()[1]
        for i in range(yBegin, yEnd):
            for j in range(xBegin, xEnd):
                index = i * visibleX + j
                self.__animPool[index] = GridAnimItem()
                item = self.__animPool[index]
                lastXPos = (index % previousCapX) * previousCellWidth
                lastYPos = (index / previousCapX - previousTopY) * previousCellHeight + currentTopY * cellHeight
                item.assignPos(lastXPos, lastYPos)
                item.setTarget(j * cellWidth, i * cellHeight)

    def onDrawGrid(self, render, xBegin, xEnd, yBegin, yEnd, cellWidth, cellHeight, rect):
        # clear unused item in the item pool
        for key in self.__animPool.keys():
            xPos, yPos = self.__animPool[key].getPosAnim()
            if xPos.QueryValue() == xPos and yPos.QueryValue() == yPos:
                del self.__animPool[key]

        # check that anim pool did'nt grow unbounded
        assert len(self.__animPool) <= 100

        # do the drawing
        visibleX = self.getVisibleRange()[0]
        for i in range(yBegin, yEnd):
            for j in range(xBegin, xEnd):
                index = i * visibleX + j
                # if there exist item in anim pool for this position,
                # use it to animate grid cell
                if self.__animPool.has_key(index):
                    xPos, yPos = self.__animPool[index].getPosAnim()
                else:
                    xPos, yPos = j * cellWidth, i * cellHeight
                render.PushMatrix()
                render.Translate(xPos, yPos)
                self.onDrawCellEx(render, j, i, rect)
                render.PopMatrix()

