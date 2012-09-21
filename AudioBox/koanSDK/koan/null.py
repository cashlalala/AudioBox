
#----------------------------------------------------------------
# reference: see "the null object pattern" (by google)#
#----------------------------------------------------------------
class NullObj:
    def __init__(self, *arg, **argd):   pass
    def __call__(self, *arg, **argd):   return self
    def __getattr__(self, name):        return self
    def __setattr__(self, name, value): pass
    def __nonzero__(self):              return 0
    def __delattr__(self, name):        return self
    def __repr__(self):			        return '<Null>'
    def __eq__(self, o):                return self is o or o is None
    def __ne__(self, o):                return self is not o and o is not None
    def __len__(self):                  return 0
    def __hash__(self):                 return 0

if __name__ == '__main__':
    Null = NullObj()
    print 'Null == None ====> ', Null == None
    print 'Null != None ====> ', Null != None
    print 'None == Null ====> ', None == Null
    print 'None != Null ====> ', None != Null
    print 'Null == Null ====> ', Null == Null
    print 'Null != Null ====> ', Null != Null
    print 'Null == 1 ====> ', Null == 1
    print 'Null != 1 ====> ', Null != 1
    print 'Null == 0 ====> ', Null == 0
    print 'Null != 0 ====> ', Null != 0
    print '1 == Null ====> ', Null == 1
    print '1 != Null ====> ', Null != 1
    print 'Null == 0 ====> ', Null == 0
    print 'Null != 0 ====> ', Null != 0
    print 'Null is None ====> ', Null is None
    print 'Null is not None ====> ', Null is not None
    print 'Null is Null ====> ', Null is Null
    print 'Null is not Null ====> ', Null is not Null
    print 'None is Null ====> ', None is Null
    print 'None is not Null ====> ', None is not Null
    if Null:        print 'if Null: ====> True'
    else:           print 'if Null: ====> False'
    if not Null:    print 'if not Null: ====> True'
    else:           print 'if not Null: ====> False'