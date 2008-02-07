RIGHTSIDEUP = 0
UPSIDEDOWN = 1

FRONT = 0
BACK = 1

TOP = 0
BOTTOM = 1

class Pecha(object):
    """
    A object representing a complete pecha document.

    blockCount: number of pecha blocks (pecha pages) in the document
    blocksPerSheet: number of pecha blocks per physical sheet of paper (front
        and back)

    >>> class FakeLayout(object):
    ...   def __init__(self, *a, **k):
    ...     self.blocks = []

    # check page counts
    >>> for x in xrange(1,14+1):
    ...   p = Pecha(FakeLayout, blockCount=x)
    ...   p.blockCount, p.sheetCount
    (1, 1)
    (2, 1)
    (3, 1)
    (4, 1)
    (5, 2)
    (6, 2)
    (7, 2)
    (8, 2)
    (9, 3)
    (10, 3)
    (11, 3)
    (12, 3)
    (13, 4)
    (14, 4)

    """

    def __init__(self, klass, blockCount=0, blocksPerSheet=4):
        self.LayoutClass = klass
        self.blocksPerSheet = blocksPerSheet
        self.blockCount = blockCount
        self.sheets = []
        self.setupSheets()

    def __repr__(self):
        blockCount = sum([len(s.blocks) for s in self.sheets])
        return "<%s: %s child sheets | %s child blocks>" % (
            self.__class__.__name__, len(self.sheets), blockCount)

    def _determineSheetCount(self):
        div, mod = divmod(self.blockCount, self.blocksPerSheet)
        if mod == 0:
            self.sheetCount = div
        else:
            self.sheetCount = div + 1

    def setBlockCount(self, number):
        self._blockCount = number
        self._determineSheetCount()

    def getBlockCount(self):
        return self._blockCount
    blockCount = property(getBlockCount, setBlockCount)

    def setSheetCount(self, number):
        self._sheetCount = number

    def getSheetCount(self):
        return self._sheetCount
    sheetCount = property(getSheetCount, setSheetCount)

    def setupSheets(self):
        for sheetNum in xrange(1, self.sheetCount + 1):
            pp = self.LayoutClass(self, sheetNum, self.blocksPerSheet)
            self.sheets.append(pp)
        self.cleanupBlocks()

    def cleanupBlocks(self):
        for i, sheet in enumerate(self.sheets):
            newBlocks = []
            for j, block in enumerate(sheet.blocks):
                if block.number <= self.blockCount:
                    newBlocks.append(block)
            self.sheets[i].blocks = newBlocks

    def getBlockList(self):
        blocks = []
        for sheet in self.sheets:
            for block in sheet.blocks:
                blocks.append(block)
        blocks.sort()
        return blocks

    def getSheet(self, sheetNumber):
        for sheet in self.sheets:
            if sheet.number == sheetNumber:
                return sheet

    def getSheetByBlock(self, blockNumber):
        for sheet in self.sheets:
            for block in sheet.blocks:
                if block.number == blockNumber:
                    return sheet

class Block(object):
    """
    An object representing a block of text, classically presented on a side of
    paper with borders and text within those borders.

    paper: the parent object, the page upon which the blocks are printed
    orientation: whether the pecha text block is rightside-up on the paper or
        upside-down
    side: the front or back of the physcial paper
    location: the top of bottom of the side
    number: the pecha block number

    >>> b = Block(None, RIGHTSIDEUP, FRONT)
    >>> b.orientation == RIGHTSIDEUP
    True
    >>> b.side == FRONT
    True

    >>> b = Block(None, UPSIDEDOWN, BACK)
    >>> b.orientation == UPSIDEDOWN
    True
    >>> b.side == BACK
    True
    """
    def __init__(self, sheet, orientation=RIGHTSIDEUP, side=FRONT,
        location=TOP, number=1):
        self.sheet = sheet
        self.orientation = orientation
        self.side = side
        self.location = location
        self.number = number

    def __cmp__(self, other):
        return cmp(self.number, other.number)

    def __repr__(self):
        if self.side == FRONT:
            side = 'front'
        else:
            side = 'back'
        if self.orientation == RIGHTSIDEUP:
            orient = 'rightside-up'
        else:
            orient = 'upside-down'
        if self.location == TOP:
            loc = 'top'
        else:
            loc = 'bottom'
        return "<%s: %s | %s | sheet %s | %s | %s>" % (
            self.__class__.__name__, self.number, loc, self.sheet.number, side,
            orient)

    def setOrientation(self, const):
        self._orient = const

    def getOrientation(self):
        return self._orient
    orientation = property(getOrientation, setOrientation)

    def setSide(self, const):
        self._side = const

    def getSide(self):
        return self._side
    side = property(getSide, setSide)

    def setLocation(self, const):
        self._loc = const

    def getLocation(self):
        return self._loc
    location = property(getLocation, setLocation)

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()

