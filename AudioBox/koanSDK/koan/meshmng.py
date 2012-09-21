
##################################################################################

import koan
import os
from resourcemgr import ResourceManager
###############################################################################################

class MeshManager(ResourceManager):
    """MeshManager

    Event:
        Mesh Loaded(filename)
    """
    def __init__(self, **argd):
        ResourceManager.__init__(self, **argd)
        self.autoRemove(self.window.bind("Clear Mesh", self.clear))

    def LoadResource(self, *key):
        if not key or not key[0]:
            raise ValueError, "filename is a zero string"

        mesh = self.window.render.CMesh()
        assert mesh
        fp, fn = os.path.split(key[0])
        fp += r'/'
        succ = mesh.Load(unicode(fp), unicode(fn))        
        if not succ:
            raise Exception
        self.window.render.RefreshTextures()
        return mesh

    def GetMesh(self, filename):
        return ResourceManager.GetResource(self, filename)

###############################################################################################
koan.optimize(MeshManager)
