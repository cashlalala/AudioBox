# This file was automatically generated by SWIG (http://www.swig.org).
# Version 1.3.31
#
# Don't modify this file, modify the SWIG interface instead.

import _rddetect
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


class RenderCap(object):
    """Proxy of C++ RenderCap class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    vramSize = _swig_property(_rddetect.RenderCap_vramSize_get, _rddetect.RenderCap_vramSize_set)
    totalMemory = _swig_property(_rddetect.RenderCap_totalMemory_get, _rddetect.RenderCap_totalMemory_set)
    freeMemory = _swig_property(_rddetect.RenderCap_freeMemory_get, _rddetect.RenderCap_freeMemory_set)
    screenWidth = _swig_property(_rddetect.RenderCap_screenWidth_get, _rddetect.RenderCap_screenWidth_set)
    screenHeight = _swig_property(_rddetect.RenderCap_screenHeight_get, _rddetect.RenderCap_screenHeight_set)
    colorDepth = _swig_property(_rddetect.RenderCap_colorDepth_get, _rddetect.RenderCap_colorDepth_set)
    def __init__(self, *args): 
        """__init__(self) -> RenderCap"""
        this = _rddetect.new_RenderCap(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _rddetect.delete_RenderCap
    __del__ = lambda self : None;
RenderCap_swigregister = _rddetect.RenderCap_swigregister
RenderCap_swigregister(RenderCap)


def GetRenderCap(*args):
  """GetRenderCap() -> RenderCap"""
  return _rddetect.GetRenderCap(*args)
class PowerState(object):
    """Proxy of C++ PowerState class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    useAC = _swig_property(_rddetect.PowerState_useAC_get, _rddetect.PowerState_useAC_set)
    BatteryLifePercent = _swig_property(_rddetect.PowerState_BatteryLifePercent_get, _rddetect.PowerState_BatteryLifePercent_set)
    BatteryLifeTime = _swig_property(_rddetect.PowerState_BatteryLifeTime_get, _rddetect.PowerState_BatteryLifeTime_set)
    BatteryFullLifeTime = _swig_property(_rddetect.PowerState_BatteryFullLifeTime_get, _rddetect.PowerState_BatteryFullLifeTime_set)
    def __init__(self, *args): 
        """__init__(self) -> PowerState"""
        this = _rddetect.new_PowerState(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _rddetect.delete_PowerState
    __del__ = lambda self : None;
PowerState_swigregister = _rddetect.PowerState_swigregister
PowerState_swigregister(PowerState)


def GetPowerState(*args):
  """GetPowerState() -> PowerState"""
  return _rddetect.GetPowerState(*args)
class CPUState(object):
    """Proxy of C++ CPUState class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    name = _swig_property(_rddetect.CPUState_name_get, _rddetect.CPUState_name_set)
    clock = _swig_property(_rddetect.CPUState_clock_get, _rddetect.CPUState_clock_set)
    bCapability = _swig_property(_rddetect.CPUState_bCapability_get, _rddetect.CPUState_bCapability_set)
    bMMX_Supported = _swig_property(_rddetect.CPUState_bMMX_Supported_get, _rddetect.CPUState_bMMX_Supported_set)
    bSSE_Supported = _swig_property(_rddetect.CPUState_bSSE_Supported_get, _rddetect.CPUState_bSSE_Supported_set)
    bSSE2_Supported = _swig_property(_rddetect.CPUState_bSSE2_Supported_get, _rddetect.CPUState_bSSE2_Supported_set)
    bPNI_Supported = _swig_property(_rddetect.CPUState_bPNI_Supported_get, _rddetect.CPUState_bPNI_Supported_set)
    bSSEMMXExt_Supported = _swig_property(_rddetect.CPUState_bSSEMMXExt_Supported_get, _rddetect.CPUState_bSSEMMXExt_Supported_set)
    b3DNow_Supported = _swig_property(_rddetect.CPUState_b3DNow_Supported_get, _rddetect.CPUState_b3DNow_Supported_set)
    bExt3DNow_Supported = _swig_property(_rddetect.CPUState_bExt3DNow_Supported_get, _rddetect.CPUState_bExt3DNow_Supported_set)
    bHT_Supported = _swig_property(_rddetect.CPUState_bHT_Supported_get, _rddetect.CPUState_bHT_Supported_set)
    bDAZ_Supported = _swig_property(_rddetect.CPUState_bDAZ_Supported_get, _rddetect.CPUState_bDAZ_Supported_set)
    bRDTSC_Supported = _swig_property(_rddetect.CPUState_bRDTSC_Supported_get, _rddetect.CPUState_bRDTSC_Supported_set)
    bCMOV_Supported = _swig_property(_rddetect.CPUState_bCMOV_Supported_get, _rddetect.CPUState_bCMOV_Supported_set)
    def __init__(self, *args): 
        """__init__(self) -> CPUState"""
        this = _rddetect.new_CPUState(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _rddetect.delete_CPUState
    __del__ = lambda self : None;
CPUState_swigregister = _rddetect.CPUState_swigregister
CPUState_swigregister(CPUState)


def GetCPUState(*args):
  """GetCPUState() -> CPUState"""
  return _rddetect.GetCPUState(*args)
class CPUUsage(object):
    """Proxy of C++ CPUUsage class"""
    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr
    def __init__(self, *args): 
        """__init__(self, WCHAR szProcessName) -> CPUUsage"""
        this = _rddetect.new_CPUUsage(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _rddetect.delete_CPUUsage
    __del__ = lambda self : None;
    def GetCPUUsage(*args):
        """GetCPUUsage(self) -> float"""
        return _rddetect.CPUUsage_GetCPUUsage(*args)

CPUUsage_swigregister = _rddetect.CPUUsage_swigregister
CPUUsage_swigregister(CPUUsage)



