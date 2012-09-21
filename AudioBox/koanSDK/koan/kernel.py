"""
koan Engine
"""

import  koan
from    event              import EventManager
from    koan.resourcemgr   import ResourceManager
import  time

class Kernel(EventManager):
    def __init__(self):
        EventManager.__init__(self)
        self._window = None
        self.ending = False
        self.preIdleTime = time.time()
        
    def Init(self):
        """
        create a dummy window to handle main message

        @rtype: None
        """
        self._window = koan.platform.CreateWindow()
        self._window.CreateDummy()
        self._window.SetCore(self)
        
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
        if msg == 'PROCESS EVENT':
            koan.animManager.pooling()
            return 1

        elif msg == 'CLOSE':
            if self.exit():
                return 1
            return 0

        elif msg == 'FORCE CLOSE':
            self.close()
            self.ending = True
            return 1

        elif msg == "TIME CHANGE":
            doGC = True
            t = time.time()        
            for w in koan.windows:
                if w.invalid or t - w.preDrawTime < 3:
                    doGC = False
                    break
            if doGC:
                ResourceManager._gc()
                
        else:
            #self.invoke(msg, pm1, pm2)
            pass
        return 1

    def onIdle(self):
        if koan.animManager:
            koan.animManager.pooling()
            for w in koan.windows:
                if w.invalid:
                    return
            koan.animManager.fireExecuteTasks()
        
    def exit(self):
        """
        to exit window

        @rtype: None
        """
        if self._window:
            self.ending = True
            self._window.Hide()
            self.close()
            return True
        return False

    def close(self):
        """
        uninitial the koan lib.

        @rtype: None
        """
        koan.animManager.pooling()

        print '[Kernel.py] Before Fire Close'
        self.fire('Close')
        koan.animManager.pooling()


        if self._window:            
            self._window.SetCore(None)
            self._window.Close()
            self._window = None
        
        EventManager.clear(self)

#########################################################
#
#   Test This Module
#
#########################################################

if __name__ == '__main__':
    pass
