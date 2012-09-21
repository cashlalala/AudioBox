import koan
from koan.action import Actions
import os
import re
import xml.sax
import xml.sax.handler
import traceback
import types
import inspect
import cPickle
import time
from pprint import pprint
from bxmlcompiler import BXMLCompiler, BXMLParser

import inspect

theme = None

from component import ScriptObject
compilePyScripts = ScriptObject.compilePyScripts

#-------------------------------------------------------------------
# pre import all widget library
'''
from button import Button, TextButton, ImageButton
from text import Text
from image import Image
from edit import Edit
from dialog import Dialog
from menu import PopupMenu, MenuItem, MenuSplitter
from slider import Slider
from scrollbar import ScrollBar
from toolbar import Toolbar, Splitter, Captionbar, Caption
from menubar import Menubar, ToolbarTray, LabelToolbar, LabelButton, MenubarItem
'''
#-------------------------------------------------------------------

def actionsWithAndCondition(conditions, acts):
    for cond in conditions:
        if getattr(cond[0], cond[1]) != cond[2]:
            return False
    acts()
    return True

def actionsWithOrCondition(conditions, acts):
    for cond in conditions:
        if getattr(cond[0], cond[1]) == cond[2]:
            acts()
            return True
    return False
    
class CommandObject:
    def __init__(self):
        pass
        
    def setAttribute(self, attrs):
        pass
        
    def add(self, o):
        pass
        
    def applyCommand(self, control, **keyword):
        pass

class cmd_trigger(CommandObject):
    def __init__(self):
        CommandObject.__init__(self)
        self.event = ''
        self.condition = ''
        self.actions = []

    def setAttribute(self, attrs):
        try:
            self.event = attrs.getValueByQName('event')
        except:
            self.condition = attrs.getValueByQName('condition')
            
    def add(self, action):
        self.actions.append(action)

    def applyCommand(self, control, **keyword):
        if not self.event and not self.condition:
            print '[KXML] trigger: no event or condition !!!'
            return

        parser = keyword.get('parser', None)
        #---------------------------------------------------------------------------
        #<trigger event = 'Close Popup'>
        #    <call func = 'beginEffect.apply' args = '(["Hide"],)'/>    <-------- action
        #    <call func = 'endEffect.apply' args = '(["Common"],)'/>    <-------- action
        #</trigger>
        #---------------------------------------------------------------------------
        act = Actions()        
        for a in self.actions:
            name = a['name']
            attrs = a['attrs']
            if name == 'set':
                for n in attrs.keys():
                    d = attrs[n]
                    n = n[1]
                    try:                        
                        t = type(control.__dict__[n])
                        if t is str:
                            v = str(d)
                            if len(v) > 3 and v[:2] == '_(' and v[-1] == ')' and parser:
                                v = parser.trans(v[2:-1])
                        elif t is unicode:
                            v = unicode(d)
                            if len(v) > 3 and v[:2] == '_(' and v[-1] == ')' and parser:
                                v = parser.trans(v[2:-1])
                        else:
                            try:
                                v = eval(d, keyword)
                            except:
                                #v = keyword['parser'].queryObjectName('', d)
                                if keyword.get('parser', None):
                                    v = keyword['parser'].queryMacroValue(d)
                                else:
                                    v = eval(d, keyword['macro'])
                        act.add(setattr, control, n, v)
                    except:
                        print '[KXML] trigger set %s = %s !!!' %(n, d)
                
            elif name == 'call':
                try:
                    func = attrs.getValueByQName('func')
                except:
                    func = a['data'].strip()
                    
                func = control.getPathObject(func.split('.'), keyword.get('parser', koan.Null).root)

                try:
                    args = attrs.getValueByQName('args').strip()
                    args = eval(args)
                except:
                    args = ()

                if func:
                    act.add(func, *args)
            elif name == 'invoke':
                try:
                    evt = attrs.getValueByQName('event')
                except:
                    evt = a['data'].strip()
                try:
                    args = attrs.getValueByQName('args').strip()
                    args = eval(args)
                except:
                    args = ()
                act.add(control.invoke, *args)

        if self.event:
            #control.autoRemove( control.bind(self.event, act) )
            control.bind(self.event, act)
        else:
            #------------------------------------------------------------------------------------
            # <trigger condition = 'pressed == True'>
            #     <set background = '*media\slideshow\Slideshow_btn_p.png|(7,7,7,7)'/>
            # </trigger>
            #------------------------------------------------------------------------------------
            conditions = self.condition.split('and')
            conds = []
            for cond in conditions:
                cond = cond.strip()
                data, value = cond.split('==')
                data = data.strip()
                value = value.strip()
                ctrl = control
                if '.' in data:
                   data = data.split('.')
                   ctrl = control.getPathObject(data[:-1], keyword.get('parser', koan.Null).root)
                   data = data[-1]
                conds.append((ctrl, data, eval(value)))

            for c in conds:
                c[0].changeEvent(c[1], actionsWithAndCondition, tuple(conds), act)
            pass
    
class cmd_style(CommandObject):
    def __init__(self):
        CommandObject.__init__(self)
        self.sets = {}
        self.cmds = []
        self.cmdObjs = []
        self.macro = {}

    def setAttribute(self, attrs):
        pass
            
    def add(self, action):
        pass
        
    def applyCommand(self, control, **keyword):
        pass
            
def ns_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


#--------------------------------------------------------------------------------------------
# Namespace Parser
#--------------------------------------------------------------------------------------------
class NamespaceParser:
    controls = {}   # {'Canvas': Widgets.panel}
    modules  = {}   # {'Widgets.panel': xxxxxxx}

    def __init__(self):
        self.namespaces = {}
        
        self.macro = {}
        
        import Widgets
        NamespaceParser.controls = Widgets.NamespaceParser_controls

        # default import
        #self.startPrefixMapping(u'color', u'Widgets.color')
        self.importMacro(u'Widgets.color')

    def defineMacros(self, macros):
        macros = macros.strip().split('|')
        for macro in macros:
            macro = macro.strip()
            if macro:
                # LEFT -> 100
                n, v = macro.split('->')
                n = n.strip() # name
                v = v.strip() # value
                if n in self.macro:
                    print '[KXML] (%s) are already defined in macro, new one will override original one !!!' %n
                self.macro[n] = eval(v, self.macro)

    def importMacro(self, uri):
        module = ns_import(uri)
        if module:
            for name in module.__dict__:
                if not name.startswith('__'):
                    if name in self.macro:
                        print '[KXML] (%s) are already defined in macro, new one will override original one !!!' %name
                    self.macro[name] = getattr(module, name)
                    
    def queryMacroValue(self, name):
        try:
            return eval(name, self.macro)
        except:
            print '[KXML] No such queryMacro name (%s) !!!' %name
            raise Exception
        
    def queryObjectName(self, ns, name):
        try:
            return eval(name)
        except:
            if ns and hasattr(self.namespaces[ns], name):
                # <Canvas xmlns:c = "Widgets.color">
                return getattr(self.namespaces[ns], name)
            elif name in NamespaceParser.controls:
                # registered control, but not loaded yet
                modulename = NamespaceParser.controls[name]
                if not modulename in NamespaceParser.modules:
                    NamespaceParser.modules[modulename] = ns_import(modulename)
                self.namespaces[name] = NamespaceParser.modules[modulename]
                return getattr(self.namespaces[name], name)
            elif name in self.namespaces:
                # already loaded
                return getattr(self.namespaces[name], name)
            else: 
                # serch default import ( Ex: self.startPrefixMapping('Browser', 'Photo.Presentation.Browser') )
                for n in self.namespaces:
                    if n != ns and hasattr(self.namespaces[n], name):
                        return getattr(self.namespaces[n], name)
        print '[KXML] No such Object name (%s) !!!' %name
        raise Exception

    def startPrefixMapping(self, prefix, uri):
        #print 'startPrefixMapping', prefix, uri
        if prefix == 'x' or prefix == None:
            self.namespaces[uri] = None
        elif prefix == 'domain':
            self.trans = koan.GetTrans(uri.lower())
        else:
            self.namespaces[uri] = ns_import(uri)

    def endPrefixMapping(self, prefix):
        #print 'endPrefixMapping', prefix
        pass

#--------------------------------------------------------------------------------------------
# Style Parser
#--------------------------------------------------------------------------------------------
class KXMLStyleParser(NamespaceParser, xml.sax.handler.ContentHandler):
    caches = {}
    tagStyles   = 'Styles'
    tagStyle    = 'Style'
    tagCmdObj   = 'CmdObject'
    tagCmd      = 'Cmd'
    
    CommandObjects = ['trigger']
    def __init__(self, path, filename, **argd):
        NamespaceParser.__init__(self)
        
        self.stkData = []
        self.stkStyle = []
        self.stkProp = []
        self.stkTag = []
        fullpath = os.path.join(path, filename)
        self.path = os.path.split(fullpath)[0]
        #------------------------------------------------------------------------
        # self.styles =
        #{
        # 'name' :
        #  {
        #   'buttonA' : <style>object
        #   'buttonB' : <style>object
        #   'buttonC' : <style>object
        #  },
        #
        # 'class' :
        #  {
        #   'buttonA' : <style>object
        #   'buttonB' : <style>object
        #   'buttonC' : <style>object
        #  }
        #}
        #
        # style object
        # style.attrs = {'width': 100, height = '100', background = 'red'}
        # style.cmds = [('bind', attrs, data), ('bind', attrs, data), ('call', attrs, data)]
        # style.cmdobjs = [trigger, trigger]
        #------------------------------------------------------------------------
        self.styles = {'name':{}, 'class':{}}
        
        
        if argd.get('parse', True):
            parser = xml.sax.make_parser()
            parser.setContentHandler(self)
            parser.setFeature(r'http://xml.org/sax/features/namespaces', True);
            #if koan.isDebug:
            #    print '[KXML Style] Load Style:', os.path.abspath(fullpath)
            try:
                parser.parse(fullpath)
            except xml.sax.SAXParseException:
                parser._source = None # workaround for closing file since parser is not deleted
                traceback.print_exc()
                print '[KXML Style] Style Parse Failed !!!'
                raise
    
            #print self.styles
            parser.setContentHandler(None)
        
    def characters(self, data):
        self.stkData[-1] += data
        
    def startElementNS(self, name, qname, attrs):
        name = name[1]
        if name.lower() == 'styles':
            self.stkTag.append(KXMLStyleParser.tagStyles)
            # 
            #<Styles xmlns = "http://schemas.cyberlink.com/koan/xml/2007"
            #   xmlns:x = "$command$"
            #   reference = 'common.xml, font.xml'       <---------- reference style
            #>
            try:    ref_styles = attrs.getValueByQName('reference')
            except: ref_styles = ''
            if ref_styles:
                for ref_style in ref_styles.split(','):
                    try:
                        styles = loadStyle(self.path, ref_style.strip())
                        self.styles['name'].update(styles['name'])
                        self.styles['class'].update(styles['class'])
                    except:
                        traceback.print_exc()
                        print '[KXML Style] No such reference style(%s) !!!' %ref_style.strip()

        elif name.lower() == 'style':
            s = cmd_style()
            try:    stylename = attrs.getValueByQName('name')
            except: stylename = ''
            try:    parent = attrs.getValueByQName('parent')
            except: parent = ''
            try:    target = attrs.getValueByQName('target')
            except: target = ''

            if parent:
                parents = parent.split(',')
                for p in parents[::-1]:
                    p = p.strip()
                    if p in self.styles['name']:
                        parent_style = self.styles['name'][p]
                    else:
                        print '[KXML Style] Can not find parent style(%s) !!!' %p
                    s.sets.update(parent_style.sets)
                    s.cmds.extend(parent_style.cmds)
                    s.cmdObjs.extend(parent_style.cmdObjs)
            
            if target:
                s.target = target
                if not stylename:
                    #---------------------------------
                    # no name , so it should be a default style
                    # <style target = 'Component'>
                    #---------------------------------
                    try:
                        cls = self.queryObjectName('', target)                
                        if cls:
                            self.styles['class'][cls] = s
                    except:
                        print '[KXML Style] Can not find class (%s)!!!' %target
                        traceback.print_exc()
            if stylename:
                self.styles['name'][stylename] = s
            self.stkStyle.append(s)
            
            self.stkTag.append(KXMLStyleParser.tagStyle)
            
        elif name.lower() in KXMLStyleParser.CommandObjects:
            cls = eval('cmd_'+name.lower())
            cmd = cls()
            cmd.setAttribute(attrs)
            self.stkStyle[-1].cmdObjs.append(cmd)
            self.stkTag.append(KXMLStyleParser.tagCmdObj)
        else:
            # cmd object
            self.stkProp.append(attrs)
            self.stkTag.append(KXMLStyleParser.tagCmd)
            pass
            
        self.stkData.append('')

    def endElementNS(self, name, qname):
        name = name[1]
        data = self.stkData.pop()
        tag = self.stkTag.pop()
        
        if name.lower() == 'styles':
            pass
        elif name.lower() == 'style':
            self.stkStyle.pop()
        elif name.lower() in KXMLStyleParser.CommandObjects:
            pass
        else:
            cmdAttrs = self.stkProp.pop()
            if self.stkTag[-1] == KXMLStyleParser.tagCmdObj:
                #--------------------------------------------------------
                # <trigger event = 'xxx'>
                #   <set width = '100' height = '100' bgColor = 'red'/>    <---------------
                # </trigger>
                #--------------------------------------------------------
                prop = {
                    'name' : name,
                    'attrs' : cmdAttrs
                }
                self.stkStyle[-1].cmdObjs[-1].add(prop)
            
            elif name.lower() == 'set':
                #--------------------------------------------------------
                # <set width = '100' height = '100' bgColor = 'red'/>
                #--------------------------------------------------------
                for n in cmdAttrs.keys():
                    self.stkStyle[-1].sets[n[1]] = cmdAttrs[n]
            else:
                #------------------------------------
                # <bind> Mouse Enter -> onMouseEnter </bind>
                # <call func = 'Init'/>
                # ......
                #------------------------------------
                self.stkStyle[-1].cmds.append((name, cmdAttrs, data.strip()))

class SKMLParser(KXMLStyleParser, BXMLParser):
    def __init__(self, path, filename):
        KXMLStyleParser.__init__(self, path, filename, parse = False)
        BXMLParser.__init__(self)

def clearStyleCache():
    KXMLStyleParser.caches = {}
    
def loadStyle(path, filename):
    if theme and theme():
        filename = theme().translate(filename)

    if koan.isProfile:
        t = time.clock()
        
    fullpath = os.path.abspath(os.path.join(path, filename))
    if fullpath in KXMLStyleParser.caches:
        return KXMLStyleParser.caches[fullpath]

    #skml = os.path.splitext(fullpath)[0] + '.skml'
    skml = os.path.splitext(fullpath)[0] + '.bkml'
    xmlExist = os.path.exists(fullpath)
    
    '''
    if not koan.isDebug and os.path.exists(skml) and os.path.getmtime(skml) > os.path.getmtime(fullpath):
        styles = cPickle.load( file(skml, 'rb') )    
    elif os.path.exists(fullpath):
        styles = KXMLStyleParser(path, filename).styles
        
        if not koan.isDebug:
            # if skml does not exist, generate it!        
            cPickle.dump( styles, file(skml, 'wb'), 1)
    '''
    if not xmlExist or (not koan.isDebug and BXMLCompiler.canLoadBxml(fullpath, skml)):
        parser = SKMLParser(path, filename)
        parser.parse(skml)
        styles = parser.styles
    elif xmlExist:
        if not koan.isDebug:
            # if bkml does not exist, generate it!
            x = BXMLCompiler(fullpath)
            x.save(skml)
            
        styles = KXMLStyleParser(path, filename).styles
    else:
        print '[KXML] Can not load this style file(%s) !!!' %filename
        return None
    
    KXMLStyleParser.caches[fullpath] = styles
    
    if koan.isProfile:
        print fullpath, time.clock() - t
    return styles

def convertStyle(kxmlFilename, styleFilename):
    styles = loadStyle('', kxmlFilename)
    cPickle.dump( styles, file(styleFilename, 'wb'), 1)

#--------------------------------------------------------------------------------------------
# KXML Parser
#--------------------------------------------------------------------------------------------
class KXMLParser(NamespaceParser, xml.sax.handler.ContentHandler):
    if koan.isDebug:    
        tagUnknown          = 'Unknown Tag type'
        tagAttachedProperty = 'Attached Property'
        tagElementProperty  = 'Element Property'
        tagCommandProperty  = 'Command Property'
        tagCommandObject    = 'Command Object'
        tagControl          = 'Control'
        tagXmlRefControl    = 'XML Reference Control'        
        tagChildrenProperty = 'Children Property'
    else:    
        tagUnknown          = 0
        tagAttachedProperty = 1
        tagElementProperty  = 2
        tagCommandProperty  = 3
        tagCommandObject    = 4
        tagControl          = 5
        tagXmlRefControl    = 6
        tagChildrenProperty = 7
    @staticmethod    
    def isControl(tag):
        return tag == KXMLParser.tagControl or tag == KXMLParser.tagXmlRefControl
               
    CommandObjects = ['trigger']

    def __init__(self, filename, root, parent, autostyle, **alias):
        #t = time.clock()
        """
        @param root:
        """
        NamespaceParser.__init__(self)
        self.stkObj = []
        self.stkProp = []
        self.stkTag = []
        self.stkData = []
        self.stkAutoStyle = []

        if autostyle:
            self.stkAutoStyle = autostyle

        self.root = root
        self.parent = parent
        self.alias = alias
        self.trans = koan.Null

        self.path = os.path.split(filename)[0]

        if alias.get('parse', True):
            parser = xml.sax.make_parser()
            parser.setContentHandler(self)
            parser.setFeature(r"http://xml.org/sax/features/namespaces", True);
            #if koan.isDebug:
            #    print '[KXML] Load Layout:', os.path.abspath(filename)

            try:
                parser.parse(filename)
            except xml.sax.SAXParseException:
                parser._source = None # workaround for closing file since parser is not deleted
                traceback.print_exc()
                print '[KXML] Parse Failed !!!'
                raise

            #if koan.isDebug:
            #    print '[KXML] End Load Layout:', os.path.abspath(filename), time.clock() - t
            parser.setContentHandler(None)

    def applyStyle(self, control, style):
        for name in style.sets:
            control.setAttribute(name, style.sets[name], parser = self, _ = self.trans)
            
        for cmd in style.cmds:
            prop = {
                'name': cmd[0],
                'attrs': cmd[1],
                'data': cmd[2],
                'root': self.root
            }
            control.setCommandProperty(prop, parser = self, _ = self.trans)

        for cmdObj in style.cmdObjs:
            cmdObj.applyCommand(control, parser = self, _ = self.trans)

    def autoApplyStyle(self, control, implicit = True):
        apply = False
        autoStyles = self.stkAutoStyle[-1][1]
        mro = control.__class__.mro()
        #-------------------------------------------------
        # <x:autostyle>
        #   Button -> button |   <------------- all Button, TextButton, ImageButton will apply to it
        #   Slider -> slider
        # </x:autostyle>
        #-------------------------------------------------
        for cls in mro:
            if cls in autoStyles:
                self.applyStyle(control, autoStyles[cls])
                apply = True
                break
        if implicit and not apply:
            #-------------------------------------------------
            # no any explicit or implicit description
            # <style name = 'component'>
            #    <set gamma = 'red'/>
            # </style>
            #-------------------------------------------------
            dbStyles = self.stkAutoStyle[-1][2]['class']
            for cls in mro:
                if cls in dbStyles:
                    self.applyStyle(control, dbStyles[cls])
                    break

    def characters(self, data):
        self.stkData[-1] += data
    
    def getElementTypeNS(self, name):
        #------------------------------------------
        # 1. Control              <Button>
        # 2. Element Property     <Button.text>
        # 3. Attached Property    <DockPanel.dock>
        # 4. Command Property     <x:PyScript>
        # 5. Command Object       <x:Trigger event = ''/>
        # 6. Reference Control    <XmlRefObject path = 'panel.xml'/>
        # 7. Children Property    <XmlRefObject.btn.children>
        #------------------------------------------
        names = name[1].split('.')
        if len(names) == 1:
            if name[0] and name[0].startswith('$'):
                # xmlns:x = "$command$"
                if name[1].lower() in KXMLParser.CommandObjects:
                    return KXMLParser.tagCommandObject
                else:
                    return KXMLParser.tagCommandProperty
            elif name[1].lower() == 'xmlrefobject':
                return KXMLParser.tagXmlRefControl
            return KXMLParser.tagControl
        elif len(names) == 2 and len(self.stkObj) > 1 and (names[0].lower() == 'parent' or names[0] == self.stkObj[-2][0]):
            #if len(self.stkObj) > 1 and (names[0].lower() == 'parent' or names[0] == self.stkObj[-2][0]):
            return KXMLParser.tagAttachedProperty            
        elif names[0] == self.stkObj[-1][0] or names[0].lower() == 'self':
            if names[-1].lower() == 'children':
                return KXMLParser.tagChildrenProperty
            else:
                return KXMLParser.tagElementProperty
        return KXMLParser.tagUnknown

    def __createControl(self, ns, name, parent = None):
        try:
            cls = self.queryObjectName(ns, name)
            if cls and inspect.isclass(cls):
                if parent:
                    return cls(parent)
                else:
                    return cls()
        except:
            print traceback.print_exc()
            print '[KXML] Create %s Control failed!!!' %(name)
            return None

    def startElementNS(self, name, qname, attrs):
        #print 'startElementNS', name, qname, attrs
        self.stkData.append('')        
        tag = self.getElementTypeNS(name)            
        if KXMLParser.isControl(tag):
            if tag == KXMLParser.tagControl:
                #---------------------------------------
                # create control
                #---------------------------------------
                if len(self.stkObj) == 0:
                    if self.root is None:
                        self.root = self.__createControl(name[0], name[1], self.parent)
                    control = self.root
                else:
                    if KXMLParser.isControl(self.stkTag[-1]):
                        control = self.__createControl(name[0], name[1], self.stkObj[-1][1])
                    else:
                        control = self.__createControl(name[0], name[1])

            elif tag == KXMLParser.tagXmlRefControl:
                #---------------------------------------
                # create xml reference control
                #---------------------------------------
                try:
                    path = attrs.getValueByQName('path')
                    if theme and theme():
                        path = theme().translate(path)
                    if not os.path.exists(path):
                        path = os.path.join(self.path, path)
                    if len(self.stkObj) == 0:
                        if self.root is None:
                            self.root = loadKXML(None, path, self.parent, self.stkAutoStyle)
                        else:
                            self.root = loadKXML(self.root, path, None, self.stkAutoStyle)
                        control = self.root
                    else:
                        control = loadKXML(None, path, self.stkObj[-1][1], self.stkAutoStyle)
                except:
                    traceback.print_exc()
                    print '[KXML] XML Ref Object (%s) error!!!' %path
                    control = None

            if control:
                control.invoke('Begin KXML Node')
                self.stkObj.append((name[1], control))
    
                #---------------------------------------
                # set all attributes
                #---------------------------------------
                elementProperties = []
                attachedProperties = []
                commandProperties = []
                explicitStyle = {}
                for i in attrs.keys():
                    if tag == KXMLParser.tagXmlRefControl and i[1] == 'path':
                        continue
                    elm_type = self.getElementTypeNS(i)
                    if elm_type == KXMLParser.tagAttachedProperty:
                        #-------------------------------------------------
                        # <Button DockPanel.dock = 'top'/>
                        #-------------------------------------------------
                        prop = {
                            'name': i[1],
                            'data': attrs[i],
                            'child': control
                        }
                        attachedProperties.append(prop)
                    elif elm_type == KXMLParser.tagCommandProperty:
                        #-------------------------------------------------
                        # <Button x:style = 'btn2'/>
                        #-------------------------------------------------
                        if i[1].lower() == 'style':
                            # explicit style
                            styleName = attrs[i].strip()
                            try:
                                for as in self.stkAutoStyle[::-1]:
                                    db = as[2]['name']
                                    if styleName in db:
                                        explicitStyle = db[styleName]
                                        break
                            except:
                                print '[KXML] No such style(%s) !!!' %styleName

                        #-------------------------------------------------
                        # <Button x:macro = 'L -> 100 | T -> 20 | OFF -> 30'/>
                        #-------------------------------------------------
                        elif i[1].lower() == 'macro':
                            self.defineMacros( attrs[i] )
                            pass
                        #-------------------------------------------------
                        # <Button x:bind = 'Click -> onClick'/>
                        #-------------------------------------------------
                        else:
                            prop = {
                                'name': i[1],
                                'data': attrs[i],
                                'root': self.root
                            }
                            commandProperties.append(prop)
                    else:
                        #-------------------------------------------------
                        # Element Property
                        # 1. <Button name = 'btn'/>      <------- 'name' is heighest priority
                        # 2. <Button width = '1024'/>
                        #-------------------------------------------------
                        if i[1] == 'name' and len(self.stkObj) >= 2:
                            self.stkObj[-2][1].setNameAttribute(attrs[i], control)
                        elif i[1] == 'root_name':
                            self.root.setNameAttribute(attrs[i], control)
                        elif i[1] == 'global_name':
                            control.window.setGlobalName(attrs[i], control)
                        else:
                            elementProperties.append((i[1], attrs[i]))
    
                #-------------------------------------------------
                # apply style
                # priority:
                # 1. Explicit style
                # 2. Implicit style
                #
                #-------------------------------------------------
                if explicitStyle:
                    #-------------------------------------------------
                    #   <Button x:style = 'btn2'/>
                    #   <Button x:bindEvent = 'Click : onClick'/>
                    #-------------------------------------------------
                    self.applyStyle(control, explicitStyle)
                    pass
                elif self.stkAutoStyle:
                    #-------------------------------------------------
                    # <x:autostyle>
                    #   Button -> button |   <------------- all Button, TextButton, ImageButton will apply to it
                    #   Slider -> slider
                    # </x:autostyle>
                    #-------------------------------------------------
                    self.autoApplyStyle(control)
                #-------------------------------------------------
                # sort
                # 1. Element Properties
                # 2. Attached Properties
                # 3. Command Properties
                #-------------------------------------------------
                map(lambda x: control.setAttribute(x[0], x[1], parser = self, _ = self.trans), elementProperties)
                map(lambda x: self.stkObj[-2][1].setAttachedProperty(x, parser = self, _ = self.trans), attachedProperties)
                map(lambda x: control.setCommandProperty(x, parser = self, _ = self.trans), commandProperties)
                del elementProperties
                del attachedProperties
                del commandProperties                
            else:
                print '[KXML] Create Control (%s) Failed !!!' %name[1]
                tag = KXMLParser.tagUnknown
            
        elif tag == KXMLParser.tagCommandObject:
            #----------------------------------
            #   <x:trigger event = 'Mouse Enter' condition = 'isMouseOver == True'>
            #       <x:set width = '20' height = '20'/>
            #       <x:call function = 'setFocus'/>
            #   </x:trigger>
            #----------------------------------
            cls = eval('cmd_' + name[1])
            cmd = cls()
            cmd.setAttribute(attrs)
            self.stkProp.append({'name': name[1], 'cmd': cmd})

        elif tag == KXMLParser.tagChildrenProperty:
            #----------------------------------
            # Children Property:
            #   <Dialog.text.children>
            #       <Button/>
            #       <Button/>
            #       <Button/>
            #   </Dialog.text.children>
            #
            #   <Dialog.a.b.c.children>
            #       <Button/>
            #       <Button/>
            #       <Button/>
            #   </Dialog.a.b.c.children>
            #----------------------------------    
            assert KXMLParser.isControl(self.stkTag[-1])
            props = name[1].split('.')[1:-1]
            control = self.stkObj[-1][1]
            element = control
            for p in props:
                element = getattr(element, p, None)
            #if element and element is not control:
            if element:
                self.stkObj.append((element.__class__.__name__, element))
                tag = self.stkTag[-1]
        elif tag == KXMLParser.tagElementProperty:
            #----------------------------------
            # Element Property:
            #   <Text>
            #      <Text.text> Hello World </Text.text>
            #   </Text>
            #   <Dialog.text>
            #       <Text/>
            #   </Dialog.text>
            #   <Dialog.btn.text>
            #       <Text/>
            #   </Dialog.btn.text>
            #----------------------------------            
            assert KXMLParser.isControl(self.stkTag[-1])
            props = name[1].split('.')[1:-1]
            control = self.stkObj[-1][1]
            element = control
            for p in props:
                element = getattr(element, p, None)            
            self.stkProp.append({'name': name[1], 'attrs': attrs, 'element': element})
        elif tag != KXMLParser.tagUnknown:
            #----------------------------------
            # Attached Property:
            #   <DockPanel.dock> top </DockPanel.dock>
            #
            # Command Property:
            #   <x:bindEvent event = 'click'> onClick </x:bindEvent>
            #   <x:pyscript>
            #       def test(sef):
            #           print test
            #   </x:pyscript>
            #----------------------------------
            self.stkProp.append({'name': name[1], 'attrs': attrs})
        else:
            assert tag == KXMLParser.tagUnknown
            print '[KXML] Unknown element type (%s) !!!', name[1]
        self.stkTag.append(tag)

    def endElementNS(self, name, qname):
        #print 'endElementNS', name, qname
        data = self.stkData.pop()
        tag = self.stkTag.pop()
        if KXMLParser.isControl(tag):
            o = self.stkObj.pop()
            if self.stkAutoStyle and self.stkAutoStyle[-1][0] is o:
                self.stkAutoStyle.pop()
            #----------------------------------
            # if the parent of control is not control
            # Ex:
            # <Panel.btn>    <------ element property, not control !!!
            #   <Button/>    <------ we are here
            # </Panel.btn>
            #----------------------------------
            if len(self.stkTag):
                if not KXMLParser.isControl(self.stkTag[-1]):
                    if self.stkTag[-1] == KXMLParser.tagElementProperty:
                        if not self.stkProp[-1].has_key('objects'):
                            self.stkProp[-1]['objects'] = []
                        self.stkProp[-1]['objects'].append(o[1])
                    else:
                        print '[KXML] Control is attached to unsupport property !!!', o
                #else:
                #    self.stkObj[-1][1].addChild(o[1])
            #----------------------------------
            # set pure data to control
            # Ex:
            # <Button> Click Me </Button>
            # "Click Me" is the data
            #----------------------------------
            data = data.strip()
            if data:
                o[1].setContent(data)
                
            o[1].invoke('End KXML Node')
        elif tag == KXMLParser.tagUnknown:
            pass
        else:
            prop = self.stkProp.pop()
            prop['data'] = data
            if tag == KXMLParser.tagElementProperty:
                #-----------------------------------------
                # 1.
                # <Text.text> Hello World </Text.text>
                # 2.
                # <Panel.btn>
                #   <Button/>
                # </Panel.btn>
                # 3.
                # <Dialog.cap.caption> Hellow World </Dialog.cap.caption>
                #-----------------------------------------
                try:
                    prop['element'].setElementProperty(prop, parser = self, _ = self.trans)
                except:
                    print '[KXML] Not such element(%s)!!!' %name[1]
            elif tag == KXMLParser.tagAttachedProperty:
                #-----------------------------------------
                # <DockPanel.dock> top </DockPanel.dock>
                #-----------------------------------------
                prop['child'] = self.stkObj[-1][1]
                self.stkObj[-2][1].setAttachedProperty(prop, parser = self, _ = self.trans)
            elif tag == KXMLParser.tagCommandProperty:
                #-----------------------------------------
                # parser command (implicit style)
                # <x:autostyle file = 'style.xml'>
                #   Button -> xxx | Image -> aaa
                # </x:autostyle>
                #-----------------------------------------
                if prop['name'].lower() == 'autostyle':
                    try:
                        fn = prop['attrs'].getValueByQName('file')
                        db = loadStyle(self.path, fn)
    
                        autostyles = {}
                        descs = prop['data'].split('|')
                        for desc in descs:
                            desc = desc.strip()
                            if desc:
                                # Button -> xxx
                                c, s = desc.split('->')
                                c = c.strip() # control
                                s = s.strip() # style
                                try:
                                    c = self.queryObjectName('', c)
                                except:
                                    continue
                                if c:
                                    try:
                                        autostyles[c] = db['name'][s]
                                    except:
                                        print '[KXML] Not such style(%s)!!!' %s

                        if self.stkAutoStyle:
                            s = self.stkAutoStyle[-1][1].copy()
                            s.update(autostyles)
                            autostyles = s

                        self.stkAutoStyle.append((self.stkObj[-1], autostyles, db))    
                        #------------------------------------------------------------------------
                        # apply now   
                        # ignore case (XmlRefObject with implicit style):
                        # <XmlRefObject>
                        #   <x:autostyle file = 'style.xml'/>
                        # </XmlRefObject>
                        #------------------------------------------------------------------------
                        self.autoApplyStyle(self.stkObj[-1][1], self.stkTag[-1] == KXMLParser.tagControl)
                    except:
                        print '[KXML] autostyle failed !!!'
                        traceback.print_exc()

                elif prop['name'].lower() == 'macro':
                    self.defineMacros( prop['data'] )
                    pass
                #----------------------------------------------------------------------------------
                # other commands
                #
                # <x:bindEvent event = 'click'> onClick </x:bindEvent>
                #
                # <x:pyscript>
                #   def test(sef):
                #       print test
                # </x:pyscript>
                #----------------------------------------------------------------------------------
                else:
                    if self.stkTag[-1] == KXMLParser.tagCommandObject:
                        #----------------------------------------------------------------------------------
                        # <x:trigger event = 'Mouse Enter'>
                        #    <x:set width = '50' height = '50'/>     <-------------
                        #    <x:call func = 'onMouseEnter'/>         <-------------
                        # </x:trigger>
                        #----------------------------------------------------------------------------------
                        self.stkProp[-1]['cmd'].add(prop)
                    elif KXMLParser.isControl(self.stkTag[-1]):
                        #----------------------------------------------------------------------------------
                        # <Button>
                        #   <x:set width = '50' height = '50'/>     <-------------
                        # </Button>
                        #----------------------------------------------------------------------------------
                        prop['alias'] = self.alias
                        prop['root'] = self.root
                        self.stkObj[-1][1].setCommandProperty(prop, parser = self, _ = self.trans)
                    else:
                        print '[KXML] can not set command property to "%s" !!!' %self.stkTag[-1]
                pass
            elif tag == KXMLParser.tagCommandObject:
                #----------------------------------------------------------------------------------
                # <x:trigger event = 'Mouse Enter'>     <-------------
                #    <x:set width = '50' height = '50'/>
                #    <x:call func = 'onMouseEnter'/>
                # </x:trigger>
                #----------------------------------------------------------------------------------
                prop['cmd'].applyCommand(self.stkObj[-1][1], parser = self, _ = self.trans)

class BKMLParser(KXMLParser, BXMLParser):
    def __init__(self, filename, root, parent, autostyle, **alias):        
        KXMLParser.__init__(self, filename, root, parent, autostyle, parse = False, **alias)
        BXMLParser.__init__(self)
           

def loadKXML(self, filename, parent = None, autostyle = None, **alias):
    if theme and theme():
        filename = theme().translate(filename)

    if koan.isProfile:
        t = time.clock()
    
    bkml = os.path.splitext(filename)[0] + '.bkml'
    xmlExist = os.path.exists(filename)
    if not xmlExist or (not koan.isDebug and BXMLCompiler.canLoadBxml(filename, bkml)):
        parser = BKMLParser(filename, self, parent, autostyle, **alias)
        parser.parse(bkml)
        obj = parser.root
    elif xmlExist:
        if not koan.isDebug:
            # if bkml does not exist, generate it!
            x = BXMLCompiler(filename)
            x.save(bkml)

        obj = KXMLParser(filename, self, parent, autostyle, **alias).root
    else:
        print '[KXML] Can not load this kxml file(%s) !!!' %filename
        return None
    
    if koan.isProfile:
        print filename, time.clock() - t
    obj.invoke('Load Complete')
    return obj

#from koan.drawAgent import DrawAgent, DrawPass

#--------------------------------------------------------------------------------------------
# DrawAgent Parser
#--------------------------------------------------------------------------------------------
class XNode:
    stack = []
    def __init__(self, attrs):
        self.parent = None
        self.child = None
        self.tags = {}
        pass

    def enter(self, obj):
        if self.child:
            print 'ERROR, active object has a value'
        self.child = obj
        self.child.parent = self

    def leave(self):
        if not self.child:
            print 'ERROR, active object is none'
            return None
        c = self.child
        self.child.parent = None
        self.child = None
        return c

    def chardata(self, data):
        pass

    def passchardata(self, data):
        if self.child:
            self.child.passchardata(data)
        else:
            self.chardata(data)
            

    def start(self, name, attrs):
        if self.child:
            self.child.start(name, attrs)
            return

        #for i in range(len(self.stack)):
        #    print '\t',
        #print name

        if name in self.tags:
            self.stack.append((self, self.tags[name]))
            self.stack[-1][1](self.stack[-1][0], True, attrs)
        else:
            print 'unknow tag end:', name
            self.stack.append((None, None))
            

    def end(self, name):
        if self.child:
            self.child.end(name)
            return

        this, ptr = self.stack.pop()
        if ptr:
            ptr(this, False, None)
    
    
    def getDefine(self):
        target = self
        while target:
            if hasattr(target, "define"):
                return getattr(target, "define")
            target = target.parent
            
        raise ValueError, "cannot find define table"

    def splitOne(self, instr):
        # return (t, value)
        #  t: type -> 'v' for value
        #          -> 'a' for local anim
        #          -> 'g' for global anim
        #          -> 'f' for local function
        #          -> 'gf' for global function
        #          -> '$' for environment input
        
        instr = instr.strip()
        if not instr:
            raise ValueError, instr + " cannot understand in split step"
        
        if instr[0] == '@':
            macro = instr[1:]

            define = self.getDefine()
            if macro in define:
                t, v = define[macro]
                if t == 'd':
                    return self.splitOne(v)
                return t, v

            raise ValueError, "Undefine name->", macro

        if instr[0] == '$':
            return '$', instr[1:]
        
        return 'v', instr
            
    def split(self, instr, split = 0):
        # split = 0 means not limit number
        # return [[t, value], [], ...]
        #  t: type -> 'v' for value
        #          -> 'a' for local anim
        #          -> 'g' for global anim
        #          -> '$' for environment variable
        #
        # opt:
        #
        #
        
        sp = instr.split(',')
        
        if len(sp) == 1: # maybe it is a macro
            instr = instr.strip()
            if not instr:
                raise ValueError, "instr is zero"
            if instr[0] == '@':
                macro = instr[1:]
                define = self.getDefine()
                if macro in define:
                    t, v = define[macro]
                    if t in ['d', 'v']:
                        return self.split(v, split)
                           
            # cannot find any useable macro, try next
       
        
        r = []
        for i in sp:
            r.append(self.splitOne(i))

        if split > 0 and split <> len(r):
            raise ValueError, "len not match:" + instr + ' ' + split
            
        return r

    def getAttr(self, attrs, name, defv = ''):
        return attrs.get(name, defv)
    

class XAnim(XNode):
    def __init__(self, attrs):
        XNode.__init__(self, attrs)

        self.tags = {
            'set' : XAnim.set,
        }
        
        # method cannot set environment
        self.method = attrs.get('method', 'linear')
        
        if self.method == 'linear':
            self.dur    = self.split(attrs.get('dur', '1'), 1)[0]
            self.loop   = self.split(attrs.get('loop', 'false'), 1)[0]
            self.segment = self.split(attrs.get('segment', ''))  #*
        elif self.method == 'target':
            self.type = self.split(attrs.get('type', 'decay'), 1)[0]  #*

        self.scope  = self.split(attrs.get('scope', 'local'), 1)[0]
        self.target = []
    
    def set(self, start, attrs):
        if not start:
            return
            
        name = attrs.get('name', '')
        if not name:
            raise ValueError, "you must assign a name"
        
        value = self.split(attrs.get('value', ''))
        
        if self.method == 'linear':
            if len(value) <> len(self.segment):
                raise ValueError, "the len of value must the same as seqment"

        self.target.append((name, value))
        
        define = self.getDefine()
        define[name] = ('a', name)
        
class XDrawPass(XNode):
    def __init__(self, attrs):
        XNode.__init__(self, attrs)
        
        self.tags = {
            'define'        : XDrawPass.define,
            'anim'          : XDrawPass.anim,
            'drawrect'      : XDrawPass.drawrect,
            'alpha'         : XDrawPass.alpha,
            'pushalpha'     : XDrawPass.pushalpha,
            'popalpha'      : XDrawPass.popalpha,
            'bound'         : XDrawPass.bound,
            'group'         : XDrawPass.group,
            'translate'     : XDrawPass.translate,
            'rotate'        : XDrawPass.rotate,
            'scale'         : XDrawPass.scale,
            'pushtransform' : XDrawPass.pushtransform,
            'poptransform'  : XDrawPass.poptransform,
            'viewport'      : XDrawPass.viewport,
            'projection'    : XDrawPass.projection,
            'lookat'        : XDrawPass.lookat,
            'identity'      : XDrawPass.identity,
            'identitybound' : XDrawPass.identitybound,
            'rotate3d'      : XDrawPass.rotate3d,
            'set'           : XDrawPass.set,
            'pyscript'      : XDrawPass.script,
            'call'          : XDrawPass.call,
        }
        
        parent = attrs["@agent"]
        self.define = {}
        self.define.update(parent.define)
        
        self.anims = []
        
        self.cmd = []
        self.args = [] # [[], [], ...]
        self.name = attrs.get('name', '')
        self.dur = self.split(attrs.get('dur', '0'), 1)[0]
        self.targets = [] #[(name, dur, value), ]
        
        self.calls = {} #retname -> [(name, [args1, args2]), ]
        self.calls.update(parent.calls)
        
        self.startScript = False
        self.sdata = ""
                    
        if not self.name:
            raise ValueError, "XDrawPass must has a name"
        pass

    def call(self, start, attrs):
        if not start:
            return
            
        name = attrs.get('name', '')
        func = attrs.get('func', '')
        args = self.split(attrs.get('args', ''))
        self.calls[name] = ((func, args))
        self.define[name] = 'c', name

    def chardata(self, data):
        if self.startScript:
            self.sdata += data

    def script(self, start, attrs):
        if start:
            self.startScript = True
            self.sdata = ""
        else:
            self.startScript = False
            for f in compilePyScripts(self.sdata):
                self.define[f.__name__] = 'f', f
                
    def set(self, start, attrs):
        if not start:
            return
        for i in attrs.keys():
            self.define[i] = ('d', attrs[i])
            name  = self.split(attrs.get('target', ''), 1)[0]
            dur   = self.split(attrs.get('dur', '0'), 1)[0]
            value = self.split(attrs.get('value', '0'), 1)[0]
            self.targets.append((name, dur, value))

    def define(self, start, attrs):
        if not start:
            return
        for i in attrs.keys():
            self.define[i] = ('d', attrs[i])

    def anim(self, start, attrs):
        if start:
            self.enter(XAnim(attrs))
        else:
            self.anims.append(self.leave())

    def addCmd(self, cmd, args):
        self.cmd.append(cmd)
        self.args.append(args)

    def handleArgs(self, args):
        lst = []
        doExt = False
        for t, v in args:
            if t == 'v':
                try:
                    lst.append(float(v))
                except ValueError:
                    lst.append(v)
            elif t in ['a', 'c', '$']:
                doExt = True
                lst.append(0)
            else:
                raise ValueError, "what happen"
        
        if doExt:
            self.addCmd('PutArgs', [lst])
        
            for i in range(len(lst)):
                if args[i][0] == 'a':
                    self.addCmd('ApplyAnims', (args[i][1], i))
                elif args[i][0] == '$':
                    self.addCmd('ApplyEnvs', (args[i][1], i))
                elif args[i][0] == 'c':
                    fname, fargs = self.calls[args[i][1]]
                    if fname not in self.define:
                        print ValueError, "cannot find name:" + fname
                    
                    f = self.define[fname]
                    doNextArg = self.handleArgs(fargs)
                    self.addCmd('PutArgs', [lst]) # push again
                    self.addCmd('ExecuteFunction', (f[1], doNextArg, i))
        return lst

    def drawrect(self, start, attrs):
        if not start:
            return

        hasColor = False
        if 'color' in attrs:
            hasColor = True

            v = self.split(attrs.get('color', ''), 4)
            v = self.handleArgs(v)
            self.addCmd('SetColor', v)
            
        if 'src' in attrs:
            v = self.split(attrs.get('src', ''), 1)
            v = self.handleArgs(v)
            self.addCmd('ApplyRes', v)

        if 'apply' in attrs:
            v = self.split(attrs.get('apply', ''), 1)
            v = self.handleArgs(v)
            self.addCmd('SetTexture', v)

        if 'rect' in attrs:
            if not hasColor:
                self.addCmd('SetColor', [255, 255, 255, 255])
                
            v = self.split(attrs.get('rect', ''), 4)
            v = self.handleArgs(v)
            self.addCmd('DrawRect', v)
            
        
    def alpha(self, start, attrs):
        if start:
            v = self.split(attrs.get('a', '1.0'), 1)
            v = self.handleArgs(v)
            self.addCmd('PushAlpha', v)
        else:
            self.addCmd('PopAlpha', [])
    
    def bound(self, start, attrs):
        if start:
            if 'rect' in attrs:
                rg = [('v', 0), ('v', 0), ('v', 0), ('v', 0)]
    
                if 'region' in attrs:
                    v = self.split(attrs.get('region', '0, 0, 0, 0'), 4)
                    rg = v
                
                v = self.split(attrs.get('rect', '0, 0, 0, 0'), 4) + rg
                v = self.handleArgs(v)
                self.addCmd('PushBound', v)
        else:
            self.addCmd('PopBound', [])
    
    def translate(self, start, attrs):
        if start:
            v = self.split(attrs.get('pos', '0, 0'), 2)
            v = self.handleArgs(v)
            self.addCmd('Translate', v)

    def rotate(self, start, attrs):
        if start:
            v = self.split(attrs.get('r', '0'), 1)
            v = self.handleArgs(v)
            self.addCmd('Rotate', v)

    def scale(self, start, attrs):
        if start:
            x = self.split(attrs.get('x', '1'), 1)
            y = self.split(attrs.get('y', '1'), 1)
            v = self.handleArgs(x + y)
            self.addCmd('Scale', v)
            
    def pushalpha(self, start, attrs):
        if start:
            a = self.split(attrs.get('a', '1'), 1)
            v = self.handleArgs(a)
            self.addCmd('PushAlpha', v)

    def popalpha(self, start, attrs):
        if start:
            self.addCmd('PopAlpha', ())
        
    def pushtransform(self, start, attrs):
        if start:
            self.addCmd('PushTransform', ())

    def poptransform(self, start, attrs):
        if start:
            self.addCmd('PopTransform', ())

    def viewport(self, start, attrs):
        if start:
            pos = self.split(attrs.get('pos', '0, 0, 0, 0'), 4)
            v = self.handleArgs(pos)
            self.addCmd('SetViewport', v)

    def projection(self, start, attrs):
        if start:
            fov = self.split(attrs.get('fov', '0.39269908232375'), 1)
            aspect = self.split(attrs.get('aspect', '1'), 1)
            near = self.split(attrs.get('near', '10'), 1)
            far = self.split(attrs.get('far', '10000'), 1)
            v = self.handleArgs(fov+aspect+near+far)
            self.addCmd('SetProjMatrix', v)

    def lookat(self, start, attrs):
        if start:
            fr = self.split(attrs.get('from', '0, 0, 1'), 3)
            to = self.split(attrs.get('to', '0, 0, 0'), 3)
            up = self.split(attrs.get('up', '0, 1, 0'), 3)
            v = self.handleArgs(fr+to+up)
            self.addCmd('SetViewMatrix', v)

    def identity(self, start, attrs):
        if start:
            self.addCmd('Identity', ())

    def identitybound(self, start, attrs):
        if start:
            self.addCmd('IdentityBound', ())

    def rotate3d(self, start, attrs):
        if start:
            axis = self.split(attrs.get('axis', '0, 0, 1'), 3)
            angle = self.split(attrs.get('angle', '0'), 1)
            v = self.handleArgs(axis+angle)
            self.addCmd('Rotate3D', v)

    def group(self, start, attrs):
        if start:
            self.addCmd('PushMatrix', [])
        else:
            self.addCmd('PopMatrix', [])
                
class XDrawAgent(XNode):
    globalAnims = {}
    def __init__(self, attrs):
        XNode.__init__(self, attrs)
        
        self.tags = {
            'define'        : XDrawAgent.define,
            'anim'          : XDrawAgent.anim,
            'pass'          : XDrawAgent.passTag,
            'pyscript'      : XDrawAgent.script,
            'call'          : XDrawAgent.call,
        }
        
        self.define = {}
        self.calls = {}
        self.anims = []
        self.passes = []

        # those 2 value cannot be variable
        self.name = attrs.get('name', '')
        self.default = attrs.get('default', '')

        self.fit = 'v', attrs.get('fit', 'scale')
        self.width = 'v', attrs.get('width', '1')
        self.height = 'v', attrs.get('height', '1')

        self.startScript = False
        self.sdata = ""
        pass



    def call(self, start, attrs):
        if not start:
            return
            
        name = attrs.get('name', '')
        func = attrs.get('func', '')
        args = self.split(attrs.get('args', ''))
        self.calls[name] = ((func, args))
        self.define[name] = 'c', name

    def define(self, start, attrs):
        if not start:
            return
        for i in attrs.keys():
            self.define[i] = ('d', attrs[i])

    def anim(self, start, attrs):
        if start:
            self.enter(XAnim(attrs))
        else:
            self.anims.append(self.leave())

    def passTag(self, start, attrs):
        if start:
            attrs["@agent"] = self
            self.enter(XDrawPass(attrs))
        else:
            self.passes.append(self.leave())

    def chardata(self, data):
        if self.startScript:
            self.sdata += data

    def script(self, start, attrs):
        if start:
            self.startScript = True
            self.sdata = ""
        else:
            self.startScript = False
            for f in compilePyScripts(self.sdata):
                self.define[f.__name__] = 'f', f

class KXMLDrawAgentParser(NamespaceParser, xml.sax.handler.ContentHandler, XNode):
    caches = {}

    def __init__(self, filename, **argd):
        NamespaceParser.__init__(self)
        XNode.__init__(self, {})

        self.tags = {
            'drawagents'    : KXMLDrawAgentParser.drawagents,
            'drawagent'     : KXMLDrawAgentParser.drawagent,
        }
        
        self.agents = {}
        
        if argd.get('parse', True):
            filename = os.path.abspath(filename)
            
            parser = xml.sax.make_parser()
            parser.setContentHandler(self)
            parser.setFeature(r"http://xml.org/sax/features/namespaces", True)
            #if koan.isDebug:
            #    print '[KXML] Load DrawAgent:', filename
            try:
                parser.parse(filename)
            except xml.sax.SAXParseException:
                parser._source = None # workaround for closing file since parser is not deleted
                traceback.print_exc()
                print '[KXML] DrawAgent Parse Failed !!!'
                raise
    
            parser.setContentHandler(None)
        
    def characters(self, data):
        self.passchardata(data)
        
    def startElementNS(self, name, qname, attrs):
        name = name[1].lower()
        new_attrs = {}
        for i in attrs.getQNames():
            new_attrs[i] = attrs.getValueByQName(i)
            
        self.start(name, new_attrs)

    def endElementNS(self, name, qname):
        name = name[1].lower()
        self.end(name)

    def drawagents(self, start, attrs):
        pass

    def drawagent(self, start, attrs):
        if start:
            self.enter(XDrawAgent(attrs))
        else:
            c = self.leave()
            self.agents[c.name] = c
        pass

    def getAgent(self, name):
        try:
            return self.agents[name]
        except KeyError:
            return None

    def createAgent(self, parent, name, opt = {}):
        from drawAgent import DrawAgent
        agent = self.getAgent(name)
        return DrawAgent(parent, agent, parent.window.render, opt)

class AKMLParser(KXMLDrawAgentParser, BXMLParser):
    def __init__(self, filename):
        KXMLDrawAgentParser.__init__(self, filename, parse = False)
        BXMLParser.__init__(self)

def clearDrawAgentCache():
    KXMLDrawAgentParser.caches = {}

def loadDrawAgent(filename):
    if theme and theme():
        filename = theme().translate(filename)
        
    if filename in KXMLDrawAgentParser.caches:
        return KXMLDrawAgentParser.caches[filename]

    if koan.isProfile:
        t = time.clock()
        
    fullpath = os.path.abspath(filename)

    #akml = os.path.splitext(fullpath)[0] + '.akml'
    akml = os.path.splitext(fullpath)[0] + '.bkml'
    xmlExist = os.path.exists(fullpath)
    if not xmlExist or (not koan.isDebug and BXMLCompiler.canLoadBxml(fullpath, akml)):
        parser = AKMLParser(filename)
        parser.parse(akml)
        agents = parser
    elif xmlExist:
        if not koan.isDebug:
            x = BXMLCompiler(filename)
            x.save(akml)

        agents = KXMLDrawAgentParser(filename)

        # if skml does not exist, generate it!
        #cPickle.dump( agents, file(akml, 'wb'), 1)
    else:
        print '[KXML] Can not load this DrawAgent file(%s) !!!' %filename
        return None
    KXMLDrawAgentParser.caches[filename] = agents
    
    if koan.isProfile:
        print fullpath, time.clock() - t
    return agents

def clearParserCache():
    clearStyleCache()
    clearDrawAgentCache()
    
    
    
    

#########################################################
#
#   Test This Module
#
#########################################################
if __name__ == '__main__':
    from window import Window
    import color

    class MyWindow(Window):
        def __init__(self, parent = None):
            Window.__init__(self, parent)
            self.create(0, 0, 320, 240,
                        caption = True, defaultMaximize = True,
                        classname = 'Koan', title = 'Koan Engine'
            )
            from Widgets.kxmlparser import loadKXML
            loadKXML(self, r'E:\CLCVS\PCM\Kanten\Generic\trunk\Widgets\window.xml')
            #loadKXML(None, r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Layout\common\volumebar.xml', self)
                
    koan.init()
    
    w = MyWindow()
    w.show()
    
    koan.run(1)
    w = None
    koan.final()
    koan.traceLeak()


