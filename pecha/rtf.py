from pyparsing import Optional, Literal, Word, Group
from pyparsing import Suppress, Combine, replaceWith
from pyparsing import alphas, nums, printables, alphanums
from pyparsing import restOfLine, oneOf, OneOrMore, ZeroOrMore
from pyparsing import ParseException

class RTFError(Exception):
    pass

class RTFParseError(RTFError):
   "Unable to parse RTF data."

class RTFGrammar(object):
    """
    >>> doc = r'''{\\rtf1\\ansi\\ansicpg1252\cocoartf949\cocoasubrtf270
    ... }'''
    >>> tokens = RTFGrammar().rtfDoc.parseString(doc)
    >>> tokens.version
    '1'
    >>> tokens.characterSet
    'ansi'
    """

    def __init__(self):
        separator = Literal(';')
        space = Literal(' ')
        leftBracket = Literal('{')
        rightBracket = Literal('}')
        bracket = leftBracket | rightBracket.setResultsName('bracket')

        # basic RTF control codes, ie. "\labelname3434"
        controlLabel = Combine(Word(alphas + "'") + Optional(Word(nums)))
        controlValue = Optional(space) + Optional(Word(alphanums + '-'))
        baseControl = Combine(Literal('\\') + controlLabel + controlValue
                              ).setResultsName('baseControl')

        # in some cases (color and font table declarations), control has ';' suffix
        rtfControl = Combine(baseControl + separator) | baseControl
        rtfControl.setResultsName('control')

        rtfVersionNumber = Word(nums).setResultsName('version')
        rtfVersion = Combine(Literal('\\') + 'rtf') + rtfVersionNumber

        charSet = Literal('\\') + Word(alphas).setResultsName('characterSet')

        self.rtfDoc = (leftBracket + rtfVersion + charSet +
            OneOrMore(rtfControl) +
            rightBracket
            )

class RTFParser(object):

    grammar = RTFGrammar().rtfDoc

    def __init__(self, rtfData=None):
        if rtfData:
            self.parse(rtfData)

    def parse(self, rtfData):
        """
        # setup the tests to read the test RTF files
        >>> import os.path
        >>> package, module = os.path.split(__file__)
        >>> trunk, package = os.path.split(package)
        >>> basedir = os.path.join(trunk, 'test', 'sources', 'macrtf')
        >>> def getFileData(filename):
        ...   fh = open(os.path.join(basedir, filename))
        ...   data = fh.read()
        ...   fh.close()
        ...   return data

        # simple, single-word content
        #>>> data = getFileData('simpleContent.rtf')
        #>>> try:
        #...   rp = RTFParser(data)
        #...   import pdb;pdb.set_trace()
        #... except Exception, e:
        #...   print e
        #...   print data.splitlines()
        #>>> rp.tokens
        #>>> dir(rp.tokens)
        #>>> rp.tokens.asDict()
        #>>> rp.tokens.items()
        """
        self.tokens = self.grammar.parseString(rtfData)

class RTFFile(object):
    """

    """
    def __init__(self, filename):
        self.filename = filename
        self._fonts = {}
        self.parsed = None
        self.parse()
        self.buildFontTable()

    def parse(self):
        if hasattr(self.filename, 'read'):
            fh = self.filename
        else:
            fh = open(self.filename)
        if hasattr(self.filename, 'getvalue'):
            data = fh.getvalue()
        else:
            data = fh.read()
        fh.close()
        # pass the string data into the parser
        try:
            parsed = RFTParser.parse(data)
        except ParseException, e:
            msg = "could not parse '%s'[...] : %s"
            raise RTFParseError(msg % (rtfstring[:30], e))
        self.parsed = protocol.validate(parsed)

    def setFonts(self, fontData):
        self._fonts = fontData

    def getFonts(self):
        return self._fonts

    fonts = property(getFonts, setFonts)

    def buildFontTable(self):
        """

        """

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()

