import ConfigParser
from ConfigParser import ConfigParser as Base
from ConfigParser import SafeConfigParser
import pickle
import types
import os

#########################################################
#
#   ConfigEx
#
#########################################################
class ConfigEx(SafeConfigParser):
    def __init__(self):
        SafeConfigParser.__init__(self)
        self.filesrc = ''
        self.path = '.'

    def read(self, filename):
        print '[ConfigEx] read', filename
        self.filesrc = filename
        self.path = os.path.split(filename)[0]
        try:
            self.readfp(file(filename, "rt"))
        except:
            print filename, 'not exist'

    def sync(self):
        if self.filesrc:
            self.write(open(self.filesrc, "wt"))

    def get(self, section, option, default = None):
        try:
            r = SafeConfigParser.get(self, section, option)
            if not r:
                return default
            else:
                try: return eval(r)
                except: return default
        except ConfigParser.NoSectionError:
            self.set(section, option, default)
        except ConfigParser.NoOptionError:
            self.set(section, option, default)
        except SyntaxError:
            pass
        return default

    def set(self, section, option, value):
        v = repr(value)
        try:
            Base.set(self, section, option, v)
        except ConfigParser.NoSectionError:
            self.add_section(section)
            Base.set(self, section, option, v)
            
#########################################################
#
#   Config
#
#########################################################

class Config(Base):
    def __init__(self):
        Base.__init__(self)
        self.filesrc = ''
        self.path = '.'

    def read(self, file):
        print '[setting.py] read', file
        self.filesrc = file
        self.path = os.path.split(file)[0]
        try:
            Base.readfp(self, open(file))
        except:
            print file, 'not exist'

    def sync(self):
        if self.filesrc:
            self.write(open(self.filesrc, "w"))

    def get(self, section, option, default = None, raw=False):
        if default == None:
            return Base.get(self, section, option)
        else:
            try:
                return Base.get(self, section, option, raw)
            except ConfigParser.NoSectionError:
                self.set(section, option, default)
            except ConfigParser.NoOptionError:
                self.set(section, option, default)
            return str(default)

    def set(self, section, option, value):
        try:
            Base.set(self, section, option, str(value))
        except ConfigParser.NoSectionError:
            self.add_section(section)
            Base.set(self, section, option, str(value))

    def getBool(self, section, option, default = None):
        v = self.get(section, option, default)
        return v.upper() == 'TRUE'

    def getInt(self, section, option, default = None):
        v = self.get(section, option, default)
        try:
            return int(v)
        except ValueError:
            if default != None:
                return default
            else:
                raise

    def getFloat(self, section, option, default = None):
        v = self.get(section, option, default)
        try:
            return float(v)
        except ValueError:
            if default != None:
                return default
            else:
                raise
                
    def setUStr(self, section, option, value):
        if type(value) != types.UnicodeType:
            try:
                value = unicode(value, "mbcs")
            except:
                value = u""
        str = pickle.dumps(value)
        self.set(section, option, str[:-5])

    def getUStr(self, section, option, value):
        default = pickle.dumps(value)[:-5]
        str = self.get(section, option, default)
        if not str:
            return value
        str += '\np0\n.'
        return pickle.loads(str)
        
    def setObjAsString(self, section, option, obj):
        string = repr(obj)
        string = string.encode('utf8')
        self.set(section, option, string)
        
    def getObjFromString(self, section, option, default = None):
        stringDefault = repr(None)
        if default != None:
            stringDefault = repr(default)
            stringDefault = stringDefault.encode('utf8')
        v = self.get(section, option, stringDefault)
        v = v.decode('utf8')
        return eval(v)

if __name__ == "__main__":
    import sys
    c = Config()
    c.read(r"c:\a.ini")
    print c.get("TESTS", "a", 123)
    print c.get("TEST2", "a", 123)
    print c.get("TEST2", "XXXX", 123.0)
    print c.get("GYGY", "a", 123.0)
    print c.get("GYGY2", "c", "Hello World")
    c.write(sys.stdout)
    c.sync()

    c = ConfigEx()
    c.read(r"c:\b.ini")
    c.set("test", "a0", "adfasdfas")
    c.set("test", "a1", 123)
    c.set("test", "a2", True)
    c.set("test", "a3", u"adfasdfas")
    c.set("test", "a4", None)
    c.set("test", "a5", (1, 2, 3, "adfasdfa"))
    c.set("test", "a6", [1, 2, 3, "adfasdfa"])
    c.set("test", "a7", {3:2, 4:"asdfasdf"})
    
    for i in range(10):
        print c.get("test", "a%d"%i)
    
    print c.get("test", "a7")[4]
    c.sync()
    