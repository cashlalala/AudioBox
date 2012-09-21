"""
module for management of animations

here animation means -- changing of an object's field value by time

"""
import bisect
import os
import math
import threading
import koan
import traceback
import animate.Interpolator
import weakref
import operator

#########################################################
#
#   New Style Animation
#
#########################################################

class AnimBase:
    """
    @ivar applyCount: to ensure that rendering with anim
                      has a corresponding anim.apply, like:
                      >>> koan.anim.apply(animScale)
                      >>> self.render.Scale(animScale, 1)
                      misuse of anim, like
                      >>> self.render.Scale(animScale, 1)
                      without anim.apply will cause an assert
    """
    def __init__(self, **argd):
        #self.render = argd.get('render', koan.render)
        self.animObj = None
        self.const = 0.0
        self.applyCount = 0

    def __autocheck__(self):
        import inspect
        try:
            args = inspect.getargvalues(inspect.currentframe().f_back.f_back)[3]['args']
            if args[0] == self.render:
                i = 1
                for a in args[1:]:
                    if a is self:
                        self.apply(i)
                    i+=1
        except:
            pass
            
    def __float__(self):
        #self.__autocheck__()
        return self.const        

    def __int__(self):
        #self.__autocheck__()
        return int(self.const)

    def __coerce__(self, other):
        return (self.const, other)

    def __nonzero__(self):
        return self.const != 0

    def __long__(self):
        #self.__autocheck__()
        return long(self.const)

    def __neg__(self):
        return -1 * self.const

    def QueryValue(self):
        return self.animObj.GetValue()

    def apply(self, n):
        self.applyCount += 1
        koan.render.SetAnim(self.animObj, n)
        
    '''
    def apply(self, n, **argd):
        self.applyCount += 1
        koan.render.SetAnim(self.animObj, n, argd.get('debug', False))
    '''
    
    def isConst(self):
        return self.animObj.IsConst()

    def isStable(self):
        return self.animObj.IsStable()
        
    def Reset(self):
        self.animObj.Reset()       

    def CheckAbsArg(self, argd):
        absTime = argd.get('starttime')
        if absTime <> None:
            self.animObj.SetAbsStartTime(absTime)

class AnimLinear(AnimBase):
    def __init__(self, tlen, p, v, **argd):
        AnimBase.__init__(self, **argd)

        if len(p) == 0 or \
            len(p) <> len(v) or \
            p[-1] <> 1.0:
            raise ValueError, "Argument error"

        pre = p[0]
        for i in range(1, len(p)):
            if p[i] <= pre:
                raise ValueError, "Argument error"
            pre = p[i]

        loop = argd.get('loop', False)

        self.animObj = animate.Interpolator.LinearInterpolator(loop, tlen)
        self.CheckAbsArg(argd)

        for i in xrange(len(p)):
            self.animObj.AddValues(p[i], v[i])

        self.const = float(v[-1])
        self.animObj.Reset()
        
class AnimSpring(AnimBase):
    def __init__(self, tlen, f, t, **argd):
        AnimBase.__init__(self, **argd)
        self.animObj = animate.Interpolator.SpringInterpolator(tlen, f, t)
        self.CheckAbsArg(argd)        
        self.animObj.Reset()
        self.const = float(t)

class AnimTarget(AnimBase):
    def __init__(self, type, tlen, f, t, dirtyTarget = None, **argd):
        AnimBase.__init__(self, **argd)
        self.animObj = animate.Interpolator.TargetInterpolator(type, tlen, f, t)
        self.CheckAbsArg(argd)
        self.animObj.Reset()
        self.dirtyTarget = None
        if dirtyTarget:
            self.dirtyTarget = weakref.ref(dirtyTarget)
        self.const = float(t)
        self.Dirty()

    def Dirty(self):
        if self.dirtyTarget:
            o = self.dirtyTarget()
            if o:
                o.dirty = True

    def Reset(self, t, target, **argd):
        self.const = float(target)
        if koan.useAnimation:
            
            absTime = argd.get('starttime')
            if absTime == None:
                absTime = 0
                useAbs = False
            else:
                useAbs = True 
            
            self.animObj.ResetTarget(t, target, useAbs, absTime)
        else:
            self.animObj.ForceAssignValue(target)
        self.Dirty()

    def ForceReset(self, t, target):
        self.const = float(target)
        if koan.useAnimation:
            self.animObj.ResetTargetNow(t, target, koan.GetTime())
        else:
            self.animObj.ForceAssignValue(target)
        self.Dirty()

    def Assign(self, value):
        if koan.useAnimation:
            self.animObj.AssignValue(value)
        else:
            self.animObj.ForceAssignValue(value)
        self.const = float(value)
        self.Dirty()
        
    def Stop(self):
        self.animObj.Stop()
        self.const = self.animObj.QueryValue()
        
    def ForceAssign(self, value):
        self.animObj.ForceAssignValue(value)
        self.const = float(value)

    def QueryValue(self):
        return self.animObj.QueryValue()

class __AnimSin(AnimBase):
    def __init__(self, tlen, **argd):
        AnimBase.__init__(self, **argd)
        self.animObj = animate.Interpolator.SinInterpolator(tlen)
        self.CheckAbsArg(argd)        
        self.animObj.Reset()
        self.const = float(0)

class AnimTransform(AnimBase):
    def __init__(self, interpolator, scale, transition, **argd):
        AnimBase.__init__(self, **argd)
        self.interpolator = interpolator
        if isinstance(interpolator, AnimTransform):
        # to merge multiple AnimTransforms
            self.scale = interpolator.scale * scale
            self.transition = interpolator.transition * scale + transition
            self.animObj = animate.Interpolator.LinearTransform(interpolator.baseAnimObj, self.scale, self.transition)
            self.baseAnimObj = interpolator.baseAnimObj
        else:
            self.baseAnimObj = interpolator.animObj
            self.animObj = animate.Interpolator.LinearTransform(interpolator.animObj, scale, transition)
            self.animObj.Reset()
            self.scale = scale
            self.transition = transition

    def __float__(self):
        #self.__autocheck__()
        return self.scale * float(self.interpolator) + self.transition

    def __int__(self):
        #self.__autocheck__()
        return int(self.scale * float(self.interpolator) + self.transition)

    def __coerce__(self, other):
        return (self.scale * float(self.interpolator) + self.transition, other)

class PolynomialTransform(AnimBase):
    def __init__(self, interpolator, a0, a1, a2, a3, **argd):
        AnimBase.__init__(self, **argd)
        self.interpolator = interpolator
        self.animObj = animate.Interpolator.PolynomialTransform(interpolator.animObj, a0, a1, a2, a3)
        self.CheckAbsArg(argd)        
        self.animObj.Reset()
        self.a0 = a0
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        
    def __float__(self):
        t = float(self.interpolator)
        return self.a0 + self.a1 * t + self.a2 * t * t + self.a3 * t * t * t

    def __int__(self):
        t = float(self.interpolator)
        return int(self.a0 + self.a1 * t + self.a2 * t * t + self.a3 * t * t * t)

    def __coerce__(self, other):
        t = float(self.interpolator)
        return (self.a0 + self.a1 * t + self.a2 * t * t + self.a3 * t * t * t, other)

def AnimSin(tlen, scale = 1, transition = 0):
    if scale == 1 and transition == 0:
        return __AnimSin(tlen)
    else:
        return AnimTransform(__AnimSin(tlen), scale, transition)

class FunctionTransform(AnimBase):
    def __init__(self, funcInterpolator, paramInterpolator, **argd):
        AnimBase.__init__(self, **argd)
        self.funcInterpolator = funcInterpolator
        self.paramInterpolator = paramInterpolator
        self.animObj = animate.Interpolator.FunctionTransform(funcInterpolator.animObj, paramInterpolator.animObj)
        self.CheckAbsArg(argd)        
        self.animObj.Reset()
        self.const = float(self.funcInterpolator)

class KeyframeValues:
    def __init__(self, start, end, values, loop = False):
        self.keyvalues = animate.Interpolator.KeyframeValues()
        self.keyvalues.StartSetValues(start, end, loop)
        for value in values:
            self.keyvalues.AddValue(float(value))

class AnimKeyframeTransform(AnimBase):
    def __init__(self, interpolator, keyvalues, **argd):
        AnimBase.__init__(self, **argd)
        self.interpolator = interpolator
        self.keyvalues = keyvalues
        assert not isinstance(interpolator, AnimKeyframeTransform), 'not allow recursively use of transform'
        assert not isinstance(interpolator, AnimTransform), 'not allow recursively use of transform'
        self.animObj = animate.Interpolator.KeyframeTransform(interpolator.animObj, keyvalues.keyvalues)
        self.CheckAbsArg(argd)        
        self.animObj.Reset()

    def __float__(self):
        #self.__autocheck__()
        return self.keyvalues.keyvalues.Transform(float(self.interpolator))

    def __int__(self):
        #self.__autocheck__()
        return self.keyvalues.keyvalues.Transform(float(self.interpolator))

    def __coerce__(self, other):
        return (self.keyvalues.keyvalues.Transform(float(self.interpolator)), other)

class FollowAnimValue(AnimBase):
    def __init__(self, refobj, valuediff):
        AnimBase.__init__(self)

        if isinstance(refobj, AnimBase):
            obj = refobj.animObj
        else:
            obj = None
            valuediff += float(refobj)

        self.const = refobj + valuediff
        self.animObj = animate.Interpolator.FollowAnimValue(obj, valuediff)

class AddAnimValue(AnimBase):
    def __init__(self, a, b):
        AnimBase.__init__(self)

        if isinstance(a, AnimBase):
            aobj = a.animObj
        else:
            aobj = animate.Interpolator.FollowAnimValue(None, float(a)) # XXX

        if isinstance(b, AnimBase):
            bobj = b.animObj
        else:
            bobj = animate.Interpolator.FollowAnimValue(None, float(b)) # XXX


        self.const = a + b
        self.animObj = animate.Interpolator.AddAnimValue(aobj, bobj)

class SubAnimValue(AnimBase):
    def __init__(self, a, b):
        AnimBase.__init__(self)

        if isinstance(a, AnimBase):
            aobj = a.animObj
        else:
            aobj = animate.Interpolator.FollowAnimValue(None, float(a)) # XXX

        if isinstance(b, AnimBase):
            bobj = b.animObj
        else:
            bobj = animate.Interpolator.FollowAnimValue(None, float(b)) # XXX

        self.const = a - b
        self.animObj = animate.Interpolator.SubAnimValue(aobj, bobj)

class MulAnimValue(AnimBase):
    def __init__(self, a, b):
        AnimBase.__init__(self)

        if isinstance(a, AnimBase):
            aobj = a.animObj
        else:
            aobj = animate.Interpolator.FollowAnimValue(None, float(a)) # XXX

        if isinstance(b, AnimBase):
            bobj = b.animObj
        else:
            bobj = animate.Interpolator.FollowAnimValue(None, float(b)) # XXX

        self.const = float(a) * float(b)
        self.animObj = animate.Interpolator.MulAnimValue(aobj, bobj)

class DivAnimValue(AnimBase):
    def __init__(self, a, b):
        AnimBase.__init__(self)

        if isinstance(a, AnimBase):
            aobj = a.animObj
        else:
            aobj = animate.Interpolator.FollowAnimValue(None, float(a)) # XXX

        if isinstance(b, AnimBase):
            bobj = b.animObj
        else:
            bobj = animate.Interpolator.FollowAnimValue(None, float(b)) # XXX

        self.const = float(a) / float(b)
        self.animObj = animate.Interpolator.DivAnimValue(aobj, bobj)

def add(a, b):
    if isinstance(a, AnimBase) or isinstance(b, AnimBase):
        return AddAnimValue(a, b)
    return float(a)+float(b)
def sub(a, b):
    if isinstance(a, AnimBase) or isinstance(b, AnimBase):
        return SubAnimValue(a, b)
    return float(a)-float(b)
def mul(a, b):
    if isinstance(a, AnimBase) or isinstance(b, AnimBase):
        return MulAnimValue(a, b)
    return float(a)*float(b)
def div(a, b):
    if isinstance(a, AnimBase) or isinstance(b, AnimBase):
        return DivAnimValue(a, b)
    return float(a)/float(b)
def neg(a):
    if isinstance(a, AnimBase):
        return AnimTransform(a, -1, 0)
    return -a

def apply(obj, n):
    if hasattr(obj, "apply"):
        obj.apply(n)

'''
def apply(obj, n, **argd):
    if hasattr(obj, "apply"):
        obj.apply(n, **argd)
'''

def MakeAnims(animobj, tlen, p, vs, **argd):
    values = zip(*vs)

    anims = []
    for i in range(len(values)):
        anims.append(animobj(tlen, p, values[i], **argd))
    return anims

#########################################################
#
#   Function Declare
#
#########################################################

def GetAnimManager():
    """
    get the default animManager
    """
    return koan.animManager

def __calKeyframes(start, end, func, *additionalArgs, **keyArgs):
    """
    helping to calculate and pack key values
    """
    perc = start
    values = func(perc, *additionalArgs)
    samplingRate = 60.0
    if keyArgs.has_key('samplingRate'):
        samplingRate = keyArgs['samplingRate']

    keyArrays = []
    if operator.isSequenceType(values):
        valueCount = len(values)
        isSequence = True
        for value in values:
            keyArrays.append([value])
    else:
        isSequence = False
        keyArrays.append(values)

    offset = 1.0 / samplingRate
    epsilon = offset * 0.0001
    while perc != end:
        perc += offset
        if (end - start > 0) ^ ((perc + epsilon) < end):
            perc = end
        values = func(perc, *additionalArgs)
        if isSequence:
            for i in range(valueCount):
                keyArrays[i].append(values[i])
        else:
            keyArrays.append(values)
    return keyArrays

def makeKeyframe(start, end, func, *additionalArgs, **keyArgs):
    valueArrays = __calKeyframes(start, end, func, *additionalArgs, **keyArgs)
    loop = False
    if keyArgs.has_key('loop'):
        loop = keyArgs['loop']    
    return KeyframeValues(start, end, valueArrays, loop)

def makeKeyframeAnim(start, end, func, *addionalArgs, **keyArgs):
    """
    @param start: starting animation time
    @param end: ending animation time
    @param func: function to calculate animation values
    """
    linearAnim = AnimLinear(end - start, (0, 1), (start, end))
    keyValues = makeKeyframe(start, end, func, *addionalArgs, **keyArgs)
    return AnimKeyframeTransform(linearAnim, keyValues)



# ---------------------------------------------------------------------
#
#   Math Mapping Object
#
# ---------------------------------------------------------------------

class Linear:
    """
    Linear Interpolator Value by assigning key value in key time
    """
    def __init__(self, period, value):
        if len(period) <> len(value):
            raise ValueError

        if len(period) < 2 or len(value) < 2:
            raise ValueError

        for i in range(len(period)):
            if period[i] < 0 or period[i] > 1:
                raise ValueError

        self.period = period
        self.value = value

    def print_debug(self):
        print self.period, self.value

    def map(self, prec):
        """
        map from time to value by interpolation

        @rtype: float
        """
        if prec <= 0.0:
            return self.value[0]

        if prec >= 1.0:
            return self.value[len(self.value) - 1]

        idx = bisect.bisect(self.period, prec) - 1

        dlen = self.period[idx + 1] - self.period[idx]
        dcur = prec - self.period[idx]

        if not dlen == 0:
            newPrec = float(dcur) / float(dlen)
        else:
            newPrec = 1

        v0 = self.value[idx]
        v1 = self.value[idx + 1]
        return v0 + float(v1 - v0) * newPrec

koan.optimize(Linear.map)

class Log:
    """
    Log Interpolator Value
    """
    e_1 = math.e - 1.0
    def __init__(self, e, fromValue, toValue):
        self.fromValue = fromValue
        self.toValue = toValue
        self.e = e

    def print_debug(self):
        print self.fromValue, self.toValue

    def map(self, prec):
        """
        @rtype
        """
        if prec <= 0.0:
            return self.fromValue

        if prec >= 1.0:
            return self.toValue

        prec **= self.e

        diff = self.toValue - self.fromValue
        return self.fromValue + math.log(1 + Log.e_1 * prec) * diff

koan.optimize(Log.map)

#########################################################
#
#   Animation Function
#
#########################################################

class AnimAtom:
    """
    a representation of an animation
    for management of anims
    """
    def __init__(self, task = None):
        self.task = task
    def remove(self):
        """
        to remove this anim task from animManager

        @rtype: None
        """
        if self.task <> None and koan.animManager:
            koan.animManager.removeTask(self.task)
            self.task.close()
            self.task = None            

def PostEvent(func, *arg):
    """
    post event to animManager

    Posted Events cannot be canceled

    @rtype: None
    """
    koan.animManager.addPostEvent(func, *arg)

def Cancel(obj, attr = None):
    """
    cancel a task from animManager
    """
    if koan.animManager:
        koan.animManager.cancel(obj, attr)

def Execute(t, func, *arg, **argd):
    """
    execute a function later with animManager

    @param t: this function will be executed t(secs) later
    @rtype: AnimAtom
    """
    e = ExecuteTask(t, koan.Action(func, *arg))
    koan.animManager.add(e, **argd)
    return AnimAtom(e)

def AlwaysExecute(func, *arg, **argd):
    """
    use animManager to execute a function continuously

    @rtype: AnimAtom
    """
    e = ExecuteTask(0, koan.Action(func, *arg), **argd)
    e.always = True
    koan.animManager.add(e, **argd)
    return AnimAtom(e)

def IntervalExecute(t, func, *arg, **argd):
    """
    execute a function 1 time / t sec

    @param t: the interval between 2 execution
    @rtype: AnimAtom
    """
    e = ExecuteTask(t, koan.Action(func, *arg), **argd)
    e.always = True
    koan.animManager.add(e, **argd)
    return AnimAtom(e)

def Once(obj, atr, tm, p, v, **argd):
    """
    @return: a Task set obj.atr with linear interpolated values
    @rtype: AnimAtom
    """
    e = AnimTask(obj, atr, **argd)
    e.once(tm, Linear(p, v))
    return AnimAtom(e)

def OnceEx(obj, atr, tm, func, **argd):
    """
    @return: a Task repeatly set obj.atr with linear interpolated values
    @rtype: AnimAtom
    """
    e = AnimTask(obj, atr, **argd)
    e.once(tm, func)
    return AnimAtom(e)

def Always(obj, atr, tm, p, v, **argd):
    """
    @return: a Task repeatedly set obj.atr with linear interpolated values
    @rtype: AnimAtom
    """
    e = AnimTask(obj, atr, **argd)
    e.always(tm, Linear(p, v))
    return AnimAtom(e)

def AlwaysEx(obj, atr, tm, func):
    """
    @param func: the mapping from time to value
    @return: a Task repeatedly set obj.atr by func.map(t)
    @rtype: AnimAtom
    """
    e = AnimTask(obj, atr)
    e.always(tm, func)
    return AnimAtom(e)

def print_Debug():
    """
    print what tasks, anim tasks are executing

    @rtype: None
    """
    print '--- AnimManager ---'
    print '--- tasks ---'
    for i in GetAnimManager().tasks:
        i.print_debug()
    print '-------------------'
    print '--- anim tasks ---'
    for i in GetAnimManager().animtasks:
        i.print_debug()
    print 'time', GetAnimManager().taketime
    print '-------------------'
    print '--- processingTasks ---'
    for i in GetAnimManager().processingTasks:
        i.print_debug()
    print '-------------------'

#########################################################
#
#   Object Declare
#
#########################################################

def HashPE(f, a):
    """
    make hash
    """
    try:
        hash((f, a))
        return (f, a), True
    except:
        return f, False

class Manager:
    """
    Animation Manager
    Manage a series of animation that acts simultaneously

    there are 3 category of animations it manages
        1. post event
        2. task
        3. animtask
    """
    # tasks, animtasks
    def __init__(self):
        self.lock = threading.Lock()
        # execute tasks
        self.tasks = []
        self.processingTasks = []
        self.noReadyTasks = []

        # UI anim task
        self.taketime = 0
        self.animtasks = []

        # post event
        self.posteventCritsec = threading.RLock()
        self.postevents = []
        self.posteventIdx = 0
        self.posteventCache = {}

    def add(self, t, **argd):
        """
        add a new task

        @type t: a Task object
        @rtype: None
        """
        if argd.get('startnow', False):
            t.start(koan.GetTime())
            self.tasks.append(t)
        else:
            self.noReadyTasks.append(t)

    def addAnim(self, t):
        """
        add a new animation task

        @type t: a Task object
        @rtype: None
        """
        self.animtasks.append(t)

    def addPostEvent(self, f, *a):
        """
        add a new post event

        @rtype: None
        """
        self.lock.acquire()        
        h, hashable = HashPE(f, a)
      
        if self.posteventCache.get(h) > 0:
            if hashable:
                self.lock.release()
                return
            if self.posteventIdx:
                if (f, a) in self.postevents[self.posteventIdx:]:
                    self.lock.release()
                    return
            else:
                if (f, a) in self.postevents:
                    self.lock.release()
                    return
            
            self.posteventCache[h] += 1
        else:
            self.posteventCache[h] = 1
        
        self.postevents.append((f, a))
        self.lock.release()

    def removeTask(self, t):
        """
        remove a task from tasks, animtasks, processingTasks

        @param t: the task to be removed
        @type t: a Task object
        @rtype: None
        """
        needResetTimer = False

        if t in self.tasks:
            self.tasks.remove(t)
            if getattr(t, 'timeResolution', 100) <> 100:
                needResetTimer = True

        if t in self.noReadyTasks:
            self.noReadyTasks.remove(t)
            if getattr(t, 'timeResolution', 100) <> 100:
                needResetTimer = True

        if t in self.processingTasks:
            self.processingTasks.remove(t)

        if t in self.animtasks:
            self.animtasks.remove(t)
            if getattr(t, 'timeResolution', 100) <> 100:
                needResetTimer = True

        if needResetTimer:
            PostEvent(self.ResetTimeResolution)

    def ResetTimeResolution(self):
        res = 100
        for t in self.tasks + self.noReadyTasks + self.animtasks:
            r = getattr(t, 'timeResolution', 100)
            if r < res:
                res = r
        if koan.dummy and koan.dummy._window:
            koan.dummy._window.SetTimeResolution(res)

    def cancel(self, obj, attr):
        """
        another method to remove a task

        @param obj: tasks that affect obj.attr will be removed
        @param attr: tasks that affect obj.attr will be removed
        @rtype: None
        """
        for i in self.tasks:
            if i._isYou(obj, attr):
                self.removeTask(i)

        for i in self.noReadyTasks:
            if i._isYou(obj, attr):
                self.removeTask(i)

        for i in self.animtasks:
            if i._isYou(obj, attr):
                self.removeTask(i)

        for i in self.processingTasks:
            if i._isYou(obj, attr):
                self.removeTask(i)

    def removeObj(self, obj):
        """
        the third method to remove a task

        @param obj: tasks that affect obj will be removed
        @rtype: None
        """
        for i in self.tasks:
            if i._getObject() == obj:
                self.removeTask(i)
        for i in self.animtasks:
            if i._getObject() == obj:
                self.removeTask(i)

    def executePostEvent(self):
        """
        execute post events in the queue, and then clean the queue

        @rtype: None
        """
        self.lock.acquire()
        while self.posteventIdx < len(self.postevents):# and not koan.dummy.ending:
            (f, a) = self.postevents[self.posteventIdx]
            self.posteventIdx += 1
            
            h, _h = HashPE(f, a)           
            self.posteventCache[h] -= 1
            '''
            try:
                self.posteventCache[h] -= 1
            except KeyError:
                traceback.print_exc()
                pass
            '''
            self.lock.release()
            if koan.isDebug:
                f(*a)
            else:
                try:
                    f(*a)
                except:
                    print '---- ignore exceptions ----'
                    traceback.print_exc()
            self.lock.acquire()

        self.posteventIdx = 0
        self.postevents = []
        self.posteventCache = {}
        self.lock.release()

    def executeAnimTasks(self):
        t0 = koan.GetTime()

        next = []
        t = koan.GetTime()
        for i in self.animtasks:
            if i.step(t):
                next.append(i)
        self.animtasks = next
        d = koan.GetTime() - t0
        if d > self.taketime:
            self.taketime = d

    def executeTasks(self):

        if self.processingTasks:
            self.tasks += self.processingTasks
            print '[koan.anim] processingTasks is not empty'
        self.processingTasks = self.tasks
        self.tasks = []

        #if koan.render:
        #    t0 = koan.render.GetRenderTime()
        #else:
        t0 = koan.GetTime()

        while self.processingTasks:
            e = self.processingTasks.pop()
            if e.step(t0):
                self.tasks.append(e)

    def fireExecuteTasks(self):
        #if koan.render:
        #    t0 = koan.render.GetRenderTime()
        #else:
        if self.noReadyTasks:
            t0 = koan.GetTime()
    
            for i in self.noReadyTasks:
                i.start(t0)
                self.tasks.append(i)
            self.noReadyTasks = []

    def pooling(self):
        self.executePostEvent()

        if koan.dummy and not koan.dummy.ending:
            self.executeTasks()
            self.executeAnimTasks()

        if all([not w.invalid for w in koan.windows]):
            # noone dirty, we still need to fire execute tasks
            koan.animManager.fireExecuteTasks()
            
    #def isIdle(self):
    #    return bool(self.noReadyTasks or self.processingTasks or self.tasks or self.animtasks or self.postevents)
        
class ExecuteTask:
    """
    to call a function once at a specified time or continuously
    """
    def __init__(self, t, action, **argd):
        """
        @param t: the task will be executed t(secs) later
        @type t: float
        @param action: the action to be executed
        @type action: an Action object
        """
        self.action = action
        self.duration = t
        self.renderTime = None
        self.executeTime = None

        self.always = False

        res = argd.get('timeResolution', 100)
        if res <> 100:
            self.timeResolution = res
            PostEvent(GetAnimManager().ResetTimeResolution)

    def close(self):
        self.always = False
        
    def print_debug(self):
        """
        @rtype: None
        """
        print self.action.callback

    def _isYou(self, obj, attr):
        """
        check if this task execute function "obj"

        @param obj: the function to be checked
        @param attr: not used(TODO: remove arg?)
        """
        return (obj == self.action.callback)

    def _getObject(self):
        """
        @return: the Action object associated with this task
        """
        return self.action

    def start(self, t0):
        self.renderTime = t0

    def step(self, t): # t is the renderer time
        """
        execute this task and check if it shall be executed next time

        @param t: the system time, if t > task execution time, this task were executed
        @return: if this task shall be excuted next time
        @rtype: boolean
        """
        if self.duration == 0:
            self.action()
            return self.always

        if self.executeTime == None:
            if self.renderTime == t:
                # still not start this task
                return True
            else:
                self.executeTime = t + self.duration

        if t >= self.executeTime:
            self.action()

            if self.always:
                self.executeTime += self.duration
                return True
            return False
        return True

class AnimTask:
    """
    to specify how a field value changed over time
    """
    def __init__(self, o, attr, **argd):
        """
        @param o: the target object to be manipulated
        @param attr: the target attribute to be manipulated
        """
        #assert False, 'anim.Task depreciated'
        self.obj = o
        self.attr = attr
        self.delay = 0
        self.autoCancel = True
        res = argd.get('timeResolution', 100)
        if res <> 100:
            self.timeResolution = res
            PostEvent(GetAnimManager().ResetTimeResolution)

    def close(self):
        pass
        
    def print_debug(self):
        print self.obj,
        self.mapping.print_debug()

    def _isYou(self, obj, attr):
        """
        check if this task affects obj.attr
        """
        return (self.obj is obj) and (self.attr == attr)

    def _getObject(self):
        return self.obj

    def __del__(self):
        self.cancel()

    def __set(self, tlen, mapping):
        """
        set the task's duration and relation between the changed field value and time

        @param tlen: the duration of this task
        @param mapping: the mapping from time to target field value
        """
        if self.autoCancel:
            GetAnimManager().cancel(self.obj, self.attr)

        if tlen == 0:
            raise ValueError

        self.mapping = mapping

        self.isContinue = True
        self.len = tlen
        self.beginTime = koan.GetTime() + self.delay
        koan.animManager.addAnim(self)

    def cancel(self):
        """
        cancel this task from animManager
        """
        if koan.animManager:
            koan.animManager.removeTask(self)

    def always(self, tlen, m):
        """
        set that this task shall execute once

        @param tlen: duration of this task
        @param m: the mapping of time -> value
        """
        self.__set(tlen, m)
        self.isContinue = True

    def once(self, tlen, m):
        """
        set that this task shall execute once

        @param tlen: duration of this task
        @param m: the mapping of time -> value
        """
        self.__set(tlen, m)
        self.isContinue = False

    def step(self, t):
        """
        execute this task -- set the target field by time

        @return: if this task shall execute next time
        """
        if self.beginTime > t: # it is a delay anim
            return True

        o = self.obj
        if self.isContinue:
            if t > self.beginTime + self.len:
                self.beginTime = self.beginTime + ((t - self.beginTime) // self.len) * self.len
        else:
            if t > self.beginTime + self.len:
                self.__setLastValue()
                return False

        prec = float(t - self.beginTime) / float(self.len)

        try:
            v = self.mapping.map(prec)
            setattr(self.obj, self.attr, v)
        except:
            pass
        return True

    def __setLastValue(self):
        v = self.mapping.map(1.0)
        setattr(self.obj, self.attr, v)

koan.optimize(AnimTask.step)

#########################################################
#
#   Test This Module
#
#########################################################

if __name__ == '__main__':
    # TODO: this unit test is outdated
    #Init()

    class C:
        pass;
    class B:
        def __init__(self):
            self.c = C()
            self.c.str = 'Hello World'
            def fun(s):
                print s.str
            GetAnimManager().execute(1, fun, self.c)
            c = C()
            self.c.str = 'Hello World 2'

    b = B()
    b = None
    GetAnimManager().pooling()
    #Destory()
