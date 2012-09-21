"""
koan: CyberLink 3D UI Engine

@undocumented: memusage
@undocumented: __version__, __date__, __author__, __credits__, langloader
"""

__version__ = "$Revision: 1.20 $"
__date__ = "$Date: 2006/01/27 04:13:50 $"
__author__ = "CyberLink Co,."
__credits__ = "CyberLink Co,."

version = "4.0"

#-----------------------------------------------------------------------
# import python component
#-----------------------------------------------------------------------
import os
import sys
import gc
import time
import traceback
import types
gc.enable()

#-----------------------------------------------------------------------
# koan system variable
#-----------------------------------------------------------------------
if os.name <> 'posix':
    isDebug = ('DEBUG' in sys.argv) or ('HAPCLIENT' in os.environ and os.environ['HAPCLIENT'] == 'Debuging') and ('nodebug' not in sys.argv)
else:
    isDebug = ('DEBUG' in sys.argv)

isProfile = ('profile' in sys.argv)

#if isDebug:
#    gc.set_debug(gc.DEBUG_LEAK)

isKoanBox = ('KOANBOX' in sys.argv)     # koan box only run on single window mode
isRUI = ('RUI' in sys.argv)
isCompatibleMode = ('SAFE' in sys.argv)
isTouchStone = 'TOUCHSTONE' in sys.argv
isTraceLeak = 'TRACELEAK' in sys.argv or 'traceleak' in sys.argv

def optimize(obj): # default do nothing
    pass

def __useOptimal():
    if sys.platform == 'win32':
        try:
            import platform
            return (platform.reg.GetRegistry("optimal", 0) != 0)
        except:
            traceback.print_exc()
            return False
    else:
        return 'OPTIMAL' in sys.argv

if __useOptimal():
    try:
        import psyco

        def optimize(obj):
            "obj: class, obj, or function"
            psyco.bind(obj)

        print 'Enable Optimal'
    except:
        print 'Enable Optimal but no find psyco'
        pass

#-----------------------------------------------------------------------
# import component
#-----------------------------------------------------------------------

import setting
import platform
import anim
from action     import Action
from event      import EventManager, Switch

from rectangle  import Rectangle
from arrowctrl  import ArrowControl
from layout     import LayoutManager
import kernel
import draw

config              = setting.Config()

def NullTranslate(s):
    return ToUnicode(s)

def GetTrans(domain):
    return NullTranslate

ToUnicode           = platform.ToUnicode
clock               = platform.KClock()
GetTime             = clock.GetTime
MakePath            = platform.MakePath

run                 = platform.Run
leaveloop           = platform.LeaveLoop
dumpmessage         = platform.DumpMessage
peekmessage         = platform.PeekMsg

########################################################################

# application
#animManager         = anim.Manager()
windows             = []                # all koan window will be saved here

# render
useAnimation        = True
is3D                = True
frameControl        = False

dummy               = None
error               = None

########################################################################
def init(error_callback = None):
    global dummy
    global animManager
    global error
    animManager = anim.Manager()
    dummy = kernel.Kernel()
    dummy.Init()
    error = error_callback


def final():
    global dummy
    global windows
    global animManager
    global config
    global time
    
    if dummy:
        dummy.exit()
        dummy = None

    if animManager:
        animManager.pooling()
        animManager = Null
        
    time = None
    error = None
    #gc.collect()
    
    config.sync()

def traceLeak():
    if isTraceLeak:
        from pprint import pprint
        import event
        print '============ leak objects ============='
        pprint(event.evtobjs)
        print '======================================='
        
        for o in event.evtobjs:
            if o():
                print '------- %s ---------' %o().__class__
                pprint(gc.get_referrers(o()))
                print '------------------------------'

#----------------------------------------------------------------
# font
#----------------------------------------------------------------
# multi-language
fonts               = {}
defaultFont         = 'Trebuchet MS'
defaultFontSize     = 30
defaultTextAlign    = 'L'
useRTL              = False

def font(str):
    if fonts.has_key(str):
        return fonts[str][0]
    else:
        return defaultFont

def fontsize(str):
    if fonts.has_key(str):
        return fonts[str][1]
    else:
        return defaultFontSize

"""
    Arial
    Arial*Bold/Underline/Strikeout/Italic/BoldItalic
    CreateFont('Arial', 'Underline', effect = 'Broad', depth = 3, bgcolor = '255, 255, 255, 255')
"""

def CreateFont(*argl, **arg):
    ret = ''
    if len(argl) not in [1, 2]:
        raise ValueError, 'CreateFont must be with name and style'

    ret = argl[0]
    if len(argl) == 2:
        ret += '*'
        ret += argl[1]

    for i in arg.keys():
        ret += '&%s = %s' % (i, str(arg[i]))

    return ret


from koan.platform import ShowMessageBox

print '-----------------------------------------'
print 'Koan ' + version
print 'DEBUG %s' %str(isDebug)
print 'PROFILE %s' %str(isProfile)
print 'KOANBOX %s' %str(isKoanBox)
print 'SAFE %s' %str(isCompatibleMode)
print 'Import koan from', __path__
print '-----------------------------------------'

from null import NullObj
Null = NullObj()


def Autolock():
    # TODO: not used now, remove it
    return Null
    
#----------------------------------------------------------------
# koan assertion
#----------------------------------------------------------------
assertMode = platform.reg.GetRegistry("assert", 0)
def Assert(expression):
    '''
    key:
        hkey_local_machine\Software\CyberLink\koan\assert
    value:
        0: release (don't do any thing)
        1: print error msg and continue
        2: raise exception
    '''
    global assertMode
    if expression:
        return
    if assertMode == 1:
        traceback.print_stack()
    elif assertMode == 2:
        raise AssertionError


#----------------------------------------------------------------
# touch stone
#----------------------------------------------------------------
if isTouchStone:
    from touchstone import startTSRecording
    from touchstone import recordKeyinCmd
    from touchstone import recordComment
    from touchstone import stopTSRecording