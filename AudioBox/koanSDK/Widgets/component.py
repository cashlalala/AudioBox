"""
the component module

Component class is the base class for all visible Objects in koan

@undocumented: deadPeople, recursiveWalkComponent, Component_closeagain
"""

import koan
assert float(koan.version) >= 4.0
import gc
import traceback
from weakref import ref
import color
from koan.rectangle import Rectangle
from koan.event import EventManager
from koan.texmng import StringTextureManager

def Intersect2(a, b):
    right = min(a[0] + a[2], b[0] + b[2])
    bottom = min(a[1] + a[3], b[1] + b[3])
    left = max(a[0], b[0])
    top = max(a[1], b[1])

    return left, top, right - left, bottom - top

def Intersect(a, b):
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    left = max(a[0], b[0])
    top = max(a[1], b[1])

    return left, top, right, bottom
    
def clamp(min_v, v, max_v):
    return max( min_v, min(v, max_v) )

def recursiveWalkComponent(node, func):
    """
    recursively walk the component and it's children and perform func on each component
    """
    func(node)
    map(lambda c: recursiveWalkComponent(c, func), node._children)

def Component_closeagain(v):
    print 'second close Warring:', v

# --------------------------------------------------------
# This is used for detecting koan component leaks
# --------------------------------------------------------
deadPeople = {}

def ClearLeakRecord():
    global deadPeople
    deadPeople = {}

def DetectLeak():
    if not koan.isDebug:
        return

    gc.collect()

    print 'start DetectLeak ---------------------'

    for i in gc.get_objects():
        try:
            hv = id(i)
        except:
            continue
        if deadPeople.has_key(hv):
            if str(i) == str(deadPeople[hv]):
                if i in gc.garbage:
                    print '  Leak:', i
                else:
                    print 'Zonbie:', i
    print 'end DetectLeak    --------------------'
    
#-----------------------------------------------------------------------
# TraceObject
#-----------------------------------------------------------------------
class TraceObject:
    __traverse_level = 0
    def __init__(self):
        assert isinstance(self, Component)

    @staticmethod
    def getDebugString(node, *argv, **argd):
        """
        """
        obj_desc = str(node)[1:-1].split(' ')
        try:
            if not argd['fullname']:
                obj = obj_desc[0].split('.')[-1]
        except:
            obj = obj_desc[0]
        
        try:
            if argd['id']:
                obj += ' ' + obj_desc[-1]
        except:
            pass

        args = ''
        for i in argv:
            try:
                args += (' ' + i.split(':')[-1] + ':' + str(eval("node.%s" %(i.split(':')[0]))))
            except:
                pass
        return obj, args
        
    @staticmethod
    def trace_back(node, *argv, **argd):
        """
        traceback( 'rect:r',
                   'visible:v',
                   'focus:f',
                   'focusChild:fc'
                   id = False,
                   fullname = False    )
        """
        obj, args = TraceObject.getDebugString(node, *argv, **argd)
        print "%s%s" %(obj, args)
        if node.parent:
            TraceObject.trace_back(node.parent, *argv, **argd)
    
    @staticmethod
    def trace_tree(node, *argv, **argd):
        """
        tracetree( 'rect:r',
                   'visible:v',
                   'focus:f',
                   'focusChild:fc'
                   id = False,
                   fullname = False    )
        """
        obj, args = TraceObject.getDebugString(node, *argv, **argd)
    
        print "  " * TraceObject.__traverse_level + "%s%s" %(obj, args)
        TraceObject.__traverse_level += 1
        for c in node.children:
            TraceObject.trace_tree(c, *argv, **argd)
        TraceObject.__traverse_level -= 1
    
    def trace(self, *argv, **argd):
        print '======================== trace tree =========================='
        TraceObject.trace_tree(self, *argv, **argd)
        print '=============================================================='

    def traceback(self, *argv, **argd):
        print '======================== trace back =========================='
        TraceObject.trace_back(self, *argv, **argd)
        print '=============================================================='


import new
#-----------------------------------------------------------------------
# ScriptObject
#-----------------------------------------------------------------------
class ScriptObject:
    def __init__(self):
        self.__pyscripts = set()
        
    @staticmethod
    def compilePyScripts(script):
        # defer 'import inspect', which costs about 0.04s
        import inspect
        #-------------------------------------------
        # indent scripts
        #-------------------------------------------
        lines = script.splitlines()
        i = 0
        for line in lines:
            if line.strip() != '':
                break
            i+=1
        if len(lines):
            indent = lines[i].rfind(lines[i].lstrip())
            formatdata = ''
            for line in lines:
                if line.strip():
                    line = line[indent:]
                    formatdata += (line + '\n')
            #print formatdata
            script = formatdata
        else:
            script = ''
    
        #-------------------------------------------
        # compile scripts
        #-------------------------------------------
        c = compile(script, '<string>', 'exec')
        exec c
        x = None
        funcs = [locals()[x] for x in locals() if inspect.isfunction(locals()[x])]
        return funcs

    def addScripts(self, func):
        setattr(self, func.__name__, new.instancemethod(func, self, self.__class__))  # circular reference
        self.__pyscripts.add(func.__name__)

    def free(self):
        # cut off circular reference caused by instancemethod
        for f in self.__pyscripts:
            delattr(self, f)


#-----------------------------------------------------------------------------
# KXMLObject
#-----------------------------------------------------------------------------
import re
class KXMLObject:
    #--------------------------------------
    # {Button text = '${Text text = "click"}'}
    #--------------------------------------
    markup_extension = re.compile('^\${([^}]+)}')
    #--------------------------------------
    # (*parent.width)     the same to:  <-(parent.width)
    # (->parent.width)
    # (=parent.width)
    #--------------------------------------
    data_bind = re.compile('([^()])\(([^)]+)\)$')
    
    symb_changeevent = '@'
    symb_postevent = '^'
    symb_sync = '~'
    symb_command = '$'

    def __init__(self):
        assert isinstance(self, Component)

    def applyStyle(self, style):
        if style:
            for name in style.sets:
                self.setAttribute(name, style.sets[name], macro = style.macro)
                
            for cmd in style.cmds:
                prop = {
                    'name': cmd[0],
                    'attrs': cmd[1],
                    'data': cmd[2]
                }
                self.setCommandProperty(prop, macro = style.macro)
    
            for cmdObj in style.cmdObjs:
                cmdObj.applyCommand(self, macro = style.macro)
            
    def setContent(self, data):
        pass
    
    def setNameAttribute(self, name, obj):
        if not hasattr(self, name):
            setattr(self, name, obj)
        else:
            print '[KXML] (%s) already has (%s)property !!!' %(self, name)
            
    def setAttribute(self, name, strValue, **keyword):
        if not keyword.get('force', False) and not hasattr(self, name):
            print '[KXML] component(%s) has no such attribute(%s)!!!' %(self.__class__, name)
            return
            
        strValue = strValue.strip()
        if strValue.startswith('${'):
            #---------------------------------------------------------------------
            # <Button text = '${Text text = "Click" color = "red"}'/>
            # <Dialog beginEffect = '${DrawAgent name="Flip3D_begin" file="dialoganim.xml"}'/>
            #---------------------------------------------------------------------
            ret = KXMLObject.markup_extension.match(strValue)
            toks = ret.groups()[0].split(' ')
            if toks[0].lower() == 'drawagent':
                attrs = {}
                for i in toks[1:]:
                    n, v = i.split('=')
                    attrs[n] = eval(v)
                from kxmlparser import loadDrawAgent
                agents = loadDrawAgent(attrs['file'])
                if not agents:
                    return
                value = agents.createAgent(self, attrs['name'], self.__dict__)
            else:
                return
            #print '[KXMLObject] Makrup Extension: To do ............... !!!'
        elif strValue.startswith('*('):
            #---------------------------------------------------------------------
            #<DockPanel width = '*(parent.width)'/>
            #---------------------------------------------------------------------
            ret = KXMLObject.data_bind.match(strValue)
            try:
                src = 'self.'+name
                sep, tar = ret.groups()
                if '.' not in tar:
                    tar = 'self.' + tar.strip()
                if sep == '*':
                    sep = '<-'
                self.dataBinding(src, tar, keyword.get('parser', koan.Null).root, dir = sep)                
            except:
                traceback.print_exc()
                print '[KXML] bind: Unknown binding (%s) !!!' %(data)
            return
        #elif strValue.startswith():
        else:
            try:
                parser = keyword.get('parser', None)
                try:
                    t = type(self.__dict__[name])
                    if t is str:
                        #---------------------------------------------
                        # <Text text = 'Hello World'/>
                        #---------------------------------------------
                        value = str(strValue)
                    elif t is unicode:
                        value = unicode(strValue)
                    else:
                        # other type
                        raise AttributeError

                    if len(value) > 3 and value[:2] == '_(' and value[-1] == ')' and parser:
                        value = parser.trans(value[2:-1])
                except:
                    #---------------------------------------------
                    # <Button color = '(255, 255, 255, 255)'/>
                    #---------------------------------------------                    
                    try:
                        #keyword.update({'yellow':color.yellow, 'green':color.green})
                        value = eval(strValue, keyword)
                    except:
                        #---------------------------------------------                    
                        # <x:macro>
                        #   LEFT -> 100 |
                        #   TOP -> 100
                        # </x:macro>
                        if parser:
                            value = parser.queryMacroValue(strValue)
                        else:
                            value = eval(strValue, keyword['macro'])
            except:
                print "[KXML] set %s property(%s) error !!! value is %s" % (self, name, strValue)
                traceback.print_exc()
                return
                
        setattr(self, name, value)
        pass

    def setElementProperty(self, prop, **keyword):
        name = prop['name'].split('.')[-1]
        if prop.has_key('objects'):
            #------------------------------------------------------------
            # <Panel.btn>    <------ element property, not control !!!
            #   <Button/>
            # </Panel.btn>
            #
            # <Dialog.clients>
            #   <Button/>
            #   <Button/>
            #   <Button/>
            # </Dialog.clients>
            #------------------------------------------------------------            
            for o in prop['objects']:
                o.close()
            print '[KXML] Do not support setElementProperty with object !!!'
            return
            
            assert len(prop['objects']) > 0
            if len(prop['objects']) > 1:
                print '[KXML] %s do not support multiple child !!!' %prop['name']
                for o in prop['objects'][1:]:
                    o.close()
            setattr(self, name, prop['objects'][0])   # cause leak, need to be solved
        else:
            # <Text.text> Hello World </Text.text>
            self.setAttribute(name, prop['data'].strip(), **keyword)

    def setAttachedProperty(self, prop, **argd):
        pass

    def setCommandProperty(self, prop, **keyword):
        name = prop['name'].lower()
        data = prop['data']
        name = name.lower()
        if name == 'pyscript':
            #-------------------------------------------
            # compile PyScript
            #-------------------------------------------
            funcs = ScriptObject.compilePyScripts(data)

            #-------------------------------------------
            # set PyScript to object
            #-------------------------------------------
            map(lambda f: self.addScripts(f), funcs)

        elif name == 'binddata':
            #-------------------------------------------
            # data binding
            #-------------------------------------------
            try:
                bindings = data.split('|')
                # <x:bindData>
                #   self.width -> parent.width |
                #   self.width <- parent.width |
                #   self.width = parent.width
                # </x:bindData>
                for binding in bindings:
                    if '->' in binding:    sep = '->'
                    elif '<-' in binding:  sep = '<-'
                    elif '=' in binding:   sep = '='
                    else:               raise 'Unknown sep'

                    src, tar = binding.split(sep)
                    if '.' not in src:
                        src = 'self.' + src.strip()
                    if '.' not in tar:
                        tar = 'self.' + tar.strip()
                    self.dataBinding(src, tar, prop['root'], dir = sep)
            except:
                traceback.print_exc()
                print '[KXML] bind: Unknown data binding (%s) !!!' %(data)
                
        elif name == 'bind' or name == 'bindevent':
            #-------------------------------------------
            # event binding
            #-------------------------------------------
            try:
                # <x:bindEvent> Click -> onClick </x:bindEvent>
                # <x:bindEvent> Click -> onClick | Mouse Enter -> onMouseEnter </x:bindEvent>
                bindings = data.split('|')
                for binding in bindings:
                    evt, act = binding.split('->')
                    self.eventBinding(evt, act, prop['root'])
            except:
                traceback.print_exc()
                print '[KXML] bind: Unknown event binding (%s) !!!' %(data)
        elif name == 'call':
            #-------------------------------------------
            # <x:call func = 'onInit'/>
            # <x:call func = 'onInit' args = '(10, 20),'/>
            # <x:call func = 'onInit' args = 'True, 100, False'/>
            #-------------------------------------------
            try:
                attrs = prop['attrs']
                func = attrs.getValueByQName('func').strip()
                try:
                    args = attrs.getValueByQName('args').strip()
                    args = eval(args)
                except:
                    args = ()
                call = self.getPathObject(func.split('.'), prop['root'])
                if call:
                    call(*args)
            except:
                traceback.print_exc()
                print '[KXML] call: Unknown call method !!!'
        
        elif name == 'invoke':
            #-------------------------------------------
            # <x:invoke event = 'Click'/>
            # <x:invoke event = 'Click' args = '(10, 20),'/>
            # <x:invoke event = 'Click' args = 'True, 100, False'/>
            #-------------------------------------------
            try:
                attrs = prop['attrs']
                evt = attrs.getValueByQName('event').strip()
                try:
                    args = attrs.getValueByQName('args').strip()
                    args = eval(args)
                except:
                    args = ()
                self.invoke(evt, *args)
            except:
                traceback.print_exc()
                print '[KXML] invoke: Unknown invoke event or args !!!'
                
        elif name == 'set':
            #-------------------------------------------
            # <x:set background = 'media\Root_help.png' bgColor = 'red'/>
            #-------------------------------------------
            try:
                attrs = prop['attrs']
                for n in attrs.keys():
                    self.setAttribute(n[1], attrs[n], **keyword)
            except:
                traceback.print_exc()
                print '[KXML] set: Unknown set (%s) !!!' %(data.strip())

        elif name == 'init':
            #-------------------------------------------
            #<XmlRefObject path = 'library.xml' x:init = 'maxWidth = 300'/>
            #-------------------------------------------
            for expression in data.split('|'):
                name, value = expression.split('=')
                self.setAttribute(name.strip(), value.strip(), force = True, **keyword)
        elif name == 'trigger':
            pass

        elif name == 'focus':
            koan.anim.PostEvent(self.setFocus)
            
        elif name == 'accelerator':
            #-------------------------------------------
            # define commands
            #-------------------------------------------
            try:
                '''
                <x:accelerator>
                    Close:              ALT F4 |
                    Undo:               CTRL Z |
                    Redo:               CTRL Y |
                    Cut:                CTRL X |
                    Copy:               CTRL C |
                    Paste:              CTRL V |
                    Help:               F1 |
                    Toggle Fullscreen:  ALT ENTER,, ALT SHIFT ENTER,, F12
                </x:accelerator>
                '''
                cmd_maps = data.split('|')
                self.keymaps = {}
                for cmd_map in cmd_maps:
                    cmd, keys = cmd_map.split(':')
                    keys = keys.split(',,')

                    cmd = cmd.strip()
                    for key in keys:
                        key = key.strip()
                        key = key.replace('SPACE', ' ')
                        
                        if key not in self.keymaps:
                            self.keymaps[key] = []                        
                        self.keymaps[key].append('<'+cmd+'>')
            except:
                traceback.print_exc()
                print '[KXML] commands: Unknown commands mapping (%s) !!!' %(data)
            pass    

    def getPathObject(self, full_path, root):
        first = full_path[0].lower()
        if first == 'root':             # Ex: root.onClick
            obj = root
            name_path = full_path[1:]
        elif first == 'parent':         # Ex: parent.onClick
            obj = self.parent
            name_path = full_path[1:]
        elif first == 'self':           # Ex: self.onClick
            name_path = full_path[1:]
            obj = self
        else:                           # Ex: onClick
            name_path = full_path
            obj = self
        #-----------------------------------
        # trace the whole path
        # Ex:
        # root.panel.menu.onClick
        #-----------------------------------
        try:
            for tar in name_path:
                obj = getattr(obj, tar)
            return obj
        except:
            print '[component.py] can not find the object in the path(%s) !!!' %full_path
            return None

    def dataBinding(self, left, right, root, **argd):
        left = left.strip().split('.')
        right = right.strip().split('.')
        try:
            left_obj = self.getPathObject(left[:-1], root)
            right_obj = self.getPathObject(right[:-1], root)
        except AttributeError:
            print '[KXML] bind: No data (%s or %s) !!!' %(left, right)
        else:
            left_obj.bindData(left[-1], right_obj, right[-1], **argd)
            
    def eventBinding(self, evt, act, root):
        binding = 2  # 0: changevent, 1: comamnd , 2: event
        post = True
        evt = evt.strip()
        act = act.strip()
        #---------------------------------------------------
        # check if this event is not postevent
        #---------------------------------------------------
        if evt.startswith(KXMLObject.symb_changeevent):         # @isMouseOver -> onMouseOverChange
            evt = evt[1:]
            binding = 0
            sync = True
        elif evt.startswith(KXMLObject.symb_command):           # $New -> onMouseOverChange
            evt = evt[1:]
            binding = 1

        if act.startswith(KXMLObject.symb_postevent):           # Click -> ^onClick
            act = act[1:]
            post = False
        if binding == 0 and KXMLObject.symb_sync in act[0:2]:   # @isMouseOver -> ^~onMouseOverChange
            act = act.strip(KXMLObject.symb_sync)
            sync = False

        try:
            invoker = self
            evts = evt.split('.')
            if len(evts) > 1:               # root.xxx.Click -> onClick
                invoker = self.getPathObject(evts[:-1], root)
                evt = evts[-1]
            
            receiver = self
            acts = act.split('.')
            if len(acts) > 1:
                receiver = self.getPathObject(acts[:-1], root)
            func = getattr(receiver, acts[-1])
        except AttributeError:
            print '[KXML] bind: No callback function (%s) !!!' %(act)
        else:
            if binding == 0:
                receiver.autoRemove( invoker.changeEvent(evt, func, postevent = post, sync = sync) )
            elif binding == 1:
                receiver.autoRemove( invoker.bindCmd(evt, func, postevent = post) )
            else:
                receiver.autoRemove( invoker.bind(evt, func, postevent = post) )

# --------------------------------------------------------
# CaptureObject
# --------------------------------------------------------
class CaptureObject:
    '''
    Event:
        - Capture Begin (x, y)
        - Capture End (x, y)
        - Capture Offset (x, y)
    Overwritable:
        - captureTest()
    '''
    def __init__(self):
        assert isinstance(self, Component)
        self.__capture = False                  # has been captured
        self.__cap_x, self.__cap_y = 0, 0       # capture starting position
        
        # property
        self.useGlobalCapture = False
        
        self.bind('Mouse Down', self.__onCapture, True, postevent = False)
        self.bind('Mouse Up', self.__onCapture, False, postevent = False)
        self.bind('Mouse Move', self.__onCaptureMove, postevent = False)

    def captureTest(self, x, y):
        return self.hitTest(x, y)

    def __onCapture(self, cap, x, y, flag):        
        if self.__capture == cap:               # if already captured, return directly
            return
        if cap and not self.captureTest(x, y):  # not in capture region
            return
            
        self.__capture = cap
        #print '[CaptureObject] capture %s' %(str(self.__capture))
        self.setCapture(cap)
        if self.useGlobalCapture:
            x, y = self.local2global(x, y)
        self.__cap_x, self.__cap_y = x, y
        if self.parent:
            if self.__capture:
                self.invoke('Capture Begin', x, y)
            else:
                self.invoke('Capture End', x, y)

    def __onCaptureMove(self, x, y, flag):
        if self.parent and self.__capture:
            if self.useGlobalCapture:
                x, y = self.local2global(x, y)
            self.invoke('Capture Offset', x - self.__cap_x, y - self.__cap_y)

#----------------------------------------------------------------------------
# DragDropObject
#----------------------------------------------------------------------------
class DragDropObject:
    def __init__(self):
        assert isinstance(self, Component)
        self.__isDragOver = False
        
        # property
        self.dropMode = 'ole'               # dropMode == 'koan' for dragdrop python object
                                            # dropMode == 'ole' for dragdrop ole object
        self.canAcceptDropFiles = False     # can accept drop files?
        self.canDragFiles = False           # can drag files out?
        self.__isFirstMouseDown = False
        self.__mouseClickPt = 0, 0
        #self.bind('Mouse Down', self.onPrepareStartDrag, postevent = False)
        self.bind('Mouse Down', self.__onMouseDown)
        self.bind('Mouse Up', self.__onMouseUp)
        self.bind('Mouse Move', self.__onMouseMove)

    def __onMouseDown(self, x, y, flag): 
        self.__isFirstMouseDown = True
        self.__mouseClickPt = x, y

    def __onMouseUp(self, *arg):
        self.__isFirstMouseDown = False

    def __onMouseMove(self, x, y, flag):
        if self.__isFirstMouseDown:
            clickx, clicky = self.__mouseClickPt
            self.onPrepareStartDrag(clickx, clicky, flag)
            self.__isFirstMouseDown = False

    def onPrepareStartDrag(self, x, y, flags):
        if self.canDragFiles:
            #print '[component.py] onPrepareStartDrag'
            #pnt = self.calGlobalPoint(x, y)
            pnt = self.local2global(x, y)
            self.window.prepareDragDrop(pnt[0], pnt[1], self)

    def onQueryDrop(self, x, y):
        """
        drop query (for koan mode)
        """
        if self.canAcceptDropFiles and len(self.window.dropFiles):
            self.window.setCursor('drop')
            #print '[component.py] onQueryDrop', self.__class__
        else:
            self.window.setCursor('query')
            pass

    def onQueryDropEffect(self, x, y):
        """
        pass query drop effect (for ole mode)
        @rtype: 0: None, 1:Copy, 2:Move
        """
        # for OLE drop query
        if self.canAcceptDropFiles:
            return 1
        else:
            return 0

    def onDropFiles(self, x, y, files):
        if self.canAcceptDropFiles:
            self.fire('Drop Files', x, y, files)

    def passQueryDrop(self, x, y, state, *arg):
        """
        pass query drop message to children, and then process the query message

        @rtype: True if mouse over myself or one of my children
        """
        if not self.visible:
            return False

        dragOver = False
        
        if not dragOver:
            dragOver = self.hitTest(x, y)

        if self.__isDragOver:
            if not dragOver: # the mouse leave the component
                self.__isDragOver = False
                self.invoke('Drag Leave')
        else:
            if dragOver:
                self.__isDragOver = True
                self.invoke('Drag Enter')

        for c in self.children[::-1]:
            if c.visible and not c.blind:
                ptx, pty = c.parent2local(x, y)
                ret = c.passQueryDrop(ptx, pty, state, *arg)
                if ret:
                    return ret
        if dragOver:
            # in drag state, we still need to maintain mouse over state
            if Component.mouseOver <> self:
                if Component.mouseOver:
                    Component.mouseOver.isMouseOver = False
                    Component.mouseOver.invoke('Mouse Leave')
                    print 'MouseLeave drag', Component.mouseOver
                Component.mouseOver = self
                self.isMouseOver = True
                self.invoke('Mouse Enter')
                print 'MouseEnter drag', Component.mouseOver
        
            if state == 'QUERY':
                self.onQueryDrop(x, y)
            elif state == 'QUERYEX':
                return self.onQueryDropEffect(x, y)
            elif state == 'DROP':
                self.onDropFiles(x, y, *arg)
                self.__isDragOver = False
            return True
        else:
            return False


# --------------------------------------------------------
# ClickBase
# --------------------------------------------------------
class ClickBase:
    '''
    Event:
        - Click
    '''
    def __init__(self):
        assert isinstance(self, Component)
        self.bind('Mouse Up', self.__onMouseUp, postevent = False)

    def __onMouseUp(self, x, y, arg):
        if self.hitTest(x, y):
            self.invoke('Click')

#----------------------------------------------------------------------------
# Component
#----------------------------------------------------------------------------
class Component(Rectangle, EventManager, ClickBase, KXMLObject, ScriptObject, TraceObject, DragDropObject):
    """
    the visible component
    base class for all visible objects in koan

    Event:
        - Focus Dir(Hint)
        - Focus Change
        - Focus Child Change
        - Visible Change(v)
        - Child Visible Change(v)
        - Enable Change
        - Parent Change
        - Size Change
        - Parent Size Change
        - Child Size Change
        - Position Change
        - Parent Position Change
        - Child Position Change
        - Puncture Change
        - Close
        - Child Add (added_children)
        - Child Remove (removed_children)
        - Key
        - Mouse Down(x, y, *args)
        - Mouse Up(x, y, *args)
        - Mouse RDown(x, y, *args)
        - Mouse RUp(x, y, *args)
        - Dbl Click(x, y, *args)  (double click)
        - RDbl Click(x, y, *args)
        - Set Drop Files
        - Drop Files
        - Drag Enter
        - Drag Leave
        - Click
        - Mouse Enter
        - Mouse Leave
        - Mouse Move (x, y, flag)

    Command:
        
        
    Overwritable:
        - show()
        - hide()
        - close()
        - onDraw()


    @group Query Functions: getChildName, currentState, calGlobalRect, calGlobalPoint, isVisible,
         isFocused, convertCoord2Local, hitTest
    @group Overridable Functions: onKey, onCommand, onDraw
    """
    mouseOver = None
    mouseDownIn = None
    mouseRDownIn = None
    mousePreDown = ref(koan.Null)
    mouseCapture = None
    mouseDblClk = False
    tabStopObj = None

    def __init__(self, parent = None):
        """
        @param parent: the parent of this component
        @type parent: a Component object
        """
        Rectangle.__init__(self)
        EventManager.__init__(self)
        ClickBase.__init__(self)
        KXMLObject.__init__(self)
        ScriptObject.__init__(self)
        TraceObject.__init__(self)
        DragDropObject.__init__(self)

        self._parent = None
        self._children = []
        self._root = None
        self.parent = parent        

        # state
        self.enabled = True
        self.isMouseOver = False # care it
        self.visible = True
        self.focusChild = None
        self.blind = False
        self.clip = True               # if clip is True, all child will be clipped in local area  
        self.focus = self.isFocused()        
        self.bind('Focus Change', self.__onFocusChange, postevent = False)
        self.tabStop = 1000
                
        # background        
        self.background = ''        
        self.bgColor = color.transparent
        self.opacity = 1.0

        # theme
        self.gamma = ''
                
        # puncture
        self.puncture = False
        self.puncturePriority = 100

        # dirty
        self.preRect = 0, 0, 0, 0
        self.dirtyRects = []
        
        self.changeEvent('left', self._postPosition)
        self.changeEvent('top', self._postPosition)
        self.changeEvent('width', self._postSize, postevent = False)
        self.changeEvent('height',self._postSize, postevent = False)
        self.changeEvent('enabled', self._setEnabled)
        self.changeEvent('focusChild', self.invoke, 'Focus Child Change')
        self.changeEvent('puncture', self.__setpuncture, sync = False)
        self.changeEvent('visible', self.__onVisibleChange)

        # sight is a view of RL, if this component is not dirty, we can reuse this sight
        self.sightDirty = True
        self.sight = 0
        self.sightframeNumber = 0 # our sight is existed in which frame
        self.allSightDirty = False
        
        self.dirty = True
        self.dead = False
        
        self.autoDirty(
            [
                'visible',
                'opacity',
                'background',
                'bgColor',
            ], [
                'Size Change',
                'Position Change',
                'Visible Change',
                'Child Add',
                'Child Remove',
                'Focus Change',     # tab order change will cause focus change
            ]
        )
        self.bind('Size Change', self.__setAllChildDirty)        
        self.bind('Position Change', self.__setAllChildDirty)
        self.changeEvent('dirty', self.__setKoanDirty)

        # extend for draw agent
        self.beginEffect = None
        self.drawEffect = None
        self.endEffect = None

    def __onFocusChange(self):
        self.focus = self.isFocused()
        
    def __setSightDirty(self):
        if not self.sightDirty:
            self.sightDirty = True
            self.sightframeNumber = 0
            #self.sight = 0
            if self.parent:
                self.parent.__setSightDirty()

    def addAcceleratorKey(self, key, cmd):
        key = key.replace('SPACE', ' ')
        assert type(key) is unicode and type(cmd) is unicode
        if not hasattr(self, 'keymaps'):
            self.keymaps = {}
        if key not in self.keymaps:
            self.keymaps[key] = []
        self.keymaps[key].append('<'+cmd+'>')
        
    def setCapture(self, v):
        """
        set global cursor in captured or released state

        @param v: Capture or Release cursor
        """
        if v:
            Component.mouseCapture = self
        else:
            Component.mouseCapture = None
        self.window.setCapture(v)
        
    def __invokeVisibleChange(self, node):
        v = node.visible and self.visible
        node.invoke('Visible Change', v)
        if node.parent:
            node.parent.invoke('Child Visible Change', v)

    def __setChildDirty(self, node):
        node.dirty = True

    def invokeVisibleChange(self):
        self.__onVisibleChange()
        
    def __onVisibleChange(self):
        self.invoke('Visible Change', self.visible)
        if self.parent:
            self.parent.invoke('Child Visible Change', self.visible)

        recursiveWalkComponent(self, self.__invokeVisibleChange)
        if self.visible:
            self.__setAllChildDirty()

        if not self.visible:
            self.dirtyRects.append(self.preRect)
    
    def __setAllChildDirty(self):
        recursiveWalkComponent(self, self.__setChildDirty)
    
    def __setKoanDirty(self):
        if self.dirty:
            self.__setSightDirty()
            self.window.invalid = True

    def getChildName(self, child):
        """
        get the name of a child component

        @param child: instance of the child
        @return: name of the child
        @rtype: string
        """
        for i, j in self.__dict__.items():
            if j == child and i <> 'focusChild':
                return i
        return '<NoFind>'

    def currentState(self):
        """
        return the current state of this component

        @return: possible states:
                 1. disable
                 2. focus
                 3. inactive
                 4. normal
        @rtype: string
        """
        if not self.enabled:
            return 'disable'
        elif self.isFocused():
            return 'focus'
        else:
            return 'normal'

    def __setpuncture(self):
        if self.window:
            if self.puncture:
                self.window.punctureManager.add(self)
            else:
                self.window.punctureManager.remove(self)

    def setDirty(self, *arg):
        self.dirty = True

    def calPunctureRect(self):
        """
        get the absolute position of this component for puncture

        @return: (left, top, width, height) at global coordinate
        @rtype: tuple of 4 number
        """
        return self.calGlobalRect()

    def isVisible(self):
        """
        query the visibility of this component.
        if one of it's ancestor is invisible, it is invisible

        @rtype: boolean
        """
        v = self
        while v.parent:
            if not v.visible:
                return False
            v = v.parent
        return True

    def autoDirty(self, attributes, events = []):
        """
        register attributes and events, so that when they changed or activated,
        this component was set as dirty

        @param attributes: attributes that dirty this component
        @type attributes: a list of strings
        @param events: events that dirty this component
        @type events: a list of strings
        @rtype: None
        """
        for i in attributes:
            self.changeEvent(i, setattr, self, 'dirty', True)

        for i in events:
            self.bind(i, self.setDirty)

    def getChildren(self):
        return self._children
    children = property(getChildren)

    def getTabChildren(self):
        children = []
        for c in self.children:
            if c.visible and c.enabled and not c.blind:
                #if hasattr(c, 'tab'):
                if c.tabStop:
                    children.append(c)
                children += c.tabChildren            
        return children
    tabChildren = property(getTabChildren)
    
    def getRoot(self):
        """
        Get the root component

        @rtype: an instance of component
        """
        if self._root <> None and self._root():
            return self._root()

        t = self
        while t.parent:
            t = t.parent
        self._root = ref(t)
        return t
    root = property(getRoot)
        
    def getWindow(self):
        """
        get the window
        
        @rtype: an instance of window
        """
        try:
            return koan.Null if self.root is self else self.root
        except:
            return koan.Null
    window = property(getWindow)
    
    def getIsMouseDown(self):
        return self == Component.mouseDownIn
    def setIsMouseDown(self, v):
        #if Component.mouseDownIn:
        #    Component.mouseDownIn.dirty = True
        if self.getIsMouseDown() == v:
            return
        if v:
            Component.mouseDownIn = self
            Component.mousePreDown = ref(self)
        elif Component.mouseDownIn == None:
            Component.mouseDownIn = None
    isMouseDown = property(getIsMouseDown, setIsMouseDown)

    def getIsMouseRDown(self):
        return self == Component.mouseRDownIn
    def setIsMouseRDown(self, v):
        #if Component.mouseRDownIn:
        #    Component.mouseRDownIn.dirty = True
        if self.getIsMouseRDown() == v:
            return
        if v:
            Component.mouseRDownIn = self
            Component.mousePreDown = ref(self)
        elif Component.mouseRDownIn == self:
            Component.mouseRDownIn = None
    isMouseRDown = property(getIsMouseRDown, setIsMouseRDown)
    
    def _setEnabled(self):
        if not self.enabled and self.isFocused():
            if self.parent:
                self.parent.guestFocusChild()
        self.isMouseOver = False
        self.invoke('Enable Change')
        
    def show(self):
        """
        show animation

        @rtype: None
        """
        self.visible = True

    def hide(self):
        """
        hide animation

        @rtype: None
        """
        self.visible = False
    
    def showHide(self):
        self.visible = not self.visible

    def getParent(self):
        if self._parent:
            return self._parent()
        return None
    def setParent(self, n, **argd):
        o = self.getParent()
        if n is o:
            return  # no change

        if o:
            o._removeChild(self)
        if n:
            self._parent = ref(n)
            n._addChild(self, **argd)
        else:
            self._parent = None
        
        recursiveWalkComponent( self, lambda x: setattr(x, '_root', None) )
        self.invoke('Parent Change')
    parent = property(getParent, setParent)
    
    def _postSize(self):
        self.dirtyRects.append(self.preRect)
        self.preRect = self.position

        self.invoke('Size Change')

        if self.parent:
            self.parent.invoke('Child Size Change')
        
        for c in self._children:
            c.invoke('Parent Size Change')

    def _postPosition(self):
        self.dirtyRects.append(self.preRect)
        self.preRect = self.position

        self.invoke('Position Change')

        if self.parent:
            self.parent.invoke('Child Position Change')
            
        #for c in self._children:
        #    c.invoke('Parent Position Change')
        map(lambda c: c.invoke('Parent Position Change'), self.children)        
        
    def close(self):
        """
        close this component so that it won't be drawn again

        @rtype: None
        """
        if Component.tabStopObj is self:
            Component.tabStopObj = None
        if Component.mouseCapture is self:
            Component.mouseCapture = None
        self.close = koan.Action(Component_closeagain, str(self))
        self.free()
            
    def free(self):
        """
        break the connecting amoung parnet and children

        @rtype: None
        """
        if self.dead:
            print 'Component has been dead', self
            return

        self.dead = True
        if self.parent:
            self.parent.dirty = True
        self.invoke('Close')
        
        window = self.window
        if window and koan.animManager:
            koan.animManager.removeObj(self)
        EventManager.clear(self)
        
        self.freeChildren()
        
        # free draw agent
        if self.beginEffect:
            self.beginEffect.close()
            self.beginEffect = None
        if self.endEffect:
            self.endEffect.close()
            self.endEffect = None
        if self.drawEffect:
            self.drawEffect.close()
            self.drawEffect = None
            
        self.parent = None
        
        if koan.isDebug:
            deadPeople[id(self)] = str(self)

        ScriptObject.free(self)      

    def freeChildren(self):
        self.dirty = True
        self.focusChild = None

        while self._children:
            c = self._children[-1]
            if c:
                c.close()
        
        self._children = []

    def setFocus(self, hint = ''):
        """
        set this component focused

        @rtype: None
        """
        if self.isFocused():
            if self.focusChild:
                self.focusChild.setFocus(hint)
            return

        if not self.parent: # desktop
            return

        if not self.enabled:
            return

        # collect pre-focus
        window = self.window
        top = window.focusChild
        
        preFocus = {}
        if top:
            preFocus[top] = 0
            while top.focusChild:# and top.focusChild.enabled and top.focusChild.visible:
                top = top.focusChild
                preFocus[top] = 0

        # set focus
        ch = self
        own = self.parent
        while own:
            own.focusChild = ch
            ch = own
            own = own.parent

        # collect now-focus
        top = window.focusChild
        if top:
            curFocus = { top : 0 }
            while top.focusChild:# and top.focusChild.enabled and top.focusChild.visible:
                top = top.focusChild
                curFocus[top] = 0
    
            for e in curFocus.keys():
                if e not in preFocus:
                    e.invoke('Focus Change')
                    if hint:
                        e.invoke('Focus Dir', hint)
    
            for e in preFocus.keys():
                if e not in curFocus:
                    e.invoke('Focus Change')

    def isFocused(self):
        """
        query if this component is focused

        @rtype: boolean
        """
        if not self.enabled:
            return False
        if self.parent:
            return self.parent.focusChild == self and self.parent.isFocused()
        return True
    #focus = property(isFocused)
    
    def find(self, type, **argd):    
        for a, v in argd.items():
            if getattr(self, a) != v:
                return None
        
        if isinstance(self, type):
            return self
        
        for c in self.children:
            obj = c.find(type)
            if obj:
                return obj
        return None
    
    def removeChild(self, c):
        if c:
            c.parent = None
        
    def _removeChild(self, c):
        """
        to remove a child from this component

        @param c: the child to be removed
        @type c: an instance of Compoenet
        @rtype: None
        """
        if c.parent == self:
            c._parent = None

        if self.focusChild == c:
            self.focusChild = None

        if c in self._children:
            self.invoke('Child Remove', c)
            self._children.remove(c)

        if self.focusChild is None and self.isFocused():
            self.guestFocusChild()
    
    def isDescendant(self, obj):
        for c in self.children:
            if c is obj:
                return True
            if c.isDescendant(obj):
                return True            
        return False

    def addChild(self, c, **argd):
        c.setParent(self, **argd)
        
    def _addChild(self, c, **argd):
        """
        add a new child to this component

        @rtype: None
        """
        if c in self._children:
            raise TypeError
        if argd.get('front', False):
            self._children.insert(0, c)
        else:
            self._children.append(c)
        #if not self.focusChild:
        #    self.focusChild = c
        self.invoke('Child Add', c)

    def drawBorder(self, render, w, c):
        render.SetTexture(None)
        render.SetColor(*c)
        render.DrawRect(0, 0, self.width, w)
        render.DrawRect(0, self.height-w, self.width, self.height)
        render.DrawRect(0, 0, w, self.height)
        render.DrawRect(self.width-w, 0, self.width, self.height)
        render.SetColor(*color.white)  

    def onDraw(self, render):
        """
        override this function to draw this component

        @rtype: None
        """
        if self.drawEffect:
            self.drawEffect.draw(render, self.width, self.height)            
        elif self.background:
            # texture
            t = render.GetTexture(self.background, gamma = self.gamma)
            render.SetTexture(t)
            render.DrawRect(*self.localRect)
        elif self.bgColor[0] > 0:
            # color
            render.SetTexture(None)
            render.SetColor(*self.bgColor)
            render.DrawRect(*self.localRect)
            render.SetColor(*color.white)
        
    def drawChild(self, render):
        """
        overwritable: recursively draw it's children
        @rtype: None
        """
        map(lambda c: c.passDraw(render), self._children)

    def updateDirtyRect(self, render):
        if self.dirtyRects:
            try:
                map(lambda i: render.DirtyRect(*i), self.dirtyRects)
                self.dirtyRects = []
            except:
                print self, self.dirtyRects

    def beginPassDraw(self, render):
        """
        overwritable: draw this component
        @rtype: None
        """        
        
        render.PushAlpha(self.opacity)
        render.PushMatrix()
        render.Translate(*self.xy)
        if self.clip:
            render.PushBound(*self.localRect)

        if self.beginEffect:
            self.beginEffect.draw(render, self.width, self.height)

    def endPassDraw(self, render):
        if self.endEffect:
            self.endEffect.draw(render, self.width, self.height)

        if self.clip:
            render.PopBound()
        render.PopMatrix()
        render.PopAlpha()
        
    def updateView(self, render):
        l, t, r, b = render.viewStack[-1]
        l, t = self.parent2local(l, t)
        r, b = self.parent2local(r, b)
        local = Intersect((l, t, r, b), (0, 0, self.width, self.height))
        render.viewStack.append(local)
        return local[2] - local[0] > 0 and local[3] - local[1] > 0

    def passDraw(self, render):
        """
        overwritable: draw this component
        @rtype: None
        """
        if not render.forceSightDirty and not self.sightDirty and self.sightframeNumber == render.frameNumber - 1:
            if self.sight == 0:
                print 'WA bug !!!'
            if self.visible:
                self.sight = render.ReuseSight(self.sight)
                self.sightframeNumber = render.frameNumber
        else:           
            self.updateDirtyRect(render)
            if self.visible:
                
                if not render.forceSightDirty:
                    self.sight = render.PushSight(self.left, self.top, self.width, self.height, self.dirty or self.allSightDirty)
                    self.sightframeNumber = render.frameNumber
                
                if not render.forceSightDirty and self.allSightDirty:
                    render.forceSightDirty = self
                
                self.beginPassDraw(render)
                
                if koan.isDebug:
                    render.PushMatrix()
                
                if self.updateView(render):
                    self.onDraw(render)
                #else:
                #    print 'skip', self.left, self.top, self.width, self.height
                self.drawChild(render)
                render.viewStack.pop()

                if koan.isDebug:
                    render.PopMatrix()
                    #if hasattr(self, 'tab') and self.focus:
                    #if Component.tabStopObj == self:
                    #if self.focus and self.focusChild == None:
                    #    self.drawBorder(render, 2, color.red)

                self.endPassDraw(render)
                                    
                if render.forceSightDirty == self:
                    render.forceSightDirty = None
                    
                if not render.forceSightDirty:
                    render.PopSight()
                    
                
            self.dirty = False
            self.sightDirty = False
            self.allSightDirty = False
            
    def passKey(self, key, keymaps):
        """
        process key stroke event, then pass this event to this compoent's focused child

        @return: return true if this key stroke event was processed here, otherwise return false
        @rtype: boolean
        """
        if not self.enabled or not self.visible:
            return False
        if self.blind:
            return True

        if key == 'TAB' or key == 'SHIFT TAB':
            children = self.tabChildren
            if children:
                children.sort(lambda x, y: cmp(x.tabStop, y.tabStop))
                try:
                    idx = children.index(Component.tabStopObj)
                except:
                    idx = -1
                idx += 1 if key == 'TAB' else -1
                idx = idx % len(children)
                c = children[idx]
                c.setFocus()
                Component.tabStopObj = c
                #print 'tab stop', c
                return True

        if hasattr(self, 'keymaps'):
            keymaps = keymaps.copy()
            keymaps.update(self.keymaps)
            
        r = False
        if self.focusChild:
            r = self.focusChild.passKey(key, keymaps)
        if not r:
            if key in keymaps:
                for cmd in keymaps[key]:
                    if cmd in self.events:
                        self.invoke(cmd)
                        return True
            r = self.onKey(key)
        return r

    def passCommand(self, key, param):
        """
        try to send command to relavent components to process it

        @return: if this command was processed
        @rtype: boolean
        """
        if not self.enabled or not self.visible or self.blind:
            return False

        r = False
        if self.focusChild:
            r = self.focusChild.passCommand(key, param)
        if not r:
            r = self.onCommand(key, param)
            if r:
                print 'Command:', key, param, 'accept by', self
        if not r: # still cannot find
            for i in self._children:
                if i == self.focusChild:
                    continue
                r = i.passCommand(key, param)
                if r:
                    break
        return r

    def convertCoord2Local(self, x, y):
        """
        convertCoord2Local(x, y) -> x, y

            convert owner coordinate to local system

        @return: the global coordinate of (x, y)
        @rtype: tuple of 2 number
        """
        return x - self.left, y - self.top

    def hitTest(self, x, y):
        """
        hitTest(self, x, y) -> bool

        when the mouse is click on the region of this component,
        this function test whether the point can click this object.
        Usually we answer YES for a rectangle object, but if this
        object is not rectangle, we must decide that.
        @param x, y: (x, y) in local coordinate
        @return: if (x, y) inside the region of this component
        @rtype: boolean
        """
        return (x >= 0 and x < self.width and y >= 0 and y < self.height)

    def passScrollMsg(self, direction, wParam, lParam):
        x = []
        if direction == 'H':
            x = self.fire('HScroll', wParam, lParam)
        elif direction == 'V':
            x = self.fire('VScroll', wParam, lParam)
        for i in x:
            if i:
                return

        if self.parent:
            return self.parent.passScrollMsg(direction, wParam, lParam)
            
    def passWheelMsg(self, state):
        if not self.enabled or not self.visible or self.blind:
            return False
        
        x = self.fire('Mouse Wheel', state)
        for i in x:
            if i:
                return

        if self.parent:
            return self.parent.passWheelMsg(state)
    
    def passMouseMsgToChildren(self, x, y, button, state, *args):
        """
        pass mouse message to children, and then process the mouse message
        @param x: mouse pos x in local coordinate (may has been scrolled)
        @param y: mouse pos y in local coordinate (may has been scrolled)
        @rtype: True if mouse over myself or one of my children
        """
        #---------------------------------------------
        # check if any child is focus
        #---------------------------------------------
        for c in self.children[::-1]:
            # 1. last time is over or mouse down, we should focus to recheck again
            # 2. check only if child pass hitTest
            #if c.visible and c.enabled and not c.blind:
            if c.visible and not c.blind:       # disabled control still should pass mouse event to child
                _x, _y= c.parent2local(x, y)
                if c.passMouseMsg(_x, _y, button, state, *args):
                    return True
        return False

    def passMouseMsg(self, x, y, button, state, *args):
        """
        pass mouse message, and then process the mouse message
        @param x: mouse pos x in local coordinate
        @param y: mouse pos y in local coordinate
        @rtype: True if mouse over myself or one of my children
        """
        if Component.mouseCapture is not self:
            '''
            In some situations (scroll in StackPanel), local coordinate has been translated by scrolling or others.
            And hittest need the original rect
            '''
            _x, _y = self.local2parent(x, y)
            if not self.hitTest(*Component.parent2local(self, _x, _y)):
            #if not self.hitTest(x, y):
                return False
            if not self.enabled:            
                return self.handleMouseMsg(x, y, button, state, *args)   # control is disabled, so mouse event should stop here
            if self.passMouseMsgToChildren(x, y, button, state, *args):
                return True # mouse pass to child
        return self.handleMouseMsg(x, y, button, state, *args)

    def handleMouseMsg(self, x, y, button, state, *args):        
        # wa, mouse pass to me
        if Component.mouseOver <> self:
            if Component.mouseOver:
                Component.mouseOver.isMouseOver = False
                #print 'Mouse Leave', self
                Component.mouseOver.invoke('Mouse Leave')
            Component.mouseOver = self
            self.isMouseOver = True
            #print 'Mouse Enter', self
            self.invoke('Mouse Enter')
        
        #---------------------------------------------
        # check mouse move
        #---------------------------------------------        
        if not button:
            self.invoke('Mouse Move', x, y, args[0])

        #---------------------------------------------
        # disabled control should not fire following events
        #---------------------------------------------
        if not self.enabled:
            return True        

        #---------------------------------------------
        # check if double click
        #---------------------------------------------
        if not Component.mouseDblClk and state == 'DBCLICK':
            if Component.mousePreDown() is self:
                if button == 'LEFT':
                    #print 'Dbl Click', self
                    Component.mouseDblClk = True
                    self.isMouseDown = True
                    self.invoke('Dbl Click', x, y, args[0])
                if button == 'RIGHT':
                    #print 'RDbl Click', self
                    Component.mouseDblClk = True
                    self.isMouseRDown = True
                    self.invoke('RDbl Click', x, y, args[0])
            else:
                state = 'DOWN'
                
        #---------------------------------------------
        # check if mouse down
        #---------------------------------------------
        if state == 'DOWN':
            if button == 'LEFT':
                if Component.mouseDownIn:
                    _x, _y = self.local2global(x, y)
                    _x, _y = Component.mouseDownIn.global2local(_x, _y)
                    Component.mouseDownIn.invoke('Mouse Up', _x, _y, args[0])
                    Component.mouseDownIn = None
            
                if Component.mouseDownIn == None:
                    self.isMouseDown = True
                    #print 'Mouse Down', self
                    self.invoke('Mouse Down', x, y, args[0])
                
            if button == 'RIGHT':
                if Component.mouseRDownIn:
                    _x, _y = self.local2global(x, y)
                    _x, _y = Component.mouseRDownIn.global2local(_x, _y)
                    Component.mouseRDownIn.invoke('Mouse RUp', _x, _y, args[0])
                    Component.mouseRDownIn = None
                    
                if Component.mouseRDownIn == None:
                    self.isMouseRDown = True
                    #print 'Mouse RDown', self
                    self.invoke('Mouse RDown', x, y, args[0])
        #---------------------------------------------
        # check if mouse down
        #---------------------------------------------
        if state == 'UP':
            if button == 'LEFT':
                if Component.mouseDownIn == self:
                    #self.invoke('Click')
                    #print 'Mouse Up', self
                    self.invoke('Mouse Up', x, y, args[0])
                elif Component.mouseDownIn:
                    _x, _y = self.local2global(x, y)
                    _x, _y = Component.mouseDownIn.global2local(_x, _y)
                    Component.mouseDownIn.invoke('Mouse Up', _x, _y, args[0])
                Component.mouseDownIn = None
            elif button == 'RIGHT':
                if Component.mouseRDownIn == self:
                    #self.invoke('RClick')
                    #print 'Mouse RUp', self
                    self.invoke('Mouse RUp', x, y, args[0])
                elif Component.mouseRDownIn:
                    _x, _y = self.local2global(x, y)
                    _x, _y = Component.mouseRDownIn.global2local(_x, _y)
                    Component.mouseRDownIn.invoke('Mouse RUp', _x, _y, args[0])
                Component.mouseRDownIn = None                  

        return True

    def guestFocusChild(self, hint = ''):
        """
        set focus to one child (guess?)

        @rtype: None
        """
        if self.focusChild:
            if not self.focusChild.enabled or not self.focusChild.visible:
                self.focusChild = None
            
        if self.dead or self.focusChild:
            return
  
        for e in self.children:
            if e.enabled and e.visible:
                e.setFocus(hint)
                break

    def focusMove(self, n, focusCycle):
        """
        change the focus child in this component

        @param n: position value to move forward, negative to backward
        @return: if the focus was changed
        @rtype: boolean
        """
        if self.focusChild == None:
            if len(self._children) > 0:
                self._children[0].setFocus()
                return True
        else:
            try:
                index = self._children.index(self.focusChild)
            except ValueError:
                return False
            else:
                count = len(self._children)
                next = index
                while 1:
                    next += n

                    if not focusCycle:
                        if next < 0 or next >= count:
                            return False

                    next = (next + count) % count # warp

                    c = self._children[next]
                    if not c.enabled:
                        continue
                    c.setFocus()
                    return True
        return False
    #############################################################
    #
    #   General Overwritable function
    #
    #############################################################

    def onKey(self, key):
        """
        override this function to process key stroke

        @return: if the key stroke event was processed
        @rtype: boolean
        """
        self.invoke('Key', key)
        return False

    def onCommand(self, cmd, param):
        """
        override this function to process commands

        @param cmd: the command type
        @type cmd: string
        @param param: additional parameter(s) for this command
        @return: if that command was processed
        @rtype: boolean
        """
        return False
            
    def getPixelUnit(self):
        if self.parent:
            return self.parent.getPixelUnit()
        else:
            return 1, 1

    def getPuncturePixelUnit(self):
        return self.getPixelUnit()

    def calTextSize(self, text, font, fontsize):
        """
        get the size of a string on the screen
    
        @param font: font of the string
        @param fontsize: font size of the string
        @return: size of the string, at format (width, height)
        @rtype: a tuple of 2 number
        """
        if not text:
            return 0, 0

        unit = self.getPixelUnit()
        
        size = StringTextureManager.GetStringTextureSize(font, text, fontsize * unit[1])
        '''
        if not self.root or not hasattr(self.root, 'render'):            
            size = StringTextureManager.GetStringTextureSize(font, text, fontsize * unit[1])
        else:
            ret = self.root.render.GetStringTexture(
                text,
                fontsize * unit[1],
                color.white,
                font
            )
            try:
                text, size = ret
            except:
                print ret
                traceback.print_exc()
        '''
        size = size[0]/unit[0], size[1]/unit[1]
        return size


    #-----------------------------------------------------------------------------
    # methods for coordinate transform
    #-----------------------------------------------------------------------------
    def global2local(self, x, y):
        """
        @param x, y: (x, y) in global coordinate
        @return: (x, y) in local coordinate
        """
        path = [self]
        parent = self.parent
        while parent:
            path.append(parent)
            parent = parent.parent
        for o in path[::-1]:
            x, y = o.parent2local(x, y)
        return x, y
        
    def local2global(self, x, y):
        """
        @param x, y: (x, y) in local coordinate
        @return: (x, y) in global coordinate
        """
        if self.parent:
            return self.parent.local2global(*self.local2parent(x, y))
        else:
            return self.local2parent(x, y)
    
    def getGlobalRect(self):
        return self.local2global(0, 0) + self.local2global(*self.size)
    globalRect = property(getGlobalRect)
    
    def parent2local(self, x, y):
        """
        @param x, y: (x, y) in parent coordinate
        @return: (x, y) in local coordinate
        """
        return x - self.left, y - self.top
        
    def local2parent(self, x, y):
        """
        @param x, y: (x, y) in local coordinate
        @return: (x, y) in parent coordinate
        """
        return x + self.left, y + self.top

    def calGlobalRect(self):
        """
        get the absolute position of this component

        @return: (left, top, width, height) at global coordinate
        @rtype: tuple of 4 number
        """
        puX, puY = self.getPixelUnit()
        return self.local2global(0, 0) + (self.width * puX, self.height * puY)
        
        p = self
        offx = 0
        offy = 0
        while p:
            offx += p.left
            offy += p.top

            if p.parent == None:
                return (float(offx) * float(p.pixelUnit[0]), float(offy) * float(p.pixelUnit[1]),
                    float(self.width) * float(p.pixelUnit[0]), float(self.height) * float(p.pixelUnit[1]))

            p = p.parent

        print '[koan]: calGlobalRect Impossible code region'
        return -1, -1, -1, -1

    def calGlobalPoint(self, x, y):
        """
        transfer (x, y) from local coordinate to global coordinate

        @return: the global coordinate of (x, y)
        @rtype: tuple of 2 number
        """
        p = self
        offx = x
        offy = y
        while p:
            offx += p.left
            offy += p.top

            if p.parent == None:
                return float(offx) * float(p.pixelUnit[0]), float(offy) * float(p.pixelUnit[1])
            p = p.parent

        print '[koan]: calGlobalPoint Impossible code region'
        return -1, -1, -1, -1

class Static(Component):
    def __init__(self, parent = None):
        Component.__init__(self, parent)
        self.blind = True
        self.tabStop = False

class Splitter(Static):
    def __init__(self, parent = None):
        Static.__init__(self, parent)

class Border(Static):
    def __init__(self, parent = None):
        Static.__init__(self, parent)
        self.border = 2
        
    def onDraw(self, render):    
        if self.bgColor[0] > 0:
            # color
            b = self.border
            w = self.width
            h = self.height
            render.SetTexture(None)
            render.SetColor(*self.bgColor)
            render.DrawRect(0, 0, w, b)     # top
            render.DrawRect(0, h-b, w, h)   # bottom
            render.DrawRect(0, 0, b, h)     # left
            render.DrawRect(w-b, 0, w, h)   # right
            render.SetColor(*color.white)
            
koan.optimize(Component.passMouseMsg)
koan.optimize(Component.passDraw)

#########################################################
#
#   Test This Module
#
#########################################################

if __name__ == '__main__':
    from window import Window
    from pprint import pprint
    import color

    class MyComponent(Component):
        def __init__(self, parent = None):
            Component.__init__(self, parent) 
            
            self.bind('Mouse Enter', self.trace, 'Mouse Enter')
            self.bind('Mouse Leave', self.trace, 'Mouse Leave')
            self.bind('Mouse Down', self.trace, 'Mouse Down')
            self.bind('Mouse Up', self.trace, 'Mouse Up')
            self.bind('Mouse RDown', self.trace, 'Mouse RDown')
            self.bind('Mouse RUp', self.trace, 'Mouse RUp')
            self.bind('Click', self.trace, 'Click')
            self.bind('Dbl Click', self.trace, 'Dbl Click')
            self.bind('RDbl Click', self.trace, 'RDbl Click')
            
        def trace(self, *argv, **argd):
            print self, argv
            
    koan.init()
    
    w = Window()    
    w.create(0, 0, 800, 600, caption = True)
    w.bgColor = color.darkblue
    
    o = MyComponent(w)
    o.rect = 0, 0, 400, 300
    o.bgColor = color.gray
    
    b = Border(o)
    b.bgColor = color.white
    b.bindData('width', o, 'width', dir = '<-')
    b.bindData('height', o, 'height', dir = '<-')


    o = MyComponent(o)
    o.rect = 50, 50, 200, 100
    o.bgColor = color.yellow
    w.show()
    
    koan.run(1)    
    koan.final()
