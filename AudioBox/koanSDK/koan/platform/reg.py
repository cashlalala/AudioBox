import os
import traceback

DefaultKey = r"HKEY_LOCAL_MACHINE\Software\CyberLink\koan"

if os.name <> 'posix':

    import _winreg

    reg_keymap = {
        'HKEY_CURRENT_USER' : _winreg.HKEY_CURRENT_USER,
        'HKEY_LOCAL_MACHINE' : _winreg.HKEY_LOCAL_MACHINE,
        'HKEY_CLASSES_ROOT' : _winreg.HKEY_CLASSES_ROOT,
        'HKEY_USERS' : _winreg.HKEY_USERS,
        'HKEY_CURRENT_CONFIG' : _winreg.HKEY_CURRENT_CONFIG,
    }

    def OpenKey(key):
        blot = key.split('\\')
        if len(blot) < 2:
            raise WindowsError, 'key error'

        if blot[0] not in reg_keymap:
            raise WindowsError, 'key error'

        root = _winreg.ConnectRegistry(None, reg_keymap[blot[0]])

        subkey = blot[1]
        for i in range(2, len(blot)):
            subkey += '\\'
            subkey += blot[i]

        return root, subkey

    def HasKey(key):
        root, subkey = OpenKey(key)
        try:
            EumKey = _winreg.OpenKey(root, subkey)
        except:
            return False
        return True

    def CreateKey(key):
        root, subkey = OpenKey(key)
        return _winreg.CreateKey(root, subkey)

    def DeleteKey(key):
        root, subkey = OpenKey(key)
        # Eumerate subkey
        try:
            EumKey = _winreg.OpenKey(root, subkey)
        except:
            # traceback.print_exc()
            return -1 # No such key

        index = 0
        try:
            while True:
                EumSubkey = '%s\\%s' % (key, _winreg.EnumKey(EumKey, index))
                DeleteKey(EumSubkey)
        except:
            pass

        try:
            _winreg.DeleteKey(root, subkey)
        except:
            traceback.print_exc()

    def SetRegistry(item, value, key = DefaultKey):
        """SetRegistry(item, key, value) -> None

        SetRegistry('test', 1, r"Software\CyberLink\koan")

        [ Only support integer and string ]
        """

        root, subkey = OpenKey(key)

        if isinstance(value, int):
            rtype = _winreg.REG_DWORD
        elif isinstance(value, str) or isinstance(value, unicode):
            rtype = _winreg.REG_SZ
        else:
            raise TypeError, 'Only support integer and string'

        try:
            y=_winreg.OpenKey(root, subkey, 0, _winreg.KEY_ALL_ACCESS)
        except:
            y = _winreg.CreateKey(root, subkey)

        _winreg.SetValueEx(y, item, 0, rtype, value)
        _winreg.CloseKey(root)

    def GetRegistry(item, default = None, key = DefaultKey, createKey = False):
        """
        GetRegistry(item, default, key) -> value

        GetRegistry('test', r"Software\CyberLink\koan", 0)
        """

        root, subkey = OpenKey(key)

        try:
            y = _winreg.OpenKey(root, subkey)
            value, type = _winreg.QueryValueEx(y, item)
            _winreg.CloseKey(y)
            _winreg.CloseKey(root)
            return value
        except WindowsError:
            if default <> None:
                if createKey:
                    SetRegistry(item, default, key)
                return default
            else:
                raise WindowsError, "No such key"


    def EnumSubKeys(key = DefaultKey):
        """EnumSubKeys(key) -> value: a list of all sub keys
        
        EnumSubKeys(r"HKEY_LOCAL_MACHINE\Software\CyberLink\koan")
        """

        strSubKeys = []
        root, subkey = OpenKey(key)
        
        try:
            y = _winreg.OpenKey(root, subkey)
            try:
                nIndex = 0
                while 1:
                    strSubKeys.append(_winreg.EnumKey(y, nIndex))
                    nIndex += 1
            except EnvironmentError:
                pass
                
            _winreg.CloseKey(y)
            _winreg.CloseKey(root)

        except WindowsError:
            pass

        return strSubKeys


    def __saveReg():
        pass

else:
    import marshal
    import os
    import anydbm
    regFilename = "/etc/reg.db"
    print 'Open Register:', regFilename,
    try:
        regpool = anydbm.open(regFilename, "c")
        print "OK!!"
    except:
        print "Fail!!"
        print "-------  warning --------"
        print "your setting in registry will be lost after turn off AP"
        print "-------------------------"
        regpool = {}
        traceback.print_exc()

    def saveReg():
        if hasattr(regpool, "sync"):
            try:
                regpool.sync()
            except:
                traceback.print_exc()

    def OpenKey(key):
        return None, None

    def HasKey(key):
        return False

    def CreateKey(key):
        return None

    def DeleteKey(key):
        pass

    def SetRegistry(item, value, key = DefaultKey):
        if key[-1] <> '\\':
            k = key + '\\' + item
        else:
            k = key + item
        k = k.upper()
        regpool[k] = str(value)
        saveReg()

    def GetRegistry(item, default = None, key = DefaultKey, createKey = False):
        if key[-1] <> '\\':
            k = key + '\\' + item
        else:
            k = key + item
        k = k.upper()

        if regpool.has_key(k):
            return regpool[k]

        if not createKey:
            raise ValueError, "No such key %s\\%s" % (key, item)

        if default:
            regpool[k] = default
        else:
            regpool[k] = ''
        saveReg()
        return default

    def EnumSubKeys(key = DefaultKey):
        strSubKeys = []
        return strSubKeys


if __name__ == '__main__':
    GetRegistry('testaaa', 1)
    SetRegistry('test', 23)
    print GetRegistry('testaaa')
