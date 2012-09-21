#########################################################
#
#   Enumerate Variable
#
#########################################################

import traceback
DMAP = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'TAB']

#########################################################
#
#   Object Declare
#
#########################################################

class ArrowControl(object):
    """
    to control when arrow keys(up, down, left, right) pressed,
    how the focused child compenent change
    ex:
    ArrowControl may defined
    ------------------
    |  -----  -----  |  press right to move focus from A to B
    |  | A |  | B |  |  press down to move focus from B to D
    |  -----  -----  |  press left to move focus from D to C
    |  -----  -----  |  press up to move focus from C to A
    |  | C |  | D |  |
    |  -----  -----  |
    ------------------

    ArrowControl save the rules in a map that looks like:
    {Component1 : {'DOWN': Component2, 'UP' : Component3},
     Component2 : {'DOWN': Component3, 'UP' : Component1},
     Component3 : {'DOWN': Component1, 'UP' : Component2}}

    Event:
        Not Define Arrow : sent when a unhandled arrow key pressed

    @ivar arrowMap: the mapping rules to change focus
    """
    def __init__(self):
        self.arrowMap = {}
        self.bind('Close', self.clearDirmap)

    def getFocusControl(self):
        """
        get the component that are focused and have a mapping rule

        @rtype: Component
        """
        return [x for x in self.arrowMap.keys() if x and x.isFocused()]

    def clearDirmap(self):
        """
        clear arrow map

        @rtype: None
        """
        self.arrowMap = {}

    def dirmap(self, comp, **args):
        """
        set direction to next focused child mapping

        setting that if comp is the focused child,
        how arrow key change the focus to another child

        @param comp: the child compenent to set rule
        @param args: map from arrow key (UP,DOWN,LEFT,RIGHT) to next focused child
        @rtype: None
        """
        if not comp in self.arrowMap:
            self.arrowMap[comp] = {}

        d = self.arrowMap[comp]
        for e in args.keys():
            if e in DMAP:
                if isinstance(args[e], list):
                    d[e] = args[e]
                else:
                    d[e] = [args[e]]
        
    def clear(self):
        """
        clear the map rules

        @rtype: None
        """
        self.arrowMap = {}

    def trigger(self, focusedComps, dir):
        """
        trigger to change focused child

        @param focusedComps: the component that are focused now
        @param dir: the arrow key pressed, one of (UP, DOWN, LEFT, RIGHT)
        @return: if the focused component if changed
        @rtype: boolean
        """
        for c in focusedComps:
            if self.__trigger(c, dir):
                return True
        return False

    def __trigger(self, focusedComp, dir):
        # skip invisible components
        # avoid looping
        if not focusedComp:
            self.invoke('Not Define Arrow', dir)
            return False

        wont = []
        focusedComps = [focusedComp]

        # Example:
        #        
        # (0) enabled
        # (X) disabled
        #
        # a(O)->b(X)->d(X)
        #     ->c(X)->e(O)
        #
        # Right from a, e is focused
        
        while True:
            nextComps2 = []
            
            for focusedComp in focusedComps:
                try:
                    d = self.arrowMap[focusedComp]
                    nexts = d[dir]
                except KeyError:
                    #print 'Component not define this arrow'
                    self.invoke('Not Define Arrow', dir)
                    return False
                else:
                    for next in nexts:
                        if next:
                            if next in wont: # recursive circle, damm
                                break
        
                            if next.enabled and next.visible:
                                next.setFocus(dir)
                                return True
                            else:
                                nextComps2.append(next)
                    
                    wont.append(focusedComp)
            
            if not nextComps2:
                break
            
            focusedComps = nextComps2
            
        return False

    def setCommandProperty(self, prop, **keyword):
        name = prop['name']
        if name.lower() == 'dirmap':
            try:
                attrs = prop['attrs']
                alias = prop['alias']
                source = None
                if 'from' in attrs.getQNames():
                    fr = attrs.getValueByQName('from')
                    try:
                        try:
                            source = self.getPathObject(fr.split('.'), prop['root'])
                        except:
                            source = alias[fr]
                    except:
                        print "[KXML] dirmap@from: no such control %s !!!" % fr
                else:
                    print "[KXML] dirmap: expected 'from' tag !!!"
    
                parm = {}
                for d in attrs.getQNames():                
                    if d.upper() in ['LEFT', 'RIGHT', 'UP', 'DOWN']:
                        lst = attrs.getValueByQName(d).split(',')
                        d = str(d.upper())
                        
                        for x in lst:
                            x = x.strip()
                            tar = None
                            try:
                                try:
                                    target = self.getPathObject(x.split('.'), prop['root'])
                                except:
                                    target = alias[x]
                            except:
                                print "[KXML] dirmap@%s: no such control %s !!!" %(d, x)
                
                            if target:
                                if d not in parm:
                                    parm[d] = []
                                parm[d].append(target)
                if source:
                    self.dirmap(source, **parm)
                    pass
            except:
                traceback.print_exc()
                print '[arrowctrl] setCommandProperty !!!'
