import koan
from action import Action, PostAction


def getSet(setobj, setprop, getobj, getprop, cvt = None):
    """
    This function will execute:
        setobj.setprop = getobj.getprop

    Example:
        >>> getSet(setobj, "setprop", getobj, "getrop")
    """
    v = getattr(getobj, getprop)
    if cvt:
        v = cvt(v)
    setattr(setobj, setprop, v)

class NotifyEvent:
    """
    a representation of event
    for management of events
    """
    def __init__(self, evtmanager, evt, evtobj):
        self.evtmanager = evtmanager
        self.evt        = evt
        self.evtobj     = evtobj

    def remove(self):
        if self.evtmanager:
            self.evtmanager.removeEvent(self.evt, self.evtobj)

        self.evtmanager = None
        self.evt = None
        self.evtobj = None

class AutoUnbind:
    def __init__(self, evtobj):
        self.evt = evtobj
    def __del__(self):
        self.evt.remove()

if koan.isTraceLeak:
    import weakref
    evtobjs = []

class EventManager(object):
    """
    derive from this class to enable event handling

    @group Manipulator: clear, autoRemove, bind, unbind, removeEvent, alias
    """
    # _propertySensor holds a dictionary of
    # (property name : actions activated when this property changed)
    def __init__(self):        
        self.__dict__['events'] = {} # not use __setattr__
        self.__dict__['_propertySensor'] = {}
        if koan.isTraceLeak:
            self.__ObjectName = str(self)
        self._autoremove = set()
        
        if koan.isTraceLeak:
            self.__self = weakref.ref(self)
            evtobjs.append(self.__self)

    def __del__(self):    
        if koan.isTraceLeak:
            #print '__del__', self
            global evtobjs
            evtobjs.remove(self.__self)
            self.__self = None

    def __clear(self):
        self.events = {}
        self._propertySensor = {}
        for i in self._autoremove:
            i.remove()
        self._autoremove = None

    def clear(self):
        """
        clear events

        @rtype: None
        """
        self.__clear()

    def close(self):
        """
        clear events, as same as clear

        @rtype: None
        """
        self.__clear()

    def autoRemove(self, *x):
        """
        set that events should be removed when clear called

        @rtype: None
        """
        for i in x:
            self._autoremove.add(i)

    def bind(self, evt, func, *arg, **argd):
        """
        bind a function to be called when an event happened

        @param evt: the event that shall be notified
        @param func: the function to be called when the event happened
        @return: a NotifyEvent object
        @rtype: NotifyEvent
        """
        # func and arg will be packed as an Action
        # and then add to event dictionary
        if evt not in self.events:
            self.events[evt] = []

        if not argd.get('postevent', True):
            a = Action(func, *arg)
        else:
            a = PostAction(func, *arg)

        self.events[evt].append(a)
        
        event = NotifyEvent(self, evt, a)
        
        if argd.get('autoremove', True):
            self.autoRemove(event)
        return event

    def unbind(self, evt, func):
        """
        remove an Action(identified by its function) from an event

        @param evt: the event that have the action to be removed
        @param func: the Action bind with this function will be removed
        @rtype: None
        """
        if evt in self.events:
            evts = self.events[evt]
            for i in evts:
                if i.callback == func:
                    evts.remove(i)

    def removeEvent(self, evt, evtobj):
        """
        remove an Action from an event

        @param evt: the event that have the action to be removed
        @param evtobj: the Action to be removed
        @rtype: None
        """
        if self.events.has_key(evt) and evtobj in self.events[evt]:
            self.events[evt].remove(evtobj)
        elif self._propertySensor.has_key(evt) and evtobj in self._propertySensor[evt]:
            self._propertySensor[evt].remove(evtobj)

    def invoke(self, evt, *arg):
        """
        call the event by post call

        @param evt: the event activated
        @rtype: None
        """
        if evt in self.events:
            evts = self.events[evt][:]
            for i in evts:
                i(*arg)

    def fire(self, evt, *arg):
        """
        call the event right now

        @param evt: the event activated
        @rtype: []
        """
        if evt in self.events:
            evts = self.events[evt][:]
            return [i.callnow(*arg) for i in evts]
        else:
            return []

    def bindCmd(self, cmd, func, *arg, **argd):
        return self.bind('<'+cmd+'>', func, *arg, **argd)
        
    def unbindCmd(self, cmd, func):
        return self.unbind('<'+cmd+'>')

    def invokeCmd(self, cmd, *arg):
        return self._invokeCmd('<'+cmd+'>', *arg)

    def fireCmd(self, cmd, *arg):
        return self._fireCmd('<'+cmd+'>', *arg)

    def _invokeCmd(self, cmd, *arg):
        if cmd in self.events:
            self.invoke(cmd, *arg)
            return True
        elif self.parent:
            return self.parent._invokeCmd(cmd, *arg)

    def _fireCmd(self, cmd, *arg):
        if cmd in self.events:
            self.fire(cmd, *arg)
            return True
        elif self.parent:
            return self.parent._fireCmd(cmd, *arg)

    def changeEvent(self, name, func, *arg, **argd):
        """
        handling property change

        @kwparam postevent: pack the function as Action or PostAction
        @type postevent: boolean
        @kwparam sync: if call the function immediately
        @type sync: boolean
        @rtype: NotifyEvent
        """
        # pack func and arg to an Action
        if argd.get('postevent', True):
            action = PostAction(func, *arg)
        else:
            action = Action(func, *arg)

        try:
            self._propertySensor[name].append(action)
        except KeyError:
            self._propertySensor[name] = [action]        

        if argd.get('sync', True) and name in self.__dict__:
            action()
        event = NotifyEvent(self, name, action)

        if argd.get('autoremove', True):
            self.autoRemove(event)
        return event

    def changingEvent(self, name, func, *arg, **argd):
        """
        handling property change

        @kwparam postevent: pack the function as Action or PostAction
        @type postevent: boolean
        @kwparam sync: if call the function immediately
        @type sync: boolean
        @rtype: NotifyEvent
        """
        # pack func and arg to an Action
        action = Action(func, *arg)

        name = '$' + name
        if name not in self._propertySensor:
            self._propertySensor[name] = []
        self._propertySensor[name].append(action)

        event = NotifyEvent(self, name, action)
        
        if argd.get('autoremove', True):
            self.autoRemove(event)
        return event
        
    def alias(self, name, target, targetfield):
        """
        make alias
        map self.name to target.targetfield
        when self.name was set to value x, target.targetfield was set to x, too.

        ex:

        self.alias('font', self.text, 'font')
        # then
        self.font = 'system'
        # has the same effect as
        self.text.font = 'system'

        @rtype: None
        """

        getSet(self, name, target, targetfield)
        self.changeEvent(name, getSet, target, targetfield, self, name, postevent = False)

    def bindData(self, name, tar, tar_name, converter = None, **argd):
        """
        ex:
        self.bindData('width', btn, 'width', dir = '=')
        self.bindData('width', btn, 'width', dir = '<-')
        self.bindData('width', btn, 'width', dir = '->')        
        """
        dir = argd.get('dir', '=')
        if dir != '->':
            # <- and =
            # self.name = tar.tar_name
            getSet(self, name, tar, tar_name, converter)
        else:
            # ->
            # tar.tar_name = self.name
            getSet(tar, tar_name, self, name, converter)

        if dir != '->':
            # self.name <- tar.tar_name
            e = tar.changeEvent(tar_name, getSet, self, name, tar, tar_name, converter, postevent = False, sync = False)
            self.autoRemove( e )
        if dir != '<-':
            # self.name -> tar.tar_name
            e = self.changeEvent(name, getSet, tar, tar_name, self, name, converter, postevent = False, sync = False)
            tar.autoRemove( e )

    def __setattr__(self, name, v):
        """
        check if name is a alias, if so, map the change to the target
        """
        p = self.__dict__.get('_propertySensor')
        if not p:
            object.__setattr__(self, name, v)
            return
        
        pre = '$'+ name in p
        post = name in p
        if post or pre:            
            if hasattr(self, name):
                org = getattr(self, name)
                notthesame = (org <> v)
            else:
                notthesame = True

            if notthesame and pre:
                map(lambda x: x(), p['$' + name])

            object.__setattr__(self, name, v)

            if notthesame and post:
                map(lambda x: x(), p[name])
        else:
            object.__setattr__(self, name, v)

    def force_setattr(self, name, v):
        '''
        trigger events even the value is not changed
        '''
        p = self.__dict__.get('_propertySensor')
        
        if p:
            map(lambda x: x(), p.get('$' + name, []))

        object.__setattr__(self, name, v)

        if p:
            map(lambda x: x(), p.get(name, []))

    def triggerChangeEvent(self, name):
        '''
        trigger events
        '''
        p = self.__dict__.get('_propertySensor')
        
        if p:
            map(lambda x: x(), p.get('$' + name, []))
            map(lambda x: x(), p.get(name, []))

class Switch(EventManager):
    def __init__(self):
        EventManager.__init__(self)
        self.assent = {} # use map as set for speed

    def __nonzero__(self):
        return len(self.assent) > 0

    def set(self, agreeman):
        pre = bool(self)
        self.assent[id(agreeman)] = True
        if pre <> bool(self):
            self.invoke('Value Change')

    def reset(self, agreeman):
        pre = bool(self)
        if self.assent.has_key(id(agreeman) ):
            del self.assent[id(agreeman)]
        if pre <> bool(self):
            self.invoke('Value Change')

