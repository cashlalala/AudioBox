
##################################################################################

import koan
from resourcemgr import ResourceManager
###############################################################################################

class EffectManager(ResourceManager):
    """EffectManager

    Event:
        Effect Loaded(filename)
    """
    def __init__(self, **argd):
        ResourceManager.__init__(self, **argd)
        self.autoRemove(self.window.bind("Clear Effect", self.clear))

    def LoadResource(self, *key):
        if not key or not key[0]:
            raise ValueError, "filename is a zero string"

        effect = self.window.render.CEffect(self.window.render)
        assert effect
        succ = effect.CreateFromFile(unicode(key[0]))
        if not succ:
            raise Exception
        return effect

    def GetEffect(self,filename):
        return ResourceManager.GetResource(self, filename)

###############################################################################################
koan.optimize(EffectManager)
