import weakref

#########################################################
#
#   Object Declare
#
#########################################################

layout_dic = dict(
    LEFT = 'left',
    RIGHT= 'right',
    UP   = 'up',
    DOWN = 'down',
    HORZ = 'horz',
    VERT = 'vert'
)

class LayoutItem:
    def __init__(self, control, parent, dock):
        self.control = weakref.ref(control)

        self.follow_top     = ('up' in dock) or ('top' in dock)
        self.follow_bottom  = ('down' in dock) or ('bottom' in dock)
        self.follow_left    = ('left' in dock)
        self.follow_right   = ('right' in dock)
        self.follow_vert    = ('vert' in dock)
        self.follow_horz    = ('horz' in dock)
        
        self.region_left = control.left
        self.region_right = parent.width - (control.left + control.width)
        self.region_top = control.top
        self.region_bottom = parent.height - (control.top + control.height)

    def sizing(self, parent):
        control = self.control()
        if not control:
            return

        if self.follow_vert:
            control.top = self.region_top + (parent.height - self.region_top - self.region_bottom - control.height) / 2
        
        if self.follow_horz:
            control.left = self.region_left + (parent.width - self.region_left - self.region_right - control.width) / 2

        if self.follow_top and self.follow_bottom:
            control.height = parent.height - control.top - self.region_bottom
        elif not self.follow_top and self.follow_bottom:
            control.top = parent.height - self.region_bottom - control.height

        if self.follow_left and self.follow_right:
            control.width = parent.width - control.left - self.region_right
        elif not self.follow_left and self.follow_right:
            control.left = parent.width - self.region_right - control.width

class RegionLayoutItem:
    keymap = {
        'l':'left',        
        't':'top',
        'r':'right',
        'b':'bottom',
        'h':'horz',
        'v':'vert',
        'left':'left',
        'top':'top',
        'right':'right',
        'bottom':'bottom',
        'horz':'horz',
        'vert':'vert'
    }
    def __init__(self, control, parent, dock):
        self.control = weakref.ref(control)

        self.center_horz    = ('horz' in dock) and dock['horz']
        self.center_vert    = ('vert' in dock) and dock['vert']
        self.follow_top     = ('top' in dock)
        self.follow_bottom  = ('bottom' in dock)
        self.follow_left    = ('left' in dock)
        self.follow_right   = ('right' in dock)

        for d in dock:
            setattr(self, 'region_'+d, dock[d])

        self.sizing(parent)

    def sizing(self, parent):
        control = self.control()
        if not control:
            return

        if self.center_vert:
            control.top = int( (parent.height - control.height) / 2.0 )
        else:
            if self.follow_top and self.follow_bottom:
                control.top = self.region_top
                control.height = parent.height - self.region_top - self.region_bottom
            elif self.follow_top:
                control.top = self.region_top
            elif self.follow_bottom:
                control.top = parent.height - self.region_bottom - control.height

        if self.center_horz:
            control.left = int( (parent.width - control.width) / 2.0 )
        else:
            if self.follow_left and self.follow_right:
                control.left = self.region_left
                control.width = parent.width - self.region_left - self.region_right
            elif self.follow_left:
                control.left = self.region_left
            elif self.follow_right:
                control.left = parent.width - self.region_right - control.width


class LayoutManager:
    """
    LayoutManager

    LayoutManager must be use in Component, else the bind function will be fail
    """
    def __init__(self):
        self.layout_items = []
        self.autoLayout([], ['Size Change', 'Child Size Change'])
        self.bind('Close', LayoutManager.clear, self)

    def autoLayout(self, attributes, events = []):
        for i in attributes:
            self.changeEvent(i, self.recal, postevent = False)
        for i in events:
            self.bind(i, self.recal, postevent = False)

    def dock_side(self, comp, side):
        self.layout_items.append(LayoutItem(comp, self, side))

    def dock(self, comp, side):
        self.layout_items.append(RegionLayoutItem(comp, self, side))
        
    def undock_side(self, comp):
        self.layout_items = [x for x in self.layout_items if x.control() <> comp]

    def undock(self, comp):
        self.undock_side(comp)

    def layout_remove(self, comp):
        e = [x for x in self.layout_items if x.control() == comp]
        self.layout_items.remove(e)

    def recal(self):
        for e in self.layout_items:
            e.sizing(self)

    def clear(self):
        self.layout_items = []

    def setAttachedProperty(self, prop, **argd):
        global layout_dic
        name = prop['name'].split('.')[-1].lower()
        data = prop['data']
        child = prop['child']
        if name == 'dock_side':
            data = data.strip()
            result = eval(data, layout_dic)            
            self.dock_side(child, result)
        elif name == 'dock':
            docks = data.split(',')
            dock_cmd = {}
            for d in docks:
                dock, region = d.split(':')
                dock = dock.strip().lower()
                try:
                    dock = RegionLayoutItem.keymap[dock]
                except:
                    print '[layout.py] unknown dock name(%s) !!!' %dock
                try:
                    region = eval(region.strip())
                except:
                    if argd.get('parser', None):
                        region = argd['parser'].queryMacroValue(region.strip())
                    else:
                        region = eval(strValue, argd['macro'])
                dock_cmd[dock] = region
            self.dock(child, dock_cmd)
    
#########################################################
#
#   Test This Module
#
#########################################################
def test():
    pass

if __name__ == '__main__':
    test()
