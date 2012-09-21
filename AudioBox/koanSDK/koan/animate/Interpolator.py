# This file was automatically generated by SWIG (http://www.swig.org).
# Version 1.3.31
#
# Don't modify this file, modify the SWIG interface instead.

import _Interpolator
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


class IInterpolatorManager(object):
    """Proxy of C++ IInterpolatorManager class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def Lock(*args):
        """Lock(self)"""
        return _Interpolator.IInterpolatorManager_Lock(*args)

    def Unlock(*args):
        """Unlock(self)"""
        return _Interpolator.IInterpolatorManager_Unlock(*args)

    def Active(*args):
        """Active(self, DWORD time)"""
        return _Interpolator.IInterpolatorManager_Active(*args)

    def AddToActiveList(*args):
        """AddToActiveList(self, IInterpolator pIP)"""
        return _Interpolator.IInterpolatorManager_AddToActiveList(*args)

    __swig_destroy__ = _Interpolator.delete_IInterpolatorManager
    __del__ = lambda self : None;
IInterpolatorManager_swigregister = _Interpolator.IInterpolatorManager_swigregister
IInterpolatorManager_swigregister(IInterpolatorManager)

class IInterpolator(object):
    """Proxy of C++ IInterpolator class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def AddRef(*args):
        """AddRef(self) -> long"""
        return _Interpolator.IInterpolator_AddRef(*args)

    def Release(*args):
        """Release(self) -> long"""
        return _Interpolator.IInterpolator_Release(*args)

    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.IInterpolator_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.IInterpolator_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.IInterpolator_OnActived(*args)

    def GetManager(*args):
        """GetManager(self) -> IInterpolatorManager"""
        return _Interpolator.IInterpolator_GetManager(*args)

    __swig_destroy__ = _Interpolator.delete_IInterpolator
    __del__ = lambda self : None;
IInterpolator_swigregister = _Interpolator.IInterpolator_swigregister
IInterpolator_swigregister(IInterpolator)


def Increment(*args):
  """Increment(long plong) -> long"""
  return _Interpolator.Increment(*args)

def Decrement(*args):
  """Decrement(long plong) -> long"""
  return _Interpolator.Decrement(*args)
class InterpolatorManager(IInterpolatorManager):
    """Proxy of C++ InterpolatorManager class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self) -> InterpolatorManager"""
        this = _Interpolator.new_InterpolatorManager(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_InterpolatorManager
    __del__ = lambda self : None;
    def Lock(*args):
        """Lock(self)"""
        return _Interpolator.InterpolatorManager_Lock(*args)

    def Unlock(*args):
        """Unlock(self)"""
        return _Interpolator.InterpolatorManager_Unlock(*args)

    def Active(*args):
        """Active(self, DWORD time)"""
        return _Interpolator.InterpolatorManager_Active(*args)

    def AddToActiveList(*args):
        """AddToActiveList(self, IInterpolator pIP)"""
        return _Interpolator.InterpolatorManager_AddToActiveList(*args)

InterpolatorManager_swigregister = _Interpolator.InterpolatorManager_swigregister
InterpolatorManager_swigregister(InterpolatorManager)

class InterpolatorBase(IInterpolator):
    """Proxy of C++ InterpolatorBase class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def AddRef(*args):
        """AddRef(self) -> long"""
        return _Interpolator.InterpolatorBase_AddRef(*args)

    def Release(*args):
        """Release(self) -> long"""
        return _Interpolator.InterpolatorBase_Release(*args)

    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.InterpolatorBase_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.InterpolatorBase_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.InterpolatorBase_OnActived(*args)

    def IsConst(*args):
        """IsConst(self) -> bool"""
        return _Interpolator.InterpolatorBase_IsConst(*args)

    def IsStable(*args):
        """IsStable(self) -> bool"""
        return _Interpolator.InterpolatorBase_IsStable(*args)

    def SetAbsStartTime(*args):
        """SetAbsStartTime(self, float startTime)"""
        return _Interpolator.InterpolatorBase_SetAbsStartTime(*args)

    def GetManager(*args):
        """GetManager(self) -> IInterpolatorManager"""
        return _Interpolator.InterpolatorBase_GetManager(*args)

    def __init__(self, *args): 
        """__init__(self) -> InterpolatorBase"""
        this = _Interpolator.new_InterpolatorBase(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_InterpolatorBase
    __del__ = lambda self : None;
    def Reset(*args):
        """Reset(self)"""
        return _Interpolator.InterpolatorBase_Reset(*args)

    def GetInterface(*args):
        """GetInterface(self) -> LPIInterpolator"""
        return _Interpolator.InterpolatorBase_GetInterface(*args)

InterpolatorBase_swigregister = _Interpolator.InterpolatorBase_swigregister
InterpolatorBase_swigregister(InterpolatorBase)

class NullInterpolator(InterpolatorBase):
    """Proxy of C++ NullInterpolator class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def SetValue(*args):
        """SetValue(self, float v)"""
        return _Interpolator.NullInterpolator_SetValue(*args)

    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.NullInterpolator_CalValue(*args)

    def __init__(self, *args): 
        """__init__(self) -> NullInterpolator"""
        this = _Interpolator.new_NullInterpolator(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_NullInterpolator
    __del__ = lambda self : None;
NullInterpolator_swigregister = _Interpolator.NullInterpolator_swigregister
NullInterpolator_swigregister(NullInterpolator)

class LinearInterpolator(InterpolatorBase):
    """Proxy of C++ LinearInterpolator class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, bool loop, float len) -> LinearInterpolator"""
        this = _Interpolator.new_LinearInterpolator(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_LinearInterpolator
    __del__ = lambda self : None;
    def AddValues(*args):
        """AddValues(self, float d, float v)"""
        return _Interpolator.LinearInterpolator_AddValues(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.LinearInterpolator_OnActived(*args)

    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.LinearInterpolator_CalValue(*args)

    def Reset(*args):
        """Reset(self)"""
        return _Interpolator.LinearInterpolator_Reset(*args)

LinearInterpolator_swigregister = _Interpolator.LinearInterpolator_swigregister
LinearInterpolator_swigregister(LinearInterpolator)

class SpringInterpolator(InterpolatorBase):
    """Proxy of C++ SpringInterpolator class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, float len, float fm, float to) -> SpringInterpolator"""
        this = _Interpolator.new_SpringInterpolator(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_SpringInterpolator
    __del__ = lambda self : None;
    def Reset(*args):
        """Reset(self)"""
        return _Interpolator.SpringInterpolator_Reset(*args)

    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.SpringInterpolator_CalValue(*args)

SpringInterpolator_swigregister = _Interpolator.SpringInterpolator_swigregister
SpringInterpolator_swigregister(SpringInterpolator)

class TargetInterpolator(InterpolatorBase):
    """Proxy of C++ TargetInterpolator class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, char type, float len, float fm, float to) -> TargetInterpolator"""
        this = _Interpolator.new_TargetInterpolator(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_TargetInterpolator
    __del__ = lambda self : None;
    def Reset(*args):
        """Reset(self)"""
        return _Interpolator.TargetInterpolator_Reset(*args)

    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.TargetInterpolator_CalValue(*args)

    def ResetTarget(*args):
        """
        ResetTarget(self, float len, float to, bool useAbsStartTime=False, float startTime=0)
        ResetTarget(self, float len, float to, bool useAbsStartTime=False)
        ResetTarget(self, float len, float to)
        """
        return _Interpolator.TargetInterpolator_ResetTarget(*args)

    def ResetTargetNow(*args):
        """ResetTargetNow(self, float len, float to, float time)"""
        return _Interpolator.TargetInterpolator_ResetTargetNow(*args)

    def AssignValue(*args):
        """AssignValue(self, float value)"""
        return _Interpolator.TargetInterpolator_AssignValue(*args)

    def ForceAssignValue(*args):
        """ForceAssignValue(self, float value)"""
        return _Interpolator.TargetInterpolator_ForceAssignValue(*args)

    def Stop(*args):
        """Stop(self)"""
        return _Interpolator.TargetInterpolator_Stop(*args)

    def QueryValue(*args):
        """QueryValue(self) -> float"""
        return _Interpolator.TargetInterpolator_QueryValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.TargetInterpolator_OnActived(*args)

TargetInterpolator_swigregister = _Interpolator.TargetInterpolator_swigregister
TargetInterpolator_swigregister(TargetInterpolator)

class SinInterpolator(InterpolatorBase):
    """Proxy of C++ SinInterpolator class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, float len) -> SinInterpolator"""
        this = _Interpolator.new_SinInterpolator(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_SinInterpolator
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.SinInterpolator_CalValue(*args)

SinInterpolator_swigregister = _Interpolator.SinInterpolator_swigregister
SinInterpolator_swigregister(SinInterpolator)

class FunctionTransform(InterpolatorBase):
    """Proxy of C++ FunctionTransform class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, IInterpolator FuncInterpolator, IInterpolator ParamInterpolator) -> FunctionTransform"""
        this = _Interpolator.new_FunctionTransform(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_FunctionTransform
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.FunctionTransform_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.FunctionTransform_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.FunctionTransform_OnActived(*args)

FunctionTransform_swigregister = _Interpolator.FunctionTransform_swigregister
FunctionTransform_swigregister(FunctionTransform)

class LinearTransform(InterpolatorBase):
    """Proxy of C++ LinearTransform class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, IInterpolator pInterpolator, float scale, float transition) -> LinearTransform"""
        this = _Interpolator.new_LinearTransform(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_LinearTransform
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.LinearTransform_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.LinearTransform_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.LinearTransform_OnActived(*args)

LinearTransform_swigregister = _Interpolator.LinearTransform_swigregister
LinearTransform_swigregister(LinearTransform)

class PolynomialTransform(InterpolatorBase):
    """Proxy of C++ PolynomialTransform class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """
        __init__(self, IInterpolator pInterpolator, float a0, float a1, float a2, 
            float a3) -> PolynomialTransform
        """
        this = _Interpolator.new_PolynomialTransform(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_PolynomialTransform
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.PolynomialTransform_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.PolynomialTransform_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.PolynomialTransform_OnActived(*args)

PolynomialTransform_swigregister = _Interpolator.PolynomialTransform_swigregister
PolynomialTransform_swigregister(PolynomialTransform)

class KeyframeValues(object):
    """Proxy of C++ KeyframeValues class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self) -> KeyframeValues"""
        this = _Interpolator.new_KeyframeValues(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_KeyframeValues
    __del__ = lambda self : None;
    def StartSetValues(*args):
        """StartSetValues(self, float keyStart, float keyEnd, bool loop)"""
        return _Interpolator.KeyframeValues_StartSetValues(*args)

    def AddValue(*args):
        """AddValue(self, float value)"""
        return _Interpolator.KeyframeValues_AddValue(*args)

    def Transform(*args):
        """Transform(self, float input) -> float"""
        return _Interpolator.KeyframeValues_Transform(*args)

    def AddRef(*args):
        """AddRef(self) -> long"""
        return _Interpolator.KeyframeValues_AddRef(*args)

    def Release(*args):
        """Release(self) -> long"""
        return _Interpolator.KeyframeValues_Release(*args)

KeyframeValues_swigregister = _Interpolator.KeyframeValues_swigregister
KeyframeValues_swigregister(KeyframeValues)

class KeyframeTransform(InterpolatorBase):
    """Proxy of C++ KeyframeTransform class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, IInterpolator pInterpolator, KeyframeValues keyvalues) -> KeyframeTransform"""
        this = _Interpolator.new_KeyframeTransform(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_KeyframeTransform
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.KeyframeTransform_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.KeyframeTransform_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.KeyframeTransform_OnActived(*args)

KeyframeTransform_swigregister = _Interpolator.KeyframeTransform_swigregister
KeyframeTransform_swigregister(KeyframeTransform)

class AnimValue(InterpolatorBase):
    """Proxy of C++ AnimValue class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, InterpolatorBase refobj) -> AnimValue"""
        this = _Interpolator.new_AnimValue(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_AnimValue
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.AnimValue_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.AnimValue_GetValue(*args)

AnimValue_swigregister = _Interpolator.AnimValue_swigregister
AnimValue_swigregister(AnimValue)

class FollowAnimValue(InterpolatorBase):
    """Proxy of C++ FollowAnimValue class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, InterpolatorBase refobj, float valuediff) -> FollowAnimValue"""
        this = _Interpolator.new_FollowAnimValue(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_FollowAnimValue
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.FollowAnimValue_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.FollowAnimValue_GetValue(*args)

FollowAnimValue_swigregister = _Interpolator.FollowAnimValue_swigregister
FollowAnimValue_swigregister(FollowAnimValue)

class AddAnimValue(InterpolatorBase):
    """Proxy of C++ AddAnimValue class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, InterpolatorBase a, InterpolatorBase b) -> AddAnimValue"""
        this = _Interpolator.new_AddAnimValue(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_AddAnimValue
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.AddAnimValue_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.AddAnimValue_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.AddAnimValue_OnActived(*args)

AddAnimValue_swigregister = _Interpolator.AddAnimValue_swigregister
AddAnimValue_swigregister(AddAnimValue)

class SubAnimValue(InterpolatorBase):
    """Proxy of C++ SubAnimValue class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, InterpolatorBase a, InterpolatorBase b) -> SubAnimValue"""
        this = _Interpolator.new_SubAnimValue(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_SubAnimValue
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.SubAnimValue_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.SubAnimValue_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.SubAnimValue_OnActived(*args)

SubAnimValue_swigregister = _Interpolator.SubAnimValue_swigregister
SubAnimValue_swigregister(SubAnimValue)

class MulAnimValue(InterpolatorBase):
    """Proxy of C++ MulAnimValue class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, InterpolatorBase a, InterpolatorBase b) -> MulAnimValue"""
        this = _Interpolator.new_MulAnimValue(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_MulAnimValue
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.MulAnimValue_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.MulAnimValue_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.MulAnimValue_OnActived(*args)

MulAnimValue_swigregister = _Interpolator.MulAnimValue_swigregister
MulAnimValue_swigregister(MulAnimValue)

class DivAnimValue(InterpolatorBase):
    """Proxy of C++ DivAnimValue class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, InterpolatorBase a, InterpolatorBase b) -> DivAnimValue"""
        this = _Interpolator.new_DivAnimValue(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _Interpolator.delete_DivAnimValue
    __del__ = lambda self : None;
    def CalValue(*args):
        """CalValue(self, DWORD time) -> bool"""
        return _Interpolator.DivAnimValue_CalValue(*args)

    def GetValue(*args):
        """GetValue(self) -> float"""
        return _Interpolator.DivAnimValue_GetValue(*args)

    def OnActived(*args):
        """OnActived(self, DWORD time)"""
        return _Interpolator.DivAnimValue_OnActived(*args)

DivAnimValue_swigregister = _Interpolator.DivAnimValue_swigregister
DivAnimValue_swigregister(DivAnimValue)


