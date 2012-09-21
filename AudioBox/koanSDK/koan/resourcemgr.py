import koan
import weakref
import gc
from event import EventManager

class ResourceManager(EventManager):
    mgrs = []
    
    @staticmethod
    def _gc():
        for m in ResourceManager.mgrs:
            if m:
                m().gc()
    
    @staticmethod
    def _clearAll():
        for m in ResourceManager.mgrs:
            if m:
                m().clearAll()
                            
    def __init__(self, window, **argd):
        koan.EventManager.__init__(self)
        
        ResourceManager.mgrs.append(weakref.ref(self))        
        
        self.window = window
        self.resMap = {}
        self.lastClear = koan.GetTime()
        self.autoRemove(self.window.bind("Device Lost", self.onDeviceLost))
        self.autoRemove(self.window.bind("Device Restore", self.onDeviceRestore))
        self.autoRemove(self.window.bind("Free Unused Resource", self.freeUnused))

    def __del__(self):        
        dead = []
        for m in ResourceManager.mgrs:
            if not m():
                dead.append(m)
        for m in dead:
            ResourceManager.mgrs.remove(m)

        EventManager.__del__(self)
        
    def close(self):
        self.clearAll()
        EventManager.close(self)
        self.window = koan.Null

    def clearAll(self):
        self.window.dirty = True
        self.resMap.clear()
        #print 'resource clearAll'
        #gc.collect()

    def clear(self, *key):
        self.window.dirty = True
        for i in self.resMap.keys():
            if i == key:
                self.resMap[i] = None
                del self.resMap[i]
        #gc.collect()

    def onDeviceLost(self):
        #self.clearAll()
        pass

    def onDeviceRestore(self):
        pass

    def freeUnused(self):
        for item in self.resMap.keys():
            if self.resMap[item][2] < self.window.frameNumber - 1:
                self.resMap[item] = None
                del self.resMap[item]
        #print 'Current Free', self.window.render.GetFreeMemory() / (1024 * 1024), 'MB'

    def gc(self):
        gcTime = 1.1
        gcMax = 3
        gcCount = 0
        
        curFrame = self.window.frameNumber
        curPaint = self.window.render.GetPaintNumber()
        t = koan.GetTime()
        if t - self.lastClear > gcTime:
            self.lastClear = koan.GetTime()

            for item in self.resMap.keys():
                dummy, ft, f = self.resMap[item]
                if t - ft > 15 and curFrame - f > 30 and (not dummy or curPaint > dummy.GetPaintNumber()):
                    del self.resMap[item]
                    gcCount += 1
                    if gcCount >= gcMax:
                        break

    def LoadResource(self, *key):
        raise Exception, "this is a pure virtual function"

    def GetResource(self, *key):
        if self.resMap.has_key(key):
            res = self.resMap[key][0]
        else:
            try:
                res = self.LoadResource(*key)
            except:
                #import traceback
                #traceback.print_exc()
                res = None
        if res:
            self.resMap[key] = res, koan.GetTime(), self.window.frameNumber
        return res
