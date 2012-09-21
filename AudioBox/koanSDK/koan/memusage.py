import gc
import sys


class MemoryUsage:
    def __init__(self):
        self.clear()

    def clear(self):
        self.initobj = []

    def recordInitObjs(self):
        gc.collect()
        self.initobj = dict.fromkeys(map(id,gc.get_objects()))

    def dumpAddedObjs(self, dumpfile, specifiedName = None):
        if len(self.initobj) == 0:
            return

        gc.collect()
        objs = gc.get_objects()
        x = 0
        try:
            f = file(dumpfile, 'w')
            print "total objects: %d" %(len(objs))
            for i in xrange(len(objs)):
                if id(objs[i]) not in self.initobj:
                    if specifiedName == None:
                        print >>f, str(objs[i])[:70]
                    else:
                        if str(objs[i]).startswith(specifiedName):
                            ref = gc.get_referrers(objs[i])
                            print >>f, "=============  %s ================" %specifiedName
                            print >>f, "gc.garbage: %s" % (gc.garbage)
                            print >>f, "objs[%d] = %s" % (i, objs[i])
                            print >>f, "reference counts: %d" %(sys.getrefcount(objs[i]))
                            print >>f, "referrer counts: %d" %(len(ref))
                            for r in ref:
                                #if r is not objs:
                                print >>f, ("referrers = %s" % r)[:100]
                            print >>f, "\n"
                    x += 1
            print "all new added objects %d" %(x)
            print "========================="
            f.close()
        except:
            print "can't create dumpfile for memory usage or ........"
            pass
