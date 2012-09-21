import os
import xml.sax
import xml.sax.handler
import traceback
import cPickle


#--------------------------------------------------------------------------------------------
# BXML (binary XML)
#--------------------------------------------------------------------------------------------
class BXMLConverter:
    token_startPrefixMapping = 0
    token_endPrefixMapping = 1
    token_startElementNS = 2
    token_characters = 3
    token_endElementNS = 4
    
class BXMLCompiler(BXMLConverter, xml.sax.handler.ContentHandler):
    def __init__(self, filename):
        self.tokens = []
        self.defaultNS = ''
        
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.setFeature(r"http://xml.org/sax/features/namespaces", True);
        
        try:
            parser.parse(filename)
        except xml.sax.SAXParseException:
            parser._source = None # workaround for closing file since parser is not deleted
            traceback.print_exc()
            print '[XML] Parse Failed !!!'
            raise
        parser.setContentHandler(None)

    @staticmethod
    def canLoadBxml(xml, bkml):
        return os.path.exists(bkml) and os.path.getmtime(bkml) > os.path.getmtime(xml)
    
    def startPrefixMapping(self, prefix, uri):
        if prefix == None:
            self.defaultNS = uri
        self.tokens.append( (BXMLConverter.token_startPrefixMapping, (prefix, uri)) )

    def endPrefixMapping(self, prefix):
        self.tokens.append( (BXMLConverter.token_endPrefixMapping, (None,)) )

    def startElementNS(self, name, qname, attrs):
        if name[0] == self.defaultNS:
            name = (u'', name[1])
        self.tokens.append( (BXMLConverter.token_startElementNS, (name, qname, attrs)) )

    def characters(self, data):
        self.tokens.append( (BXMLConverter.token_characters, (data,)) )

    def endElementNS(self, name, qname):
        if name[0] == self.defaultNS:
            name = (u'', name[1])
        self.tokens.append( (BXMLConverter.token_endElementNS, (name, qname)) )

    def save(self, filename):
        cPickle.dump( self.tokens, file(filename, 'wb'), 1 )


class BXMLParser(BXMLConverter):
    def __init__(self):
        self.op = [ self.startPrefixMapping,
                    self.endPrefixMapping,
                    self.startElementNS,
                    self.characters,
                    self.endElementNS   ]

    def parse(self, filename):
        #if koan.isProfile:
        #    t = time.clock()    
        self.tokens = cPickle.load( file(filename, 'rb') )        
        #if koan.isProfile:
        #    print 'cPickle.load ', filename, time.clock() - t            
        for tkn in self.tokens:
            self.op[tkn[0]](*tkn[1])

#########################################################
#
#   Test This Module
#
#########################################################
if __name__ == '__main__':
    try:
        fn = r'E:\CLCVS\PCM\Kanten\Generic\trunk\Custom\Skin\Standard\Photo\Layout\window.xml'
        print '[root.py] Convert BKML', fn
        x = BXMLCompiler(fn)
        x.save(os.path.splitext(fn)[0]+'.bkml')
    except:
        import traceback
        traceback.print_exc()
        print '[root.py] Convert BKML failed !!!' 
