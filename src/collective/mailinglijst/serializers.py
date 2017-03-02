
'''
XML2Py - XML to Python de-serialization

This code transforms an XML document into a Python data structure

Usage:
    deserializer = XML2Py()
    python_object = deserializer.parse( xml_string )
    print xml_string
    print python_object
'''

from lxml import etree

class XML2Py():

    def __init__( self ):

        self._parser = parser = etree.XMLParser( remove_blank_text=True )
        self._root = None  # root of etree structure
        self.data = None   # where we store the processed Python structure

    def parse( self, xmlString ):
        '''
        processes XML string into Python data structure
        '''
        self._root = etree.fromstring( xmlString, self._parser )
        self.data = self._parseXMLRoot()
        return self.data

    def tostring( self ):
        '''
        creates a string representation using our etree object
        '''
        if self._root != None:
            return etree.tostring( self._root )

    def _parseXMLRoot( self ):
        '''
        starts processing, takes care of first level idisyncrasies
        '''
        childDict = self._parseXMLNode( self._root )
        return { self._root.tag : childDict["children"] }

    def _parseXMLNode( self, element ):
        '''
        rest of the processing
        '''
        childContainer = None # either Dict or List

        # process any tag attributes
        # if we have attributes then the child container is a Dict
        #   otherwise a List
        if element.items():
            childContainer = {}
            childContainer.update( dict( element.items() ) )
        else:
            childContainer = []


        if isinstance( childContainer, list ) and element.text:
            # tag with no attributes and one that contains text
            childContainer.append( element.text )

        else:
            # tag might have children, let's process them
            for child_elem in element.getchildren():

                childDict = self._parseXMLNode( child_elem )

              # let's store our child based on container type
                #
                if isinstance( childContainer, dict ):
                    # these children are lone tag entities ( eg, 'copyright' )
                    childContainer.update( { childDict["tag"] : childDict["children"] } )

                else:
                    # these children are repeated tag entities ( eg, 'format' )
                    childContainer.append( childDict["children"] )

        return { "tag":element.tag, "children": childContainer }


'''
Py2XML - Python to XML serialization

This code transforms a Python data structures into an XML document

Usage:
    serializer = Py2XML()
    xml_string = serializer.parse( python_object )
    print python_object
    print xml_string
'''

class Py2XML():

    def __init__( self ):

        self.data = "" # where we store the processed XML string

    def parse( self, pythonObj, objName=None ):
        '''
        processes Python data structure into XML string
        needs objName if pythonObj is a List
        '''
        if pythonObj == None:
            return ""

        if isinstance( pythonObj, dict ):
            self.data = self._PyDict2XML( pythonObj )
            
        elif isinstance( pythonObj, list ):
            # we need name for List object
            self.data = self._PyList2XML( pythonObj, objName )
            
        else:
            self.data = "<%(n)s>%(o)s</%(n)s>" % { 'n':objName, 'o':str( pythonObj ) }
            
        return self.data

    def _PyDict2XML( self, pyDictObj, objName=None ):
        '''
        process Python Dict objects
        They can store XML attributes and/or children
        '''
        tagStr = ""     # XML string for this level
        attributes = {} # attribute key/value pairs
        attrStr = ""    # attribute string of this level
        childStr = ""   # XML string of this level's children

        for k, v in pyDictObj.items():

            if isinstance( v, dict ):
                # child tags, with attributes
                childStr += self._PyDict2XML( v, k )

            elif isinstance( v, list ):
                # child tags, list of children
                childStr += self._PyList2XML( v, k )

            else:
                # tag could have many attributes, let's save until later
                attributes.update( { k:v } )

        if objName == None:
            return childStr

        # create XML string for attributes
        for k, v in attributes.items():
            attrStr += " %s=\"%s\"" % ( k, v )

        # let's assemble our tag string
        if childStr == "":
            tagStr += "<%(n)s%(a)s />" % { 'n':objName, 'a':attrStr }
        else:
            tagStr += "<%(n)s%(a)s>%(c)s</%(n)s>" % { 'n':objName, 'a':attrStr, 'c':childStr }

        return tagStr

    def _PyList2XML( self, pyListObj, objName=None ):
        '''
        process Python List objects
        They have no attributes, just children
        Lists only hold Dicts or Strings
        '''
        tagStr = ""    # XML string for this level
        childStr = ""  # XML string of children

        for childObj in pyListObj:
            
            if isinstance( childObj, dict ):
                # here's some Magic
                # we're assuming that List parent has a plural name of child:
                # eg, persons > person, so cut off last char
                # name-wise, only really works for one level, however
                # in practice, this is probably ok
                childStr += self._PyDict2XML( childObj, objName[:-1] )
            else:
                for string in childObj:
                    childStr += string;

        if objName == None:
            return childStr

        tagStr += "<%(n)s>%(c)s</%(n)s>" % { 'n':objName, 'c':childStr }

        return tagStr


def xml_deserialize(xmlString):
    deserializer = XML2Py()
    return deserializer.parse(xmlString)

def xml_serialize(pyObject, root=None):
    serializer = Py2XML()
    return serializer.parse(pyObject, root)


