
##################################################################################

import koan
import gc
import traceback
import os
import xml.dom.minidom
import StringIO
from img.font import CreateFontImage, CreateFontImageML, MeasureTrailingSpaces, GetFontImageSize
from resourcemgr import ResourceManager

def LoadXMLFile(fn):
    data = ''
    fr = file(fn, 'r')
    for i in fr:
        if not i.isspace():
            data += i
    fr.close()
    del fr
    
    xmlFile = StringIO.StringIO(data)
    dom = xml.dom.minidom.parse(xmlFile)
    xmlFile.close()
    del xmlFile
    return dom


class TextureManager(ResourceManager):
    def __init__(self, window, **argd):
        ResourceManager.__init__(self, window, **argd)

    def CreateTexture(self, img, w, h, fmt = "ARGB", **argd):
        '''
        CreateTexture will lost texture after device lost and will not auto restore
        '''
        if img == None or w == 0 or h == 0:
            return None

        t = self.window.render.CBufferTexture(self.window.render)
        ret = t.CreateFromRaw(img, w, h, fmt, argd.get('cache', False))
        if ret <= 0:
            if ret == -2:
                # try again
                self.window.fire('Free Unused Texture')
                ret = t.CreateFromRaw(img, w, h, fmt, argd.get('cache', False))
                if ret == -2:
                    print 'VMem is not enough'
                    self.window.vRamNotEnough = True
                if ret <= 0:
                    #assert False, 'unknown error'
                    return None
            else:
                #assert False, 'unknown error'
                return None
        return t

    def CreateTextureFromImageBuffer(self, imgBuf, w, h, fmt = "ARGB", **argd):
        '''
        CreateTexture will lost texture after device lost and will not auto restore
        '''
        if imgBuf == None or w == 0 or h == 0:
            return None

        t = self.window.render.CDynTexture(self.window.render)
        ret = t.Create(w, h, fmt);
        t.Update(imgBuf)
        if ret <= 0:
            if ret == -2:
                # try again
                self.window.fire('Free Unused Texture')
                ret = t.Create(w, h, fmt)
                t.Update(imgBuf)
                if ret == -2:
                    print 'VMem is not enough'
                    self.window.vRamNotEnough = True
                if ret <= 0:
                    #assert False, 'unknown error'
                    return None
            else:
                #assert False, 'unknown error'
                return None
        return t
        
    def CreateTextureFromBitmap(self, bmp, fmt = "ARGB"):
        '''
        CBufferTexture will cache the bitmap data, so it will auto restore texture after device lost
        (bitmap will be cloned and cache in CBufferTexture)
        '''
        if bmp == None:
            return None

        t = self.window.render.CBufferTexture(self.window.render)
        ret = t.CreateFromBitmap(bmp)
        if ret <= 0:
            if ret == -2:
                # try again
                #koan.FreeUnusedTexture()
                self.window.fire('Free Unused Texture')
                ret = t.CreateFromBitmap(bmp)
                if ret == -2:
                    print 'VMem is not enough'
                    self.window.vRamNotEnough = True
                if ret <= 0:
                    #assert False, 'unknown error'
                    return None
            else:
                #assert False, 'unknown error'
                return None
        return t
    
    def CreateTextureFromFileStream(self, stream, fmt = "ARGB"):
        '''
        CBufferTexture will cache the stream data, so it will auto restore texture after device lost
        (stream will be converted to IStream data and cache in CBufferTexture)
        this is often used in jpeg raw image stream buffer
        '''
        if stream == None:
            return None

        t = self.window.render.CBufferTexture(self.window.render)
        ret = t.CreateFromFileStream(stream)
        if ret <= 0:
            if ret == -2:
                # try again
                #koan.FreeUnusedTexture()
                self.window.fire('Free Unused Texture')
                ret = t.CreateFromFileStream(stream)
                if ret == -2:
                    print 'VMem is not enough'
                    self.window.vRamNotEnough = True
                if ret <= 0:
                    #assert False, 'unknown error'
                    return None
            else:
                #assert False, 'unknown error'
                return None
        return t
        
    def CreateAnimatedTexture(self, filenames, duration, isloop, maxw, maxh, fmt = "ARGB"):
        texCount = len(filenames)
        interpolator = koan.anim.AnimLinear(duration, (0, 1), (0, texCount), loop = isloop)
        
        t = self.window.render.CAnimatedTexture(self.window.render, texCount, duration, interpolator.animObj)
    
        for i in xrange(texCount):
            fn = filenames[i]
            
            if not t.Create(i, fn, maxw, maxh):
                return None
        return t

    def CreateAutoPackTexture(self, img, w, h):
        t = self.window.render.CAutoPackTexture32(self.window.render)
        t.UploadData(img, w, h)
        return t

class StringTextureManager(TextureManager):
    def __init__(self, window, **argd):
        TextureManager.__init__(self, window, **argd)
        self.premap = {}        
        self.map = {}
        self.autoRemove(self.window.bind("Device Lost", self.onDeviceLost))
        self.autoRemove(self.window.bind("Device Restore", self.onDeviceRestore))

    def close(self):
        TextureManager.close(self)
        self.window = koan.Null

    # default return value when something is wrong
    DefaultFailReturn = None, (1, 1, (0, 1))

    @staticmethod
    def GetStringTextureSize(font, text, height):
        if font == '':
            font = koan.defaultFont
        return GetFontImageSize(koan.ToUnicode(font), height, 0, koan.ToUnicode(text), 0)

    def GetStringTexture(self, font, text, height, width, color, hint):
        if not text:
            return self.DefaultFailReturn
    
        itm = (font, text, int(height), int(width), color)

        if self.map.has_key(itm):
            return self.map[itm]

        elif self.premap.has_key(itm):
            ret = self.premap[itm]
            self.map[itm] = ret
            return ret

        else:
            utext = koan.ToUnicode(text)

            uFont = koan.ToUnicode(font)
            if koan.useRTL:
                uFont += u"&RTL"
            
            t = self.window.render.CFontTexture(self.window.render)
            if t is None:
                return self.DefaultFailReturn

            succeed, w, h, adp = t.Create(
                uFont,
                height,
                width,
                color[0], color[1], color[2], color[3],
                utext,
                hint)
                
            if not succeed:
                return self.DefaultFailReturn

            self.map[itm] = (t, (w, h, adp))
            return t, (w, h, adp)

    def GetMLStringTexture(self, font, text, height, rect, align, color):
        if not text:
            return self.DefaultFailReturn
    
        itm = (font, text, int(height), rect, color)

        if self.map.has_key(itm):
            return self.map[itm]

        elif self.premap.has_key(itm):
            ret = self.premap[itm]
            self.map[itm] = ret
            return ret

        else:
            utext = koan.ToUnicode(text)

            uFont = koan.ToUnicode(font)
            if koan.useRTL:
                uFont += u"&RTL"

            t = self.window.render.CFontTexture(self.window.render)
            if t is None:
                return self.DefaultFailReturn
                
            succeed, w, h, adp = t.CreateML(
                uFont,
                height,
                rect[0], rect[1], align,
                color[0], color[1], color[2], color[3],
                utext)

            if not succeed:
                return self.DefaultFailReturn

            self.map[itm] = (t, (w, h, adp))
            return t, (w, h, adp)

    def clearAll(self):
        self.window.dirty = True
        self.premap = {}
        self.map = {}
        #print 'string clearAll'

    def gc(self):
        self.premap = self.map
        self.map = {}

###############################################################################################

class ImageTextureManager(TextureManager):
    """ImageTextureManager

    Event:
        Image Loaded(filename)
    """
    def __init__(self, window, **argd):
        TextureManager.__init__(self, window, **argd)
        self.autoRemove(self.window.bind("Free Unused Texture", self.freeUnused))
        self.autoRemove(self.window.bind("Free All Texture", self.clearAll))

    def LoadTexture(self, filename, maxw = -1, maxh = -1, gamma = None, *argv, **argd):
        if not filename:
            #raise ValueError, "filename is a zero string"
            print "filename is a zero string"
            return None

        if maxw == -1 and maxh == -1:
            maxw, maxh = self.window._window.GetDesktopSize()
        
        tex = self.window.render.CFileTexture(self.window.render)
        if '|' in filename:
            filename, margin = filename.split('|')
            filename = filename.strip()
            margin = margin.strip()
        else:
            margin = None
            
        if gamma and len(gamma) > 4:
            gamma = gamma[:4] + tuple(gamma[4:][0].replace(' ','').split('->'))
        if tex.Create(koan.ToUnicode(filename), maxw, maxh, gamma, argd.get('async', False)):
            if margin:
                margin = margin.strip()[1:-1]
                if ',' in margin:
                    m = [eval(i) for i in margin.split(",")]
                else:
                    m = [eval(i) for i in margin.split(" ")]
                tex.SetMargin(m[0], m[1], m[2], m[3])
                if len(m) > 4:
                    tex.SetHollow('hollow' in m)
                    tex.SetFilter(0x10 if 'linear' in m else 0x20 if 'point' in m else 0x0)
            return tex
        return None

    def LoadTextureEx(self, *arg, **argd):
        return self.LoadTexture(*arg)
       
    def LoadAnimatedTexture(self, filename, maxw = -1, maxh = -1):
        if not filename:
            raise ValueError, "filename is a zero string"

        if maxw == -1 and maxh == -1:
            maxw, maxh = self.window._window.GetDesktopSize()

        folder, fn = os.path.split(filename)
        
        filenames = []
        count = 0
        duration = 1.0
        loop = True
        static_tex = ''
        
        dom = LoadXMLFile(filename)
        tag_name = dom.documentElement.tagName
        if tag_name == 'AnimatedTexture':
            mtexs = dom.getElementsByTagName(tag_name)
            for mtex in mtexs:
                try:
                    duration = float( mtex.getAttribute('duration') )
                    loop = eval( mtex.getAttribute('loop') )
                    static_tex = mtex.getAttribute('static')
                except:
                    pass
                    
                if static_tex and not koan.useAnimation:
                    return self.LoadTexture(os.path.join(folder, static_tex), maxw, maxh)

                for tex in mtex.childNodes:
                    try:
                        if tex.tagName == 'Texture':
                            filenames.append( os.path.join(folder, tex.getAttribute('filename')) )
                            count += 1
                    except:
                        pass

        t = self.CreateAnimatedTexture(filenames, duration, loop, maxw, maxh)
        if t:
            t.SetName(koan.ToUnicode(filename))
        return t
        
    def GetTexture(self, *key, **argd):
        if self.resMap.has_key(key):
            txt = self.resMap[key][0]
        else:
            try:
                txt = self.LoadTexture(*key, **argd)
            except:
                txt = None
                traceback.print_exc()
                print '[texmng.py] LoadTexture ' + str(key) + ' Failed !!!' 
        self.resMap[key] = txt, koan.GetTime(), self.window.frameNumber
        return txt

    def GetTextureEx(self, *key, **argd):
        if self.resMap.has_key(key):
            txt = self.resMap[key][0]
        else:
            txt = self.LoadTextureEx(*key, **argd)
            if not txt:
                if not argd.get('errorcache', True):
                    return None

        self.resMap[key] = txt, koan.GetTime(), self.window.frameNumber
        return txt
    
    def GetAnimatedTexture(self, *key):
        if self.resMap.has_key(key):
            txt = self.resMap[key][0]
        else:
            try:
                txt = self.LoadAnimatedTexture(*key)
            except:
                txt = None

        self.resMap[key] = txt, koan.GetTime(), self.window.frameNumber
        return txt

    def clear(self, *key):
        self.window.dirty = True
        if len(key) == 3 and key[1] == 0 and key[2] == 0:
            for i in self.resMap.keys():
                if i[0] == key[0]:
                    self.resMap[i] = None
                    del self.resMap[i]
        else:
            for i in self.resMap.keys():
                if i[0] == key[0]:
                    self.resMap[i] = None
                    del self.resMap[i]


###############################################################################################
koan.optimize(StringTextureManager)
koan.optimize(ImageTextureManager)
