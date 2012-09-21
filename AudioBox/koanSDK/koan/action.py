"""
module that manage Action and Event

@undocumented: AutoUnbind
"""

from weakref import ref
from anim import PostEvent
import traceback

class Action:
    """
    Used as call back function.

    Example:
        >>> action = Action()
        >>> action.assign(func, param)  # func(param) will be called
        >>> action.assign(func)         # func() will be called
        >>> action.assign(func, p1, p2) # func(p1, p2) will be called
        # do something
        >>> action() -> call func(p1, p2)
    """
    def __init__(self, callback = None, *args):
        #self.callback = None
        #self.arg = ()
        #if callback:
        self.assign(callback, *args)

    def __repr__(self):
        return "<Action: %s, %s>" %(str(self.callback), str(self.arg))

    def assign(self, callback, *args):
        """
        setting the callback function of this action
        @param callback: the callback function
        @param args: arguments pass to the callback function
        """
        self.callback = callback
        self.arg = args

    def __call__(self, *argv, **argd):
        """
        call the callback function attached to this action
        """
        return self.callback(*(self.arg + argv), **argd)

    def callnow(self, *argv, **argd):
        """
        same as call action directly
        """
        return self.callback(*(self.arg + argv), **argd)

class PureAction(Action):
    def __call__(self, *argv, **argd):
        if self.callback:
            return self.callback(*self.arg)

    def callnow(self, *argv, **argd):
        if self.callback:
            return self.callback(*self.arg)
            
class PostAction(Action):
    """
    Used as call back function. But this action will be execute
       before the next frame paint.

    Example:
        >>> action = PostAction()       # create a PostAction object
        >>> action.assign(func, param)  # func(param) will be called
        >>> action.assign(func)         # func() will be called
        >>> action.assign(func, p1, p2) # func(p1, p2) will be called
        # do something
        >>> action() -> post call to func(p1, p2)
    """
    def __repr__(self):
        return "<PostAction: %s, %s>" %(str(self.callback), str(self.arg))

    def __call__(self, *argv, **argd):
        """
        post the callback function to be called next frame
        """
        PostEvent(self.callback, *(self.arg + argv), **argd)

class Actions:
    """
    Used as call back function.

    Example:
        >>> actions = Actions()
        >>> actions.add(func, param)  # func(param) will be called
        >>> actions.add(func)         # func() will be called
        >>> actions.add(func, p1, p2) # func(p1, p2) will be called
    """
    def __init__(self):
        self.callbacks = []
        self.args = []

    def add(self, callback, *args):
        """
        add a action to this list

        @param callback: the callback function to be added
        @type callback: a callable object
        @param args: the argu: the arguments to this callback
        """
        self.callbacks.append(callback)
        self.args.append(args)

    def remove(self, callback):
        """
        remove a callback from the list

        @param callback: the callback function to be removed
        @type callback: a callable object
        """
        tc = []
        ta = []
        for i in range(len(self.callbacks)):
            if callback <> self.callbacks[i]:
                tc.append(self.callbacks[i])
                ta.append(self.args[i])
        self.callbacks  = tc
        self.args       = ta

    def __call__(self, *argv, **argd):
        """
        call every callback functions in the list
        """
        for i in range(len(self.callbacks)):
            self.callbacks[i](*(self.args[i] + argv), **argd)
