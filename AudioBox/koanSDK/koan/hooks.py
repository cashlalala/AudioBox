orig_PushAlpha = None
orig_Translate = None
orig_Scale = None
orig_Rotate = None
pre_render = None


import koan.anim

def __check(anim):
    if isinstance(anim, koan.anim.AnimBase):
        anim.applyCount -= 1
        if anim.applyCount < 0:
            assert False

def PushAlpha(alpha):
    global orig_PushAlpha
    __check(alpha)
    orig_PushAlpha(alpha)

def Translate(x, y):
    global orig_Translate
    __check(x)
    __check(y)
    orig_Translate(x, y)

def Scale(x, y):
    global orig_Scale
    __check(x)
    __check(y)
    orig_Scale(x, y)

def Rotate(angle):
    global orig_Rotate
    __check(angle)
    orig_Rotate(angle)

def initimp(render):
    """
    wrapping some functions for additional check
    """
    
    global orig_PushAlpha
    global orig_Translate
    global orig_Scale
    global orig_Rotate
    global pre_render

    if pre_render <> render:    
        if pre_render:
            pre_render.PushAlpha = orig_PushAlpha
            pre_render.Translate = orig_Translate
            pre_render.Scale = orig_Scale
            #pre_render.Rotate = orig_Rotae
        
        orig_PushAlpha = render.PushAlpha
        orig_Translate = render.Translate
        orig_Scale = render.Scale
        #orig_Rotae = render.Rotate
        

        render.PushAlpha = PushAlpha
        render.Translate = Translate
        render.Scale = Scale
        #render.Rotate = Rotate

        pre_render = render

def init(render):
    if koan.isDebug:
        initimp(render)
    pass

