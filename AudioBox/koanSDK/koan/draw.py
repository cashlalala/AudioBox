"""
Drawing utility
"""
from os.path import splitext
import koan
from texmng import StringTextureManager

class UtilRender:
    @staticmethod    
    def calUniformRect(texSize, rect, **argd):
        """
        @return: rect with fixed size
        """
        w, h = texSize

        if rect[3] <= 0 or h <= 0:
            return (0, 0, 0, 0)

        ratio = float(w) / h
        ret = ratio >= (float(rect[2]) / rect[3])
        if argd.get('fill', False):
            ret = not ret
        
        if ret:
            newh = rect[2] / ratio
            if newh <= 0:
                newh = 1
            top = rect[0]
            left = rect[1] + (rect[3] - newh) / 2.0
            newRect = (top, left, top + rect[2], left + newh)
        else:
            neww = rect[3] * ratio
            if neww <= 0:
                neww = 1
            top = rect[0] + (rect[2] - neww) / 2.0
            left = rect[1]
            newRect = (top, left, top + neww, left + rect[3])
        return newRect
    
    def calTextSize(self, text, font, fontsize, **argd):
        """
        get the size of a string on the screen
    
        @param font: font of the string
        @param fontsize: font size of the string
        @return: size of the string, at format (width, height)
        @rtype: a tuple of 2 number
        """
        if not text:
            return 0, 0
        
        unit = 1, 1        
        #size = StringTextureManager.GetStringTextureSize(font, text, fontsize * unit[1])
        tex, size = self.GetStringTexture(
            text,
            fontsize * unit[1],
            (255, 255, 255, 255),
            font
        )
        size = size[0]/unit[0], size[1]/unit[1]
        return size

    def calMLTextSize(self, text, font, fontsize, width, height):
        """
        get the size of a multiline string on the screen
    
        @param font: font of the string
        @param fontsize: font size of the string
        @return: size of the string, at format (width, height)
        @rtype: a tuple of 2 number
        """
        if not text:
            return 0, 0
        
        unit = 1, 1
        
        tex, size = self.GetMLStringTexture(
            text,
            fontsize,
            width * unit[0],
            height * unit[1],
            ord('L'),
            (255, 255, 255, 255),
            font
        )
        size = size[0]/unit[0], size[1]/unit[1]
        return size
        
    def GetStringTexture(self, string, fontsize, color = (255, 255, 255, 255), font = '', hint = 0):
        """
        Get the String Texture for a given string
    
        @param string: the string that showed on the texture
        @param fontsize: font size of the string
        @param font: font of the string texture
        """
        if font == '':
            font = koan.defaultFont
        return self.window.stringTextureManager.GetStringTexture(font, string, fontsize, 0.0, color, hint)
    
    def GetMultiLineStringTexture(self, string, fontsize, width=1024.0, color = (255, 255, 255, 255), font = ''):
        """GetStringTexture(text, text fontsize, color = (255, 255, 255, 255), font = gDefaultFont):
        """
        if font == '':
            font = koan.defaultFont
        return self.window.stringTextureManager.GetStringTexture(font, string, fontsize, width, color)
    
    def GetMLStringTexture(self, string, sizeheight, width, height, align, color = (255, 255, 255, 255), font = ''):
        """GetStringTexture(text, text height, color = (255, 255, 255, 255), font = gDefaultFont):
        """
        if font == '':
            font = koan.defaultFont
        return self.window.stringTextureManager.GetMLStringTexture(font, string, sizeheight, (width, height), align, color)
    
    def GetImageTexture(self, filename, maxw = -1, maxh = -1):
        return self.window.imageTextureManager.GetTexture(filename, maxw, maxh)

    def DrawUniformRect(self, texsize, rect):
        """
        draw a rect with width / height ratio fixed
    
        @param txtsize: (width, height)
        @param rect: (left, top, width, height)
        @rtype: None
        """
        rect = self.calUniformRect(texsize, rect)
        self.DrawRect(*rect)
        
    def DrawUniformFillRect(self, texsize, rect):
        rect = self.calUniformRect(texsize, rect, fill = True)
        self.DrawRect(*rect)

    def DrawUniformVideo(self, tex, texsize, rect):
        """
        draw a rect with width / height ratio fixed
    
        @param txtsize: (width, height)
        @param rect: (left, top, width, height)
        @rtype: None
        """
        rect = calUniformRect(texsize, rect)
        self.DrawVideo(tex, *rect)
        
    def RatioDrawExpanded(self, txtsize, rect, focusTop = 0.75):
        """
        draw clipped rectangle with aspect ratio fixed
    
        @param txtsize: (width, height)
        @param rect: (left, top, width, height)
        @param focusTop: focusTop = 1.0  -> focused on the top side of the image
                                    0.0  -> focused on the center of the image
                                    -1.0 -> focused on the bottom side of the image
        @rtype: None
        """
        assert focusTop <= 1.0 and focusTop >= -1.0, 'wrong focusTop value'
    
        self.PushBound(rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3], 0, 0, 0, 0)
    
        w, h = txtsize
        if float(w) / h >= float(rect[2]) / rect[3]:
            newh = rect[3]
            neww = float(w * rect[3]) / h
            left = rect[0] + float(rect[2] - neww) / 2
            top = rect[1]
            self.DrawRect(left,
                     top,
                     left + neww,
                     top + newh)
        else:
            neww = rect[2]
            newh = float(h * rect[2]) / w
            left = rect[0]
            upperTop = rect[1]
            centerTop = rect[1] + float(rect[3] - newh) / 2
            top = upperTop * focusTop + centerTop * (1 - focusTop)
            self.DrawRect(left, top, left + neww, top + newh)
    
        self.PopBound()
    
    def DrawText(self, str, xy, height, color, font = ''):
        """
        draw text on screen
    
        @param xy: the left top position of the text
        @rtype: None
        """
        if not str:
            return
    
        unit = self.window.currentPixelUnit
        text, size = self.GetStringTexture(
            str,
            int(height * unit[1]),
            color,
            font
        )
        self.SetTexture(text)
    
        size = size[0]/unit[0], size[1]/unit[1]
        self.DrawRect(xy[0], xy[1], xy[0] + size[0], xy[1] + size[1])
    
    def DrawTextEx(self, str, position, align, height, color, font = '', scrollFunc = None, **argd):
        """
        advanced draw text function
    
        @return: size of the text on screen?
        @rtype: a tuple of 2 numbers
        @param align: a combination of
                      x alignment: 'L' - left, 'C' - center, 'R' - right
                      y alignment: 'T' - top, 'B' - buttom ('D' - down, same as 'B')
                      multi-line?: 'M'
        """
        align = align.upper()
        # take 'D' the same as 'B'
        align = align.replace('D', 'B')
    
        if not str:
            return 0, 0
    
        unit = self.window.currentPixelUnit
        # make sure convert to window
        #tmppos = int(position[0]*unit[0]),  int(position[1]*unit[1]),       int(position[2]*unit[0]),       int(position[3]*unit[1])
        #position = tmppos[0]/unit[0],           tmppos[1]/unit[1],            tmppos[2]/unit[0],              tmppos[3]/unit[1]
        height = int(height * unit[1])          # convert to Window Space
        if 'M' <> align[0]:
            text, size = self.GetStringTexture(
                str,
                height,      #convert PCM space to Window space
                color,
                font
            )
        else:
            a = 'L'
            if 'C' in align:    a = 'C'
            elif 'R' in align:  a = 'R'
    
            text, size = self.GetMLStringTexture(
                str,
                height,
                int((position[2] - position[0]) * unit[0]),
                int((position[3] - position[1]) * unit[1]),
                ord(a),
                color,
                font
            )
            align = align[1:]
    
    
        '''
        -----------  PCM coordinate system (1024 768) --------------    precision: floating point
        -----------  Widnows coordinate system (w, h) --------------    precision: integer
        size: text rectangle size    (PCM space)
        offset1: text ascent line    (PCM space)
        offset2: text descent line  (PCM space)
        yh: text real height          (PCM space)
        h3: bound region width   (PCM space)
        height: assign text height (Window space)
    
        PushBound: PCM space, and must be convert to window space with just multiply pixelunit
        DrawRect: PCM space, and must be convert to window space with just multiply pixelunit
        '''
    
        adp1, adp2 = size[2]                        # ascent, descent percentage
        size = size[0]/unit[0], size[1]/unit[1]     # size is float but must be convert back to integer(Window Space) with just multiply pixelunit        
        h3 = (height/3) / unit[1]                   # PCM space, can be convert back to integer(Window Space) with just multiply pixelunit
        diffWidth = size[0] - (position[2] - position[0])
    
        # calculating position and bound
        drawBound = [position[0], position[1], position[2], position[3], 0, 0, 0, 0]
        
        useFade = argd.get('fade', False)
        if align in ('L', 'C', 'R'):
            #offset1 = adp1 * size[1]                    # offset1, offset2, yh must can be convert back in integer(Window Space) with just multiply pixelunit
            #offset2 = adp2 * size[1]
            #yh = offset2 - offset1
            #posY = (position[1] + position[3] - yh) / 2 - offset1
            posY = (position[1] + position[3] - size[1]) / 2
        elif 'B' in align:
            posY = position[3] - size[1]
            if useFade:
                drawBound[1] -= h3
                drawBound[1+4] += h3
        elif 'T' in align:
            posY = position[1] #- offset1
            if useFade:
                drawBound[3] -= h3
                drawBound[3+4] += h3
    
        if 'L' in align or (scrollFunc and diffWidth > 0.0 and ('C' in align or 'R' in align) ):
            posX = position[0]
            if useFade:
                drawBound[2] -= h3
                drawBound[2+4] += h3
        elif 'R' in align:
            posX = position[2] - size[0]
            if useFade:
                drawBound[0] -= h3
                drawBound[0+4] += h3
        elif 'C' in align:
            posX = (position[0] + position[2] - size[0]) / 2
            if posX < position[0]:
                posX = position[0]
                drawBound[2] -= h3
                drawBound[2+4] += h3
    
        rect = posX, posY, posX + size[0], posY + size[1]
        useBound = True
        useScrolling = False
        if rect[0] >= drawBound[0] and rect[1] >= drawBound[1] and \
            rect[2] <= drawBound[2] and rect[3] <= drawBound[3]:
            useBound = False
        if scrollFunc and diffWidth > 0.0:
            useScrolling = True
            useBound = True
    
        if useBound:
            self.PushBound( *drawBound )

        if useScrolling:
            self.PushMatrix()
            scroll, alpha = scrollFunc(diffWidth, size[0] + (position[2] - position[0]))
            self.PushAlpha(alpha)
            self.Translate(scroll, 0)
    
        #self.SetTexture(None)
        #self.SetColor(255,128,128,128)
        #self.DrawRect(*rect)
        #self.SetColor(255,255,255,255)
        self.SetTexture(text)
        self.DrawRect(*rect)
    
        if useScrolling:
            self.PopAlpha()
            self.PopMatrix()
            
        if useBound:
            self.PopBound()
        return size[0], size[1]
    
    def DrawTextFree(self, str, position, align, height, color, font = ''):
        """
        draw text without setting the bounding rect of it
        @param align: 'L': left, 'M':
    
        @return: size of the text on screen?
        @rtype: (xsize, ysize)
        """
        align = align.upper()
        if str == "":
            return 0, 0
    
        unit = self.window.currentPixelUnit
        if align <> 'M':
            text, size = self.GetStringTexture(
                str,
                int(height * unit[1]),
                color,
                font
            )
        else:
            text, size = self.GetMultiLineStringTexture(
                str,
                int(height * unit[1]), int((position[2] - position[0]) * unit[0]),
                color,
                font
            )
    
        adp1, adp2 = size[2]
        size = size[0]/unit[0], size[1]/unit[1]
        offset1 = adp1 * size[1]
        offset2 = adp2 * size[1]
    
        yh = offset2 - offset1
        h3 = height/3
    
        self.SetTexture(text)
        
        if align == 'L':
            pos = (position[0] + position[2]) / 2, (position[1] + position[3]) / 2
            pos = pos[0] - (size[0]/2), pos[1] - (yh/2) - offset1
    
            self.DrawRect(position[0], pos[1], position[0] + size[0], pos[1] + size[1])
        elif align == 'C':
            pos = (position[0] + position[2]) / 2, (position[1] + position[3]) / 2
            pos = pos[0] - (size[0]/2), pos[1] - (yh/2) - offset1
            self.DrawRect(pos[0], pos[1], pos[0] + size[0], pos[1] + size[1])
        elif align == 'R':
            pos = (position[1] + position[3]) / 2.0 - (yh/2) - offset1
            self.DrawRect(position[2] - size[0], pos, position[2], pos + size[1])
        elif align == 'M':
            self.DrawRect(position[0], position[1], position[0]+size[0], position[1]+size[1])

        return size[0], size[1]

    def GetTexture(self, filename, maxw = -1, maxh = -1, gamma = None, **argd):
        window = self.window
        if hasattr(window, 'theme') and window.theme:
            filename = window.theme.translate(filename)

        if splitext(filename)[1].upper() == '.XML':
            return window.imageTextureManager.GetAnimatedTexture(filename, maxw, maxh)
        else:
            if gamma and hasattr(window, 'colorTheme') and window.colorTheme:
                gamma = window.colorTheme(gamma)
                return window.imageTextureManager.GetTexture(filename, maxw, maxh, gamma, **argd)
            else:
                return window.imageTextureManager.GetTexture(filename, maxw, maxh, **argd)
            
    def GetEffect(self, filename):
        window = self.window
        if hasattr(window, 'theme') and window.theme:
            filename = window.theme.translate(filename)
        return window.effectManager.GetEffect(filename)
