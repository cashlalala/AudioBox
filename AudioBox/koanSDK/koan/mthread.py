import time
import platform
import threading
import traceback
from threading import Thread, RLock, Event
from Queue import Queue
import bisect

class PQTask(object):
    def __init__(self):
        object.__init__(self)
        self.pri = 0
        self.item = None
    def __cmp__(self, b):
        return cmp(self.pri, getattr(b, 'pri', 0))
            
class PQThread(threading.Thread):
    def __init__(self, name = ""):
        threading.Thread.__init__(self)
        self.name = name
        self.queueCmd = Queue()
        self.queue = []
        self.lock = threading.Lock()
        self.quit = False
        self.busy = False

    def insertTask(self, priority, itm):
        self.lock.acquire()
        p = PQTask()
        p.pri = priority
        p.item = itm
        bisect.insort_right(self.queue, p)
        self.queueCmd.put('task')
        self.lock.release()

    def appendTask(self, priority, itm):
        self.lock.acquire()
        p = PQTask()
        p.pri = priority
        p.item = itm
        bisect.insort_left(self.queue, p)
        self.queueCmd.put('task')
        self.lock.release()

    def hasTask(self):
        l = 0
    
        self.lock.acquire()
        l = len(self.queue)
        self.lock.release()
    
        if self.busy or self.queueCmd.qsize() > 0 or l > 0:
            return True
        return False

    def onThreadStart(self):
        pass

    def onThreadEnd(self):
        pass

    def processItem(self, priority, itm):
        pass

    def run(self):
        print 'PQThread start'
        platform.InitThread()
        
        self.onThreadStart()
        while(1):
            self.busy = False
            task = self.queueCmd.get(True)
            
            if task == 'close':
                break
            elif task == 'task':
                self.lock.acquire()
                self.busy = True
                p = self.queue.pop()
                priority, itm = p.pri, p.item
                self.lock.release()
            
            if itm == 'close':
                break
            try:
                self.processItem(priority, itm)
            except:
                traceback.print_exc()
                pass
        
        self.onThreadEnd()
        platform.UninitThread()
        print 'PQThread exit'

    def createThread(self):
        self.start()
        self.__running = True

    def close(self):
        if not self.quit:
            self.insertTask(1000, 'close')
            self.join()
            self.quit = True

class QueueThread(threading.Thread):
    def __init__(self, name = ""):
        threading.Thread.__init__(self)
        self.queue = Queue()
        self.closeEvent = threading.Event()
        self.__running = False

    def addItem(self, itm):
        self.queue.put(itm)

    def processItem(self, item):
        pass

    def run(self):
        platform.InitThread()
        while(not self.closeEvent.isSet()):
            itm = self.queue.get(True)
            if self.closeEvent.isSet():
                return
            self.processItem(itm)
        platform.UninitThread()

    def createThread(self):
        self.start()
        self.__running = True

    def close(self):
        self.closeEvent.set()
        self.queue.put(None)
        if self.__running:
            self.join()

class AutoLock:
    def __init__(self, lock):
        self.lock = lock
        self.lock.acquire()

    def __del__(self):
        self.lock.release()


class IteratingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.funcs = []
        self.quitEvent = threading.Event()
        self.lock = threading.Lock()
        self.runEvent = threading.Event()
        self.runEvent.clear()

    def __iterate(self):
        l = AutoLock(self.lock)
        for i in range(len(self.funcs)):
            self.funcs[i]()

    def run(self):
        print 'Start Iterating Thread'
        platform.InitThread()
        while not self.quitEvent.isSet():
            self.__iterate()
            self.runEvent.wait()
            self.quitEvent.wait(0.001)
        print 'Close Iterating thread'
        platform.UninitThread()

    def add(self, func):
        l = AutoLock(self.lock)

        if func in self.funcs:
            return

        self.funcs.append(func)
        self.runEvent.set()
        print 'IteratingThread Add:', func

    def remove(self, func):
        l = AutoLock(self.lock)
        self.funcs.remove(func)
        if len(self.funcs) <= 0:
            self.runEvent.clear()
        print 'IteratingThread Remove:', func

    def start(self):
        self.quitEvent.clear()
        threading.Thread.start(self)

    def stop(self):
        self.runEvent.set()
        self.quitEvent.set()
        self.join()

class CmdThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.__EventSend = Event()
        self.__EventSend.clear()
        self.__EventComplete = Event()
        self.__EventComplete.clear()
        self.__cmd2 = ''
        self.__Param = None
        self.__ReturnVal = None
        self.__AccessLock = RLock()

    def Reply(self, ret = None):
        self.__ReturnVal = ret
        self.__EventSend.clear()
        self.__EventComplete.set()

    def GetRequest(self):
        self.__EventSend.wait()
        self.__EventSend.clear()
        #print 'Get', self.__cmd2, self.__Param
        return self.__cmd2, self.__Param

    def CheckRequest(self):
        if not self.__EventSend.isSet():
            return False;
        return True;

    def Command(self, cmd, *arg):
        luck = AutoLock(self.__AccessLock)

        if not self.isAlive():
            raise ValueError, "Thread is not alive"

        #print 'command', cmd, arg
        self.__cmd2 = cmd
        self.__Param = arg

        self.__EventSend.set();
        self.__EventComplete.wait();
        self.__EventComplete.clear()

        #print 'command ret', self.__ReturnVal
        return self.__ReturnVal


class PQThreadEx(CmdThread):
    def __init__(self):
        self.queue = []
        self.qlock = threading.Lock()
        self.pause = False
        CmdThread.__init__(self)

    def cancelTask(self, canceller):
        self.qlock.acquire()
        
        queue, self.queue = self.queue, []
        
        for i in queue:
            if not canceller.Cancel(i.item):
                self.queue.append(i)

        self.qlock.release()
        

    def insertTask(self, priority, itm, nodup = True):
        
        itm.pri = priority
        
        p = PQTask()
        p.pri = priority
        p.item = itm

        self.qlock.acquire()
        
        if nodup:
            for i in self.queue:
                if i.item.CheckTask(itm):
                    p = None
                    break
        if p:
            bisect.insort_right(self.queue, p)
        self.qlock.release()

    def appendTask(self, priority, itm, nodup = True):
    
        itm.pri = priority
        
        p = PQTask()
        p.pri = priority
        p.item = itm

        self.qlock.acquire()
        
        if nodup:
            for i in self.queue:
                if i.item.CheckTask(itm):
                    p = None
                    break
        if p:
            bisect.insort_left(self.queue, p)
        self.qlock.release()

    def hasTask(self):
        return len(self.queue) > 0

    def onThreadStart(self):
        pass

    def onThreadEnd(self):
        pass

    def processItem(self, priority, itm):
        pass

    def processCmd(self, cmd, *param):
        if cmd == 'PauseThread':
            self.pause = param[0]
            self.Reply()
        else:
            print 'Non handle command', cmd, param
            self.Reply()

    def Pause(self, v):
        return self.Command('PauseThread', v)

    def run(self):
        print 'PQThreadEx start'
        platform.InitThread()
        
        self.onThreadStart()
        while(1):
            if self.CheckRequest():
                cmd, param = self.GetRequest()
                if cmd == 'ExitThread':
                    self.Reply()
                    break
                else:
                    self.processCmd(cmd, *param)
            elif self.pause:
                time.sleep(0.01)
            elif self.queue:
                
                self.qlock.acquire()
                p = self.queue.pop()
                self.qlock.release()

                priority, itm = p.pri, p.item

                try:
                    self.processItem(priority, itm)
                except:
                    traceback.print_exc()
                    pass
            else:
                time.sleep(0.01)
                
        self.onThreadEnd()
        platform.UninitThread()
        print 'PQThreadEx exit'

    def createThread(self):
        self.start()

    def close(self):
        if not self.isAlive():
            return
        self.Command('ExitThread')
        self.join()
            
if __name__ == '__main__':
    import time

    class MyThread(CmdThread):
        def __init__(self):
            CmdThread.__init__(self)
            self.start()

        def run(self):
            while 1:
                cmd, arg = self.GetRequest()
                #print 'get', cmd, arg
                if cmd == 'close':
                    self.Reply(0)
                    break

                elif cmd == 'say':
                    print arg
                    self.Reply(arg)

                elif cmd == 'sleep':
                    self.Reply(0)
                    print 'before sleep', arg
                    time.sleep(*arg)
                    print 'after sleep'

        def close(self):
            self.Command('close')
            self.join()

    x = MyThread()

    for i in range(10):
        for j in range(3):
            x.Command("say", 'fuck x')
        x.Command("sleep", 1)
    x.Command("say", 'fuck x again')
    x.close()
