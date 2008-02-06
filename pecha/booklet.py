import math

# XXX move into pecha.base
RIGHTSIDEUP = 0
UPSIDEDOWN = 1

FRONT = 0
BACK = 1

TOP = 0
BOTTOM = 1

# XXX move into pecha.base
class Pecha(object):
    """
    A object representing a complete pecha document.

    blockCount: number of pecha blocks (pecha pages) in the document
    blocksPerSheet: number of pecha blocks per physical sheet of paper (front
        and back)

    # check page counts
    >>> for x in xrange(1,14+1):
    ...   p = Pecha(blockCount=x)
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

    # now, let's test some special cases... first, with just one page
    >>> p = Pecha(blockCount=1)
    >>> p.blockCount, p.sheetCount
    (1, 1)

    # spectial case with two pecha pages
    >>> p = Pecha(blockCount=2)
    >>> p.blockCount, p.sheetCount
    (2, 1)

    # spectial case with six pecha pages
    >>> p = Pecha(blockCount=6)
    >>> p.blockCount, p.sheetCount
    (6, 2)

    # spectial case with eight pecha pages
    >>> p = Pecha(blockCount=8)
    >>> p.blockCount, p.sheetCount
    (8, 2)
    >>> p.sheets[0].number
    1
    >>> p.sheets[1].number
    2

    >>> for b in p.getBlockList():
    ...   print b
    <Block: block 1 | top of page 1 | back side | upside-down>
    <Block: block 2 | top of page 1 | front side | rightside-up>
    <Block: block 3 | top of page 2 | back side | upside-down>
    <Block: block 4 | top of page 2 | front side | rightside-up>
    <Block: block 5 | bottom of page 2 | front side | rightside-up>
    <Block: block 6 | bottom of page 2 | back side | upside-down>
    <Block: block 7 | bottom of page 1 | front side | rightside-up>
    <Block: block 8 | bottom of page 1 | back side | upside-down>

    # now, in page order (top to bottom, front to back)
    >>> from itertools import chain
    >>> for b in chain(*[sh.blocks for sh in p.sheets]):
    ...   print b
    <Block: block 2 | top of page 1 | front side | rightside-up>
    <Block: block 7 | bottom of page 1 | front side | rightside-up>
    <Block: block 1 | top of page 1 | back side | upside-down>
    <Block: block 8 | bottom of page 1 | back side | upside-down>
    <Block: block 4 | top of page 2 | front side | rightside-up>
    <Block: block 5 | bottom of page 2 | front side | rightside-up>
    <Block: block 3 | top of page 2 | back side | upside-down>
    <Block: block 6 | bottom of page 2 | back side | upside-down>

    # spectial case with 14 pecha pages
    #>>> p = Pecha(blockCount=14)
    #>>> p.blockCount, p.sheetCount
    #(14, 4)
    #>>> len(p.sheets) == p.sheetCount
    #True

    #>>> len(p.getSheet(4).blocks)
    #2
    #>>> print p.getSheetByBlock(11)

    # spectial case with 32 pecha pages
    #>>> p = Pecha(blockCount=32)
    #>>> for b in p.getBlockList():
    #...   print b
    #>>> for b in chain(*[sh.blocks for sh in p.sheets]):
    #...   print b

    """

    def __init__(self, blockCount=0, blocksPerSheet=4):
        self.blocksPerSheet = blocksPerSheet
        self.blockCount = blockCount
        self.sheets = []
        self.setupSheets()

    def __repr__(self):
        # XXX include number of children (blocks) in repr
        pass

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
            pp = Sheet(self, sheetNum, self.blocksPerSheet)
            self.sheets.append(pp)

    def getBlockList(self):
        blocks = []
        for sheet in self.sheets:
            for block in sheet.blocks:
                blocks.append(block)
        blocks.sort()
        return blocks

    def getPageList(self):
        pass

    def getSheet(self, sheetNumber):
        for sheet in self.sheets:
            if sheet.number == sheetNumber:
                return sheet

    def getSheetByBlock(self, blockNumber):
        for sheet in self.sheets:
            print sheet
            for block in sheet.blocks:
                print block
                if block.number == blockNumber:
                    return sheet

# XXX Once this code has passing tests, we need to move the Pecha and PechaPage
# objects into a "base" module, leaving Sheet in the booklet module. The
# pecha object will need to be updated to have the ability to create different
# physical page instances, depending upon parameters passed to the constructor.

# XXX move into pecha.layouts.booklet; will need to import orientation and side
# constants
class Sheet(object):
    """
    An object representing a two-sided, pysical piece of paper.

    document: the parent object, the pecha itself
    page: page number
    blocks: number of pecha pages per physical sheet of paper (front and back)

    # check that the "child" pecha pages get created properly
    >>> p = Pecha(1)
    >>> s = Sheet(p, 1)
    >>> len(s.blocks) == 1
    True

    >>> p = Pecha(4)
    >>> s = Sheet(p, 1)
    >>> len(s.blocks) == 4
    True
    >>> for block in s.blocks:
    ...   print block
    <Block: block 1 | top of page 1 | back side | upside-down>
    <Block: block 2 | top of page 1 | front side | rightside-up>
    <Block: block 3 | bottom of page 1 | front side | rightside-up>
    <Block: block 4 | bottom of page 1 | back side | upside-down>

    >>> p = Pecha(6)
    >>> s = Sheet(p, 2)

    # the first page shoudl have 4 blocks and the second should have 2 for a
    # total of 6 blocks (but we're just checking the second page)
    >>> len(s.blocks) == 2
    True
    >>> len(s.blocks)
    >>> for block in s.blocks:
    ...   print block
    <Block: block 5 | bottom of page 2 | front side | rightside-up>
    <Block: block 6 | bottom of page 2 | back side | upside-down>

    """
    def __init__(self, document, number, blocks=4):
        self.document = document
        self.number = number
        self.blocks = []
        self.blocksPerSheet = blocks
        self.setupBlocks()

    def __cmp__(self, other):
        return cmp(self.number, other.number)

    def __repr__(self):
        return "<%s: sheet %s | %s child blocks>" % (
            self.__class__.__name__, self.number, len(self.blocks))

    def setupBlocks(self):
        """
        Created the pecha pages needed for this physical page.

        The logic for this is simple, but tedious. Examples should help. Let's
        take a single page, first:

            +------+
            | 1    |
            |......|
            |      |
            +------+

        The above "image" represents a piece of paper. If folded in half along
        the dotted line (a mini-booklet), we could read as manny as four blocks
        printed on this sheet. The blocks would have the following attributes:

            block 1 | top | page 1 | back | upside-down
            block 2 | top | page 1 | front | rightside-up
            block 3 | bottom | page 1 | front | rightside-up
            block 4 | bottom | page 1 | back | upside-down

        With two sheets of paper, we would have the following:

            +------+
            | 1 +------+
            |...| 2    |
            |   |......|
            +---|      |
                +------+

            block 1 | top | page 1 | back | upside-down
            block 2 | top | page 1 | front | rightside-up
            block 3 | top | page 2 | back | upside-down
            block 4 | top | page 2 | front | rightside-up
            block 5 | bottom | page 2 | front | rightside-up
            block 6 | bottom | page 2 | back | upside-down
            block 7 | bottom | page 1 | front | rightside-up
            block 8 | bottom | page 1 | back | upside-down

        Sorting this in page order (top to bottom, front to back) instead of
        block order, we get:

            sheet 1 | front | top | block 2 | rightside-up
            sheet 1 | front | bottom | block 7 | rightside-up
            sheet 1 | back | top | block 1 | upside-down
            sheet 1 | back | bottom | block 8 | upside-down
            sheet 2 | front | top | block 4 | rightside-up
            sheet 2 | front | bottom | block block 5 | rightside-up
            sheet 2 | back | top | block 3 | upside-down
            sheet 2 | back | bottom | block 6 | upside-down

        Looking at it in this order, we witness the following pattern:

            2   inner a + 1         front
            7   inner n - 1         front
            1   outer a             back
            8   outer n             back
            4   inner (a+2) + 1     front
            5   inner (n-2) - 1     front
            3   outer (a+2)         back
            6   outer (n-2)         back

        And this pattern yields the following representations, in increasing
        generality:

            Representation 1, where MIN=1, MAX=8, and SHEET ranges from 1 to 2:
            (MIN + 2 * (SHEET - 1)) + 1
            (MAX - 2 * (SHEET - 1)) - 1
            (MIN + 2 * (SHEET - 1))
            (MAX - 2 * (SHEET - 1))

            Representation 2, same as above and with SIDE ranging from 0 to 1:
            (MIN + 2 * (SHEET - 1)) + (1 * abs(SIDE - 1))
            (MAX - 2 * (SHEET - 1)) - (1 * abs(SIDE - 1))

            Representation 3, same as above and with LOC ranging from 0 to 1:
            (((LOC * 7) + 1) + 2 * ((LOC * 2 * -1) + 1) * (SHEET - 1)) +
                ((LOC * 2 * -1) + 1) * (abs(SIDE - 1))

        This final form is what was used as the algorithm for determining the
        block number.
        """
        for side in xrange(2):
            orientation = side
            sideModifier = abs(side - 1)
            for location in xrange(2):
                signModifier = ((location * -2) + 1)
                minMaxModifier = ((location * 7) + 1)
                relativeBlockNum = (
                    minMaxModifier + 2 * signModifier * (self.number - 1)
                    + sideModifier * signModifier)
                sheetSet = int(math.ceil(self.number/2.0))
                blockNum = relativeBlockNum + (sheetSet - 1) * (self.blocksPerSheet * 2)
                #print self.number, self.number, side, location, blockNum
                p = Block(self, orientation, side, location, blockNum)
                self.blocks.append(p)
        # now for some cleanup - we may need to trim the blocks
        remainder = self.number * self.blocksPerSheet - self.document.blockCount
        #print self.document.blockCount, self.number, self.number * self.blocksPerSheet, remainder
        if remainder > 0:
            # since we have a remainder, we know this is the last sheet (and
            # thus last set of blocks) in the pecha; what we now want to do is
            # remove all blocks higher than the index implied by the remainder,
            # but this is tricky since the blocks are non-sequential and spread
            # across both sides of the sheet
            stopIndex = self.blocksPerSheet - remainder
            print '            .'
            print "Before"
            for sheet in self.document.sheets:
                print sheet
                for block in sheet.blocks:
                    print block
            for i, sheet in enumerate(self.document.sheets):
                newBlocks = []
                for j, block in enumerate(sheet.blocks):
                    if block.number <= self.document.blockCount:
                        print i, j, block.number, stopIndex, block
                        newBlocks.append(block)
                #print stopIndex, remainder, self.blocks
                self.document.sheets[i].blocks = newBlocks
            print "After"
            for sheet in self.document.sheets:
                print sheet
                for block in sheet.blocks:
                    print block
            print '            .'

# XXX move into pecha.base
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
        return "<%s: block %s | %s of page %s | %s side | %s>" % (
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

