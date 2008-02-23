from pyparsing import Optional, Literal, Word, Group
from pyparsing import Suppress, Combine, replaceWith
from pyparsing import alphas, nums, printables, alphanums
from pyparsing import restOfLine, oneOf, OneOrMore, ZeroOrMore
from pyparsing import ParseException

class RTFError(Exception):
    pass

class RTFParseError(RTFError):
   "Unable to parse RTF data."

SEP = Literal(';')

BRCKT_L = Literal('{')
BRCKT_R = Literal('}')
BRCKT = BRCKT_L | BRCKT_R
BRCKT.setName("Bracket")

# basic RTF control codes, ie. "\labelname3434"
CTRL_LABEL = Combine(Word(alphas + "'") + Optional(Word(nums)))
BASE_CTRL = Combine(Literal('\\') + CTRL_LABEL)

# in some rare cases (color table declarations), control has ' ;' suffix
BASE_CTRL = Combine(BASE_CTRL + SEP) | BASE_CTRL
BASE_CTRL.setName("BaseControl")

RTF_CTRL = BASE_CTRL | HTM_CTRL
RTF_CTRL.setName("Control")

RTFCODE = OneOrMore(RTF_CTRL | BRCKT)

RTFParser = OneOrMore(RTFCODE)

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
            parsed = RFTParser.parseString(data)
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
