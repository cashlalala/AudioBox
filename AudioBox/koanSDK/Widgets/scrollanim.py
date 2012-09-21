import math
from weakref import ref
import koan
from koan.event import EventManager


#--------------------------------------------------------------------------
class ScrollAnimBase(EventManager):
    def __init__(self, parent):
        EventManager.__init__(self)
        self.animatom = None
        self._parent = ref(parent)
        self.run = None

    def free(self):
        self.onStopScroll()
        self._parent = None
        EventManager.clear(self)

    def onCalc(self, diffWidth, totalWidth):
        return 0, 1.0 # return offset

    def onStartScroll(self):
        self.run = self.onCalc

    def onStopScroll(self):
        if self.animatom:
            self.animatom.remove()
            self.animatom = None
        self.run = None

#--------------------------------------------------------------------------
class ScrollAnim(ScrollAnimBase):
    def __init__(self, parent):
        ScrollAnimBase.__init__(self, parent)
        self.speed = 50.0
        self.startTime = 0.0
        self.currTime = 0.0
        self.restTime = 0.5
        self.offsetTime = 1.0
        self.autoRemove(self.changeEvent('currTime', self.__onCurrTimeChanged));
        self.reseted = True
        self.updateRateGDI = 12
        self.__nextUpdateTimeGDI = 0
        self.__scrollDirty = False

    def onStartScroll(self):
        self.reseted = True
        self.onStopScroll()
        ScrollAnimBase.onStartScroll(self)
        self.startTime = koan.GetTime()

    def __onCurrTimeChanged(self):
        if not koan.useAnimation:
            if not self.__scrollDirty:
                self.__scrollDirty = True
                koan.anim.Cancel(self.__onNextScroll)
                koan.anim.Execute(1.0 / self.updateRateGDI, self.__onNextScroll)

    def __onNextScroll(self):
        if self._parent:
            self._parent().setDirty()
        self.__scrollDirty = False

    def onCalcForGDI(self, diffWidth, totalWidth):
        self.currTime = koan.GetTime() - self.startTime
        anitime = float(diffWidth) / self.speed
        stop = self.offsetTime + anitime
        fade = stop + self.restTime
        total = fade + self.restTime + self.offsetTime
        t = math.fmod(self.currTime, total)
        pos = self.speed * max(0.0, t - self.offsetTime)
        if t > stop:
            if t < fade:
                a = 1.0 - float(t - stop ) / (self.restTime)
                pos = diffWidth
            else:
                if t < fade + self.restTime:
                    a = float(t - fade) / self.restTime
                else:
                    a = 1.0
                pos = 0
        else:
            a = 1.0
        return -pos, a

    def onCalc(self, diffWidth, totalWidth):
        if self.run:
            if not koan.useAnimation:
                return self.onCalcForGDI(diffWidth, totalWidth)
            if self.reseted == True:
                self.currTime = koan.GetTime() - self.startTime
                self.reseted = False
                aniTime = float(diffWidth) / self.speed
                offsetTime = self.offsetTime
                stopTime = self.offsetTime + aniTime
                fadeTime = stopTime + self.restTime
                totalTime = fadeTime + self.restTime + self.offsetTime
                posKey = (0, offsetTime/totalTime, stopTime/totalTime, fadeTime/totalTime, fadeTime/totalTime + 0.000001, 1)
                posValue = (0, 0, -diffWidth, -diffWidth, 0, 0)
                self.posAnim = koan.anim.AnimLinear(totalTime, posKey, posValue, loop=True)
                alphaKey = (0, offsetTime/totalTime, stopTime/totalTime, fadeTime/totalTime, 1)
                alphaValue = (1, 1, 1, 0, 1)
                self.alphaAnim = koan.anim.AnimLinear(totalTime, alphaKey, alphaValue, loop=True)
        return self.posAnim, self.alphaAnim
