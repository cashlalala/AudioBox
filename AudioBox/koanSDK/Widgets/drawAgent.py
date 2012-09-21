import koan
from koan.event import EventManager
from kxmlparser import XNode, XAnim, XDrawPass, XDrawAgent
from koan.anim import AnimLinear, AnimSpring, AnimTarget
from weakref import ref
   
def ApplyRes(render, src):
    try:
        gamma = render.localOpt['gamma']
    except:
        try:
            gamma = render.globalOpt['gamma']
        except:
            gamma = None
    t = render.GetTexture(src, gamma = gamma)
    render.SetTexture(t)

def PutArgs(render, arg):
    render.curArgs = arg

def ExecuteFunction(render, func, arg, num):
    if num >= len(render.curArgs):
        raise ValueError, "index out of range"
    render.curArgs[num] = func(*arg)

def ApplyEnvs(render, name, num):
    if num >= len(render.curArgs):
        raise ValueError, "index out of range"
    if name in render.localOpt:
        render.curArgs[num] = render.localOpt[name]
    elif name in render.globalOpt:
        render.curArgs[num] = render.globalOpt[name]
    else:
        raise ValueError, "not such environment:" + name

def ApplyAnims(render, name, num):
    if num >= len(render.curArgs):
        raise ValueError, "index out of range"
    if name in render.anims:
        render.curArgs[num] = render.anims[name]
    else:
        raise ValueError, "not such anim:" + name

    
#----------------------------------------------------------------
# DrawAgent
#----------------------------------------------------------------
class DrawAgentBasic:
    def __init__(self, xnode, render, opt):
        if not hasattr(render, 'attachedDrawAgent'):
            render.attachedDrawAgent = True
            render.ApplyRes = koan.Action(ApplyRes, render)
            render.PutArgs = koan.Action(PutArgs, render)
            render.ExecuteFunction = koan.Action(ExecuteFunction, render)
            render.ApplyEnvs = koan.Action(ApplyEnvs, render)
            render.ApplyAnims = koan.Action(ApplyAnims, render)

        self.opt = opt
        self.define = xnode.define
        self.calls = xnode.calls

    def callFunc(self, c):
        if c not in self.define:
            raise ValueError, "no such call function:" + c
        
        fname, _args = self.calls[c]
        
        if fname not in self.define or self.define[fname][0] <> 'f':
            raise ValueError, fname + " is not well defined"
            
        f = self.define[fname][1]
        args = [transf(i) for i in _args]
        
        return f(*args)

    def trans(self, v):
        t, v = v
        if t == '$':
            return self.opt[v]
        elif t == 'c':
            return self.callFunc(c)
        elif t == 'a':
            return self.anims[v]
        return v
        
    def createAnim(self, xagent, render, anim):
        
        ret = [] # name, global, anim
        isglobal = (self.trans(anim.scope).lower() == 'global')
    
        if anim.method == 'linear':
            
            dur = float(self.trans(anim.dur))
            loop = (self.trans(anim.loop).lower() == 'true')
            segment = []
            for i in anim.segment:
                segment.append(float(self.trans(i)))
        
            for name, value in anim.target:
                v = []
                for i in value:
                    v.append(float(self.trans(i)))
            
                if isglobal and xagent:
                    if name in xagent.globalAnims:
                        a = xagent.globalAnims[name]
                    else:
                        a = AnimLinear(dur, segment, v, loop = loop)
                        xagent.globalAnims[name] = a
                else:
                    a = AnimLinear(dur, segment, v, loop = loop)
                
                ret.append((name, isglobal, a))
                pass
        elif anim.method == 'target':
            type = self.trans(anim.type).lower().encode()
            
            for name, value in anim.target:
                
                v = float(self.trans(value[0]))
                
                if isglobal and xagent:
                    if name in xagent.globalAnims:
                        a = xagent.globalAnims[name]
                    else:
                        a = AnimTarget(type, 0, v, v, None)
                        xagent.globalAnims[name] = a
                else:
                    a = AnimTarget(type, 0, v, v, None)
                    
                ret.append((name, isglobal, a))
                pass
            
                
        return ret
                
class DrawAgent(EventManager, DrawAgentBasic):
    def __init__(self, dirtyTarget, xagent, render, opt = {}):
        
        EventManager.__init__(self)
        DrawAgentBasic.__init__(self, xagent, render, opt)
        
        render.globalOpt = opt
        render.localOpt = {}
        render.define = xagent.define
    
        self.xagent = xagent
        self.passes = []
        self.passname = {}
        self.opt = opt
        self.dirtyTarget = None
        self.define = xagent.define
        
        if dirtyTarget:
            self.dirtyTarget = ref(dirtyTarget)
                
        self.width = float(self.trans(xagent.width))
        self.height = float(self.trans(xagent.height))
        self.fit = self.trans(xagent.fit)
        
        self.anims = {}
        self.localanim = []
        self.passlist = [i.strip() for i in xagent.default.split(',')]
        self.waitNext = False

        # create global anim
        for i in xagent.anims:
            r = self.createAnim(self.xagent, render, i)
            for name, isglobal, anim in r:
                self.anims[name] = anim
                if not isglobal:
                    self.localanim.append(anim)
            pass
        
        for i in xagent.passes:
            self.passes.append(DrawPass(self, i, render, opt))
            self.passname[self.passes[-1].name] = self.passes[-1]
        
        self._apply([i.strip() for i in xagent.default.split(',')])
        
        render.globalOpt = {}
        render.localOpt = {}
        render.define = {}
        
    def makeTargetDirty(self):
        if not self.dirtyTarget:
            return
            
        o = self.dirtyTarget()
        if not o:
            return
        
        o.dirty = True
            
    def apply(self, passlist):
        if len(passlist) == 0:
            return
            
        if len(passlist) > 1:
            front, end = passlist[:-1], passlist[-1]
        else:
            front = []
            end = passlist[0]
        
        p = self.passname[end]
        if p.dur:
            front.append(end)
            end = None
        
        if end:
            if self.passlist:
                p = self.passname[self.passlist[-1]]
                if p.dur == 0: # this is a static state
                    self.passlist = self.passlist[:-1]        
            end = [end]
        else:
            end = []
        
        if self.waitNext:
            passF, passE = self.passlist[:1], self.passlist[1:]
            self.passlist = passF + front + passE + end
        else:
            self._apply(front + self.passlist + end)

    def doNextPass(self):
        self.waitNext = False
        self._apply(self.passlist[1:])

    def _apply(self, passlist):
        koan.anim.Cancel(self.doNextPass)
        
        self.passlist = passlist
        if not self.passlist:
            return
            
        top = self.passlist[0]
        
        if top not in self.passname:
            raise ValueError, top + " is not a valid pass name"
        
        self.makeTargetDirty()
        p = self.passname[top]
        p.resetAnim()
        
        if p.dur:
            self.waitNext = True
            koan.anim.Execute(p.dur, self.doNextPass)
                
    def draw(self, render, w, h, opt = {}):
        if not self.passlist:
            return

        top = self.passlist[0]
        
        if not self.passname.has_key(top):
            return
        
        if self.fit == 'scale':
        
            render.PushMatrix()
            if w != self.width or h != self.height:
                render.Scale(float(w) / self.width, float(h) / self.height)
                  
            self.passname[top].draw(render, opt)
            render.PopMatrix()
            
        elif self.fit == 'native':
            self.passname[top].draw(render, opt)
            
#----------------------------------------------------------------
# Draw Widgets
#----------------------------------------------------------------

class DrawPass(DrawAgentBasic):
    def __init__(self, drawagent, xdrawpass, render, opt = {}):
    
        DrawAgentBasic.__init__(self, xdrawpass, render, opt)
    
        self.xdrawpass = xdrawpass
        #self.drawagent = drawagent
    
        self.name = xdrawpass.name
        self.cmd = xdrawpass.cmd      # ex: ['DrawRect', 'Translate', 'PushAlpha']
        self.args = xdrawpass.args       # ex: [[0, 0, 100, 100], [0, linear(1, (0, 0.1,  1), (0, 100, 0))], [0.5]]

        self.anims = {}
        self.anims.update(drawagent.anims) # merge parent
        self.localanim = []
        
        self.dur = float(self.trans(xdrawpass.dur))
        
        # create anim
        for i in xdrawpass.anims:
            r = self.createAnim(None, render, i)
            for name, isglobal, anim in r:
                self.anims[name] = anim
                self.localanim.append(anim)
                if isglobal:
                    raise ValueError, "only accept local anim"
            pass

    def resetAnim(self):
        self.dur = float(self.trans(self.xdrawpass.dur))
        for n, d, v in self.xdrawpass.targets:
            a = self.trans(n)
            d = float(self.trans(d))
            v = float(self.trans(v))
            a.Reset(d, v)
    
        for j in self.localanim:
            if isinstance(j, AnimLinear):
                j.Reset()
                
    def draw(self, render, opt):
        render.globalOpt = self.opt
        render.localOpt = opt
        render.anims = self.anims
        
        if len(self.args) == len(self.cmd):
            for i in range(0, len(self.cmd)):
                f = getattr(render, self.cmd[i], None)
                f(*self.args[i])
        else:
            print 'commands and arguments are not match'

        render.globalOpt = {}
        render.localOpt = {}
        render.anims = {}