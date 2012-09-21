# This file was automatically generated by SWIG (http://www.swig.org).
# Version 1.3.31
#
# Don't modify this file, modify the SWIG interface instead.

import _wingdi
import new
new_instancemethod = new.instancemethod
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'PySwigObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


def _swig_setattr_nondynamic_method(set):
    def set_attr(self,name,value):
        if (name == "thisown"): return self.this.own(value)
        if hasattr(self,name) or (name == "this"):
            set(self,name,value)
        else:
            raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr


class KClock(object):
    """Proxy of C++ KClock class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self) -> KClock"""
        this = _wingdi.new_KClock(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _wingdi.delete_KClock
    __del__ = lambda self : None;
    def GetTime(*args):
        """GetTime(self) -> double"""
        return _wingdi.KClock_GetTime(*args)

    def Pause(*args):
        """Pause(self)"""
        return _wingdi.KClock_Pause(*args)

    def Reset(*args):
        """Reset(self)"""
        return _wingdi.KClock_Reset(*args)

    def Step(*args):
        """
        Step(self, double step=0.0)
        Step(self)
        """
        return _wingdi.KClock_Step(*args)

KClock_swigregister = _wingdi.KClock_swigregister
KClock_swigregister(KClock)

class MainWnd(object):
    """Proxy of C++ MainWnd class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self) -> MainWnd"""
        this = _wingdi.new_MainWnd(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _wingdi.delete_MainWnd
    __del__ = lambda self : None;
    def GetInstance(*args):
        """GetInstance(self) -> HINSTANCE"""
        return _wingdi.MainWnd_GetInstance(*args)

    def GetWindowHandle(*args):
        """GetWindowHandle(self) -> LONG"""
        return _wingdi.MainWnd_GetWindowHandle(*args)

    def GetWnd(*args):
        """GetWnd(self) -> HWND"""
        return _wingdi.MainWnd_GetWnd(*args)

    def GetKoanBoxWnd(*args):
        """GetKoanBoxWnd(self) -> HWND"""
        return _wingdi.MainWnd_GetKoanBoxWnd(*args)

    def Create(*args):
        """
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True, bool resize=True, 
            bool minmax=True, bool blur=False, 
            bool frame=False, bool defaultMaximize=False, 
            bool layeredWindow=False, bool isKoanBox=False, 
            bool isRUI=False)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True, bool resize=True, 
            bool minmax=True, bool blur=False, 
            bool frame=False, bool defaultMaximize=False, 
            bool layeredWindow=False, bool isKoanBox=False)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True, bool resize=True, 
            bool minmax=True, bool blur=False, 
            bool frame=False, bool defaultMaximize=False, 
            bool layeredWindow=False)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True, bool resize=True, 
            bool minmax=True, bool blur=False, 
            bool frame=False, bool defaultMaximize=False)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True, bool resize=True, 
            bool minmax=True, bool blur=False, 
            bool frame=False)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True, bool resize=True, 
            bool minmax=True, bool blur=False)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True, bool resize=True, 
            bool minmax=True)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True, bool resize=True)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False, 
            bool border=True)
        Create(self, WCHAR classname, WCHAR title, int w, int h, bool useCaptionbar=False)
        Create(self, WCHAR classname, WCHAR title, int w, int h)
        """
        return _wingdi.MainWnd_Create(*args)

    def CreateDummy(*args):
        """CreateDummy(self)"""
        return _wingdi.MainWnd_CreateDummy(*args)

    def Close(*args):
        """Close(self)"""
        return _wingdi.MainWnd_Close(*args)

    def NotifyClose(*args):
        """NotifyClose(self)"""
        return _wingdi.MainWnd_NotifyClose(*args)

    def SetRatio(*args):
        """SetRatio(self, float f, int w)"""
        return _wingdi.MainWnd_SetRatio(*args)

    def SetTimeResolution(*args):
        """SetTimeResolution(self, int res)"""
        return _wingdi.MainWnd_SetTimeResolution(*args)

    def EnableDWMBlurBehind(*args):
        """EnableDWMBlurBehind(self, bool enabled, bool blur)"""
        return _wingdi.MainWnd_EnableDWMBlurBehind(*args)

    def SetHook(*args):
        """SetHook(self, PyObject ?, IWinProcHook ?)"""
        return _wingdi.MainWnd_SetHook(*args)

    def DoDragDrop(*args):
        """DoDragDrop(self, WCHAR files, int lens)"""
        return _wingdi.MainWnd_DoDragDrop(*args)

    def Show(*args):
        """Show(self)"""
        return _wingdi.MainWnd_Show(*args)

    def Hide(*args):
        """Hide(self)"""
        return _wingdi.MainWnd_Hide(*args)

    def Focus(*args):
        """Focus(self)"""
        return _wingdi.MainWnd_Focus(*args)

    def Topmost(*args):
        """Topmost(self, bool v)"""
        return _wingdi.MainWnd_Topmost(*args)

    def IsVisible(*args):
        """IsVisible(self) -> bool"""
        return _wingdi.MainWnd_IsVisible(*args)

    def IsFullScreen(*args):
        """IsFullScreen(self) -> bool"""
        return _wingdi.MainWnd_IsFullScreen(*args)

    def IsMinimize(*args):
        """IsMinimize(self) -> bool"""
        return _wingdi.MainWnd_IsMinimize(*args)

    def FullScreen(*args):
        """
        FullScreen(self, bool v, bool show=True)
        FullScreen(self, bool v)
        """
        return _wingdi.MainWnd_FullScreen(*args)

    def MinimizeScreen(*args):
        """MinimizeScreen(self, bool v)"""
        return _wingdi.MainWnd_MinimizeScreen(*args)

    def SetIcon(*args):
        """SetIcon(self, WCHAR strIcon)"""
        return _wingdi.MainWnd_SetIcon(*args)

    def SetMinimalSize(*args):
        """SetMinimalSize(self, int w, int h)"""
        return _wingdi.MainWnd_SetMinimalSize(*args)

    def SetHitCursor(*args):
        """SetHitCursor(self, bool v)"""
        return _wingdi.MainWnd_SetHitCursor(*args)

    def EnterMovingMode(*args):
        """EnterMovingMode(self)"""
        return _wingdi.MainWnd_EnterMovingMode(*args)

    def SetCursor(*args):
        """SetCursor(self, WCHAR strCursor)"""
        return _wingdi.MainWnd_SetCursor(*args)

    def ShowCursor(*args):
        """ShowCursor(self, bool v)"""
        return _wingdi.MainWnd_ShowCursor(*args)

    def SetCapture(*args):
        """SetCapture(self, bool v)"""
        return _wingdi.MainWnd_SetCapture(*args)

    def ShowWindow(*args):
        """ShowWindow(self, HWND hWnd, bool v)"""
        return _wingdi.MainWnd_ShowWindow(*args)

    def SetParent(*args):
        """SetParent(self, LONG hWnd)"""
        return _wingdi.MainWnd_SetParent(*args)

    def BeginPuncture(*args):
        """BeginPuncture(self)"""
        return _wingdi.MainWnd_BeginPuncture(*args)

    def EndPuncture(*args):
        """EndPuncture(self)"""
        return _wingdi.MainWnd_EndPuncture(*args)

    def AddPuncture(*args):
        """AddPuncture(self, int priority, float x, float y, float w, float h)"""
        return _wingdi.MainWnd_AddPuncture(*args)

    def AddPunctureRegion(*args):
        """
        AddPunctureRegion(self, int priority, float x, float y, float w, float h, PyObject rectList, 
            float xPixelUnit, float yPixelUnit)
        """
        return _wingdi.MainWnd_AddPunctureRegion(*args)

    def SetWindowRegion(*args):
        """
        SetWindowRegion(self, float x, float y, float w, float h, PyObject rectList, 
            float xPixelUnit, float yPixelUnit)
        """
        return _wingdi.MainWnd_SetWindowRegion(*args)

    def SetLayeredWindow(*args):
        """SetLayeredWindow(self, bool layered)"""
        return _wingdi.MainWnd_SetLayeredWindow(*args)

    def SetLayeredWindowAlpha(*args):
        """SetLayeredWindowAlpha(self, float alpha)"""
        return _wingdi.MainWnd_SetLayeredWindowAlpha(*args)

    def SetWindowText(*args):
        """SetWindowText(self, WCHAR str)"""
        return _wingdi.MainWnd_SetWindowText(*args)

    def GetClientSize(*args):
        """
        GetClientSize(self, bool normal=False) -> PyObject
        GetClientSize(self) -> PyObject
        """
        return _wingdi.MainWnd_GetClientSize(*args)

    def GetWindowSize(*args):
        """
        GetWindowSize(self, bool normal=False) -> PyObject
        GetWindowSize(self) -> PyObject
        """
        return _wingdi.MainWnd_GetWindowSize(*args)

    def GetWindowPos(*args):
        """
        GetWindowPos(self, bool normal=False) -> PyObject
        GetWindowPos(self) -> PyObject
        """
        return _wingdi.MainWnd_GetWindowPos(*args)

    def GetDesktopSize(*args):
        """GetDesktopSize(self) -> PyObject"""
        return _wingdi.MainWnd_GetDesktopSize(*args)

    def SetWindowPos(*args):
        """SetWindowPos(self, int x, int y)"""
        return _wingdi.MainWnd_SetWindowPos(*args)

    def SetWindowSize(*args):
        """SetWindowSize(self, int x, int y)"""
        return _wingdi.MainWnd_SetWindowSize(*args)

    def SetClientSize(*args):
        """SetClientSize(self, int x, int y)"""
        return _wingdi.MainWnd_SetClientSize(*args)

    def AttachChild(*args):
        """
        AttachChild(self, HWND hWnd, int priority=99)
        AttachChild(self, HWND hWnd)
        """
        return _wingdi.MainWnd_AttachChild(*args)

    def AttachChild2(*args):
        """AttachChild2(self, HWND hWnd)"""
        return _wingdi.MainWnd_AttachChild2(*args)

    def DetachChild(*args):
        """DetachChild(self, HWND hWnd)"""
        return _wingdi.MainWnd_DetachChild(*args)

    def SetChildPos(*args):
        """SetChildPos(self, HWND hWnd, int x, int y, int width, int height)"""
        return _wingdi.MainWnd_SetChildPos(*args)

    def SetCore(*args):
        """SetCore(self, PyObject core)"""
        return _wingdi.MainWnd_SetCore(*args)

    def Dirty(*args):
        """Dirty(self)"""
        return _wingdi.MainWnd_Dirty(*args)

    def ShowMessageBox(*args):
        """ShowMessageBox(self, WCHAR title, WCHAR message)"""
        return _wingdi.MainWnd_ShowMessageBox(*args)

    def JScript(*args):
        """JScript(self, char script) -> PyObject"""
        return _wingdi.MainWnd_JScript(*args)

    def RegisterKoanBox(*args):
        """RegisterKoanBox(self, int hwnd)"""
        return _wingdi.MainWnd_RegisterKoanBox(*args)

    def UnRegisterKoanBox(*args):
        """UnRegisterKoanBox(self)"""
        return _wingdi.MainWnd_UnRegisterKoanBox(*args)

    def OnCloseKoanBox(*args):
        """OnCloseKoanBox(self)"""
        return _wingdi.MainWnd_OnCloseKoanBox(*args)

    def EnableMCE2Foot(*args):
        """EnableMCE2Foot(self, bool ?)"""
        return _wingdi.MainWnd_EnableMCE2Foot(*args)

MainWnd_swigregister = _wingdi.MainWnd_swigregister
MainWnd_swigregister(MainWnd)

class CKoanDatePicker(object):
    """Proxy of C++ CKoanDatePicker class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, PyObject pCallback, bool longFormat) -> CKoanDatePicker"""
        this = _wingdi.new_CKoanDatePicker(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _wingdi.delete_CKoanDatePicker
    __del__ = lambda self : None;
    def Show(*args):
        """Show(self, bool ?)"""
        return _wingdi.CKoanDatePicker_Show(*args)

    def GetHWND(*args):
        """GetHWND(self) -> HWND"""
        return _wingdi.CKoanDatePicker_GetHWND(*args)

    def GetDate(*args):
        """GetDate(self) -> PyObject"""
        return _wingdi.CKoanDatePicker_GetDate(*args)

    def SetDate(*args):
        """SetDate(self, int year, int month, int day)"""
        return _wingdi.CKoanDatePicker_SetDate(*args)

    def Focus(*args):
        """Focus(self)"""
        return _wingdi.CKoanDatePicker_Focus(*args)

    def SetFont(*args):
        """SetFont(self, wchar_t szFont, UINT uiFontSize)"""
        return _wingdi.CKoanDatePicker_SetFont(*args)

CKoanDatePicker_swigregister = _wingdi.CKoanDatePicker_swigregister
CKoanDatePicker_swigregister(CKoanDatePicker)


def SetThreadPriority(*args):
  """SetThreadPriority(WCHAR priority)"""
  return _wingdi.SetThreadPriority(*args)

def GetThreadPriority(*args):
  """GetThreadPriority() -> char"""
  return _wingdi.GetThreadPriority(*args)

def InitThread(*args):
  """InitThread()"""
  return _wingdi.InitThread(*args)

def UninitThread(*args):
  """UninitThread()"""
  return _wingdi.UninitThread(*args)

def SetThreadName(*args):
  """SetThreadName(WCHAR name)"""
  return _wingdi.SetThreadName(*args)

def ShowMessageBox(*args):
  """ShowMessageBox(WCHAR message)"""
  return _wingdi.ShowMessageBox(*args)

def CreateLink(*args):
  """CreateLink(WCHAR lpszPathObj, WCHAR lpszPathLink) -> BOOL"""
  return _wingdi.CreateLink(*args)

def GetLink(*args):
  """GetLink(WCHAR lpszPathLink) -> PyObject"""
  return _wingdi.GetLink(*args)

def Run(*args):
  """Run(DWORD id) -> PyObject"""
  return _wingdi.Run(*args)

def LeaveLoop(*args):
  """LeaveLoop(DWORD id)"""
  return _wingdi.LeaveLoop(*args)

def PeekMsg(*args):
  """PeekMsg()"""
  return _wingdi.PeekMsg(*args)
class ProxyWnd(object):
    """Proxy of C++ ProxyWnd class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, HWND ?, PyObject core) -> ProxyWnd"""
        this = _wingdi.new_ProxyWnd(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _wingdi.delete_ProxyWnd
    __del__ = lambda self : None;
    def SetCore(*args):
        """SetCore(self, PyObject core)"""
        return _wingdi.ProxyWnd_SetCore(*args)

ProxyWnd_swigregister = _wingdi.ProxyWnd_swigregister
ProxyWnd_swigregister(ProxyWnd)

def DumpMessage(*args):
  """
    DumpMessage(bool waitOne=True) -> PyObject
    DumpMessage() -> PyObject
    """
  return _wingdi.DumpMessage(*args)

class CKoanEdit(object):
    """Proxy of C++ CKoanEdit class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(self, PyObject pCallback, wchar_t text, bool bMultiline=False, 
            char align='L', bool bVScroll=False, bool bHScroll=False) -> CKoanEdit
        __init__(self, PyObject pCallback, wchar_t text, bool bMultiline=False, 
            char align='L', bool bVScroll=False) -> CKoanEdit
        __init__(self, PyObject pCallback, wchar_t text, bool bMultiline=False, 
            char align='L') -> CKoanEdit
        __init__(self, PyObject pCallback, wchar_t text, bool bMultiline=False) -> CKoanEdit
        __init__(self, PyObject pCallback, wchar_t text) -> CKoanEdit
        """
        this = _wingdi.new_CKoanEdit(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _wingdi.delete_CKoanEdit
    __del__ = lambda self : None;
    def Show(*args):
        """Show(self, bool ?)"""
        return _wingdi.CKoanEdit_Show(*args)

    def Focus(*args):
        """Focus(self)"""
        return _wingdi.CKoanEdit_Focus(*args)

    def GetHWND(*args):
        """GetHWND(self) -> HWND"""
        return _wingdi.CKoanEdit_GetHWND(*args)

    def GetText(*args):
        """GetText(self) -> PyObject"""
        return _wingdi.CKoanEdit_GetText(*args)

    def SetBgColor(*args):
        """SetBgColor(self, int a, int r, int g, int b)"""
        return _wingdi.CKoanEdit_SetBgColor(*args)

    def SetFontColor(*args):
        """SetFontColor(self, int a, int r, int g, int b)"""
        return _wingdi.CKoanEdit_SetFontColor(*args)

    def SetText(*args):
        """SetText(self, wchar_t szText)"""
        return _wingdi.CKoanEdit_SetText(*args)

    def SetFont(*args):
        """SetFont(self, wchar_t szFont, UINT uiFontSize)"""
        return _wingdi.CKoanEdit_SetFont(*args)

    def SetMultiLine(*args):
        """SetMultiLine(self, bool bMultiline)"""
        return _wingdi.CKoanEdit_SetMultiLine(*args)

    def SetLimit(*args):
        """SetLimit(self, int limit)"""
        return _wingdi.CKoanEdit_SetLimit(*args)

CKoanEdit_swigregister = _wingdi.CKoanEdit_swigregister
CKoanEdit_swigregister(CKoanEdit)


