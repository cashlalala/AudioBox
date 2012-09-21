import koan

class PunctureManager(koan.EventManager):
    """PunctureManager

    event:
        Reset
    """
    def __init__(self, window):
        koan.EventManager.__init__(self)
        self.window = window
        self.objs = []
        self.bind("Reset", self.reset)
        self.autoRemove(window.bind('Window Size Change', self.reset))

    def close(self):
        """
        @rtype: None
        """
        koan.EventManager.clear(self)
        self.objs = []
        self.window = koan.Null

    def add(self, cmp):
        """
        @param cmp:
        @type cmp: Component
        """
        self.objs.append(cmp)
        self.invoke("Reset")

        cmp.punctureManagerAddEvent = []
        e = cmp.punctureManagerAddEvent

        e.append(cmp.changeEvent('visible', self.reset))
        e.append(cmp.bind('Visible Change', self.reset))
        e.append(cmp.bind('Position Change', self.reset))
        e.append(cmp.bind('Size Change', self.reset))
        e.append(cmp.bind('Parent Position Change', self.reset))
        e.append(cmp.bind('Parent Size Change', self.reset))
        e.append(cmp.bind('Puncture Change', self.reset))
        e.append(cmp.bind('Close', self.remove, cmp))

    def remove(self, cmp):
        """
        remove a Component

        @param cmp: the Component to be removed
        @rtype: None
        """
        if cmp in self.objs:
            for e in cmp.punctureManagerAddEvent:
                e.remove()
            cmp.punctureManagerAddEvent = []
            self.objs.remove(cmp)
            self.invoke("Reset")

    def reset(self, *args):
        if not self.window._window:
            return
        self.window._window.BeginPuncture()
        for i in self.objs:
            if not i.dead and i.isVisible():
                try:
                    useNonrectangularRegion = self.__useNonrectangularRegion
                except AttributeError:
                    self.__useNonrectangularRegion = koan.config.getInt("Misc", "usenonrectangularregion", 0)
                    useNonrectangularRegion = self.__useNonrectangularRegion
                if useNonrectangularRegion == 1 and hasattr(i, 'punctureRegion') and i.punctureRegion != None:
                    punctureRect = i.calPunctureRect()
                    pixelUnit = i.getPuncturePixelUnit()
                    self.window._window.AddPunctureRegion(i.puncturePriority, punctureRect[0], \
                        punctureRect[1], punctureRect[2], punctureRect[3], i.punctureRegion, pixelUnit[0], pixelUnit[1] )
                else:
                    self.window._window.AddPuncture(i.puncturePriority, *i.calPunctureRect())
        self.window._window.EndPuncture()
