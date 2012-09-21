import koan
import os
import sys
import time
import traceback

if sys.platform == 'win32':      
    # window platform    
    from koan.renderer.wingdi import SetThreadPriority, GetThreadPriority, InitThread, UninitThread, SetThreadName
    from koan.renderer.wingdi import KClock, Run, LeaveLoop, DumpMessage, PeekMsg
    from koan.renderer.wingdi import CreateLink, GetLink
        
    from koan.img.image import LoadImage
    from koan.renderer.rddetect import CPUUsage
    import reg

    def CreateWindow():
        from koan.renderer.wingdi import MainWnd
        return MainWnd()

    def CreateEdit(callback = None, text = u'', multiline = False, align = 'L', vscroll = False, hscroll = False):
        from koan.renderer.wingdi import CKoanEdit
        return CKoanEdit(callback, text, multiline, align, vscroll, hscroll)

    def CreateDatePicker(callback = None, longFormat = False):
        from koan.renderer.wingdi import CKoanDatePicker
        return CKoanDatePicker(callback, longFormat)
    
    def ToUnicode(str):
        try:
            return unicode(str)
        except UnicodeDecodeError:
            return unicode(str, 'mbcs')

    def GetImageData(filename, maxw, maxh):
        return LoadImage(ToUnicode(filename), maxw, maxh)

    def CanUse3D():
        from koan.renderer.rddetect import GetRenderCap, GetPowerState, GetCPUState
        from koan.platform import reg
        try:
            vram = int(koan.config.get('AutoDetect', 'min_lp_vram', '12'))
        except:
            vram = 12

        cap = GetRenderCap()
        if cap == None:
            return False
        else:
            if cap.totalMemory < vram * 1024 * 1024:
                return False
            if cap.colorDepth < 16:
                return False
        return True

    def AutoDetectAnim(b2D):
        pass
        """
        from koan.renderer.rddetect import GetCPUState
        cpu = GetCPUState()
        if koan.config.get('RENDER', 'UseAnim', 'True').upper() == "AUTO" and cpu and b2D:
            min_cpu_anim = int(koan.config.get('AutoDetect', 'min_cpu_anim', '1200'))
            koan.useAnimation = cpu.clock >= min_cpu_anim
        else:
            koan.useAnimation = koan.config.get('RENDER', 'UseAnim', 'True').upper() != "FALSE"
        """

    def AutoDetectRenderer():
        from koan.renderer.rddetect import GetRenderCap, GetPowerState, GetCPUState

        abort3D = False
        LP = False
        des = ''

        if koan.config.getBool('AutoDetect', 'must_use_ac', True):
            ps = GetPowerState()
            print 'UseAC', ps.useAC
            if not ps.useAC:
                abort3D = True
                des += 'AC Off Line\n'

        cpu = GetCPUState()
        if cpu == None:
            des += 'Cannot get CPU State\n'
        else:
            print '----- CPU -----'
            print cpu.name

            min_hp_cpu = int(koan.config.get('AutoDetect', 'min_hp_cpu', '1000'))
            print 'CPU', cpu.clock, 'MHz'

            if cpu.clock < min_hp_cpu:
                if cpu.bCapability and cpu.bSSE2_Supported:
                    print 'Although current Frequency <', min_hp_cpu, ', but SSE2 Supported, so accept it'
                else:
                    LP = True
                    des += 'CPU is below %fG\n' % (min_hp_cpu / 1000.0)

        cap = GetRenderCap()
        if cap == None:
            abort3D = True
            des += 'Cannot create DirectDraw (Remote Desktop or resource lock is occupied)\n'
        else:
            min_lp_vram = int(koan.config.get('AutoDetect', 'min_lp_vram', '12'))
            min_hp_vram = int(koan.config.get('AutoDetect', 'min_hp_vram', '24'))

            rm = ((cap.totalMemory + 2 * 1024 * 1024) / (4 * 1024 * 1024)) * 4
            print 'VRam:%d (~%dMB)' % (cap.totalMemory, rm)

            if rm < min_lp_vram:
                abort3D = True
                des += 'Use 2D due to Video Memory is too small(HW: %dM)\n' % (cap.totalMemory / (1024*1024))
            elif rm < min_hp_vram:
                LP = True
                des += 'Use 3DLP due to Video Memory is too small(HW: %dM)\n' % (cap.totalMemory / (1024*1024))

            print 'Color Depth:', cap.colorDepth
            if cap.colorDepth < 16:
                abort3D = True
                des += 'Color Depth in Pattle mode\n'

        if abort3D:
            rnd = '2D'
        elif LP:
            rnd = '3DLP'
        else:
            rnd = '3D'

        print "Select %s\n" %(rnd)
        return rnd , des

    def MakePath(*path):
        if len(path) == 0:
            return ''

        ret = path[0]
        for i in path[1:]:
            ret = os.path.join(ret, i)

        return os.path.abspath(ret)

    def ShowMessageBox(message):
        from koan.renderer.wingdi import ShowMessageBox
        ShowMessageBox(message)
else:
    # linux platform
    from koan.renderer.winsdl import SetThreadPriority
    import PIL
    import PIL.Image

    def CreateWindow():
        from koan.renderer.winsdl import BaseWnd
        return BaseWnd()

    def ToUnicode(str):
        try:
            return unicode(str)
        except UnicodeDecodeError:
            return unicode(str, 'utf8')

    def InitThread(*arg):
        pass

    def UninitThread(*arg):
        pass

    def SetThreadName(*arg):
        pass

    GetTime = time.time

    def GetImageData(filename, maxw, maxh):
        try:
            filename = filename.replace( "\ "[0], "/")
            org = PIL.Image.open(filename)
            w, h = org.size

            if w > maxw:
                tmpw = maxw
                tmph = h * maxw / w
            else:
                tmpw = w
                tmph = h
            if tmph > maxh:
                newh = maxh
                neww = tmpw *maxh / tmph
            else:
                newh = tmph
                neww = tmpw
            if neww == w and newh == h:
                im = org
            else:
                im = org.resize((neww, newh))

            fmt = im.mode
            #fmt = 'ARGB'
            w, h = im.size
            s = im.tostring()
        except:
            print 'Load', filename, 'fail'
            return None, 0, 0, ''

        return s, w, h, fmt

    def CanUse3D():
        return True

    def AutoDetectAnim(b2D):
        koan.useAnimation = True

    def AutoDetectRenderer():
        #return 'rdsdl', 'use default'
        return '3D', 'use default'

    def MakePath(*path):
        if len(path) == 0:
            return ''

        ret = path[0]
        for i in path[1:]:
            ret = os.path.join(ret, i)

        ret = ret.replace( "\ "[0], "/")
        return os.path.abspath(ret)

    GetTimeEx = GetTime

    def ShowMessageBox(message):
        print message
