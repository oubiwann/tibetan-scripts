import math

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

    >>> from itertools import chain

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

    #>>> s = Sheet(p, 1)
    >>> p.blockCount, p.sheetCount
    (1, 1)
    >>> for b in chain(*[sh.blocks for sh in p.sheets]):
    ...   print b
    <Block: 1 | top | sheet 1 | back | upside-down>

    # special case with two pecha pages
    >>> p = Pecha(blockCount=2)
    >>> s = Sheet(p, 1)
    >>> p.blockCount, p.sheetCount
    (2, 1)
    >>> for b in chain(*[sh.blocks for sh in p.sheets]):
    ...   print b
    <Block: 2 | top | sheet 1 | front | rightside-up>
    <Block: 1 | top | sheet 1 | back | upside-down>

    # special case with four pecha pages
    >>> p = Pecha(blockCount=4)
    >>> p.blockCount, p.sheetCount
    (4, 1)
    >>> for b in chain(*[sh.blocks for sh in p.sheets]):
    ...   print b
    <Block: 2 | top | sheet 1 | front | rightside-up>
    <Block: 3 | bottom | sheet 1 | front | rightside-up>
    <Block: 1 | top | sheet 1 | back | upside-down>
    <Block: 4 | bottom | sheet 1 | back | upside-down>

    # special case with six pecha pages
    >>> p = Pecha(blockCount=6)
    >>> p
    <Pecha: 2 child sheets | 6 child blocks>
    >>> p.blockCount, p.sheetCount
    (6, 2)
    >>> for b in chain(*[sh.blocks for sh in p.sheets]):
    ...   print b
    <Block: 2 | top | sheet 1 | front | rightside-up>
    <Block: 1 | top | sheet 1 | back | upside-down>
    <Block: 4 | top | sheet 2 | front | rightside-up>
    <Block: 5 | bottom | sheet 2 | front | rightside-up>
    <Block: 3 | top | sheet 2 | back | upside-down>
    <Block: 6 | bottom | sheet 2 | back | upside-down>

    # special case with eight pecha pages
    >>> p = Pecha(blockCount=8)
    >>> p
    <Pecha: 2 child sheets | 8 child blocks>
    >>> p.blockCount, p.sheetCount
    (8, 2)
    >>> p.sheets[0].number
    1
    >>> p.sheets[1].number
    2

    >>> for b in p.getBlockList():
    ...   print b
    <Block: 1 | top | sheet 1 | back | upside-down>
    <Block: 2 | top | sheet 1 | front | rightside-up>
    <Block: 3 | top | sheet 2 | back | upside-down>
    <Block: 4 | top | sheet 2 | front | rightside-up>
    <Block: 5 | bottom | sheet 2 | front | rightside-up>
    <Block: 6 | bottom | sheet 2 | back | upside-down>
    <Block: 7 | bottom | sheet 1 | front | rightside-up>
    <Block: 8 | bottom | sheet 1 | back | upside-down>

    # now, in block order (top to bottom, front to back)
    >>> for b in chain(*[sh.blocks for sh in p.sheets]):
    ...   print b
    <Block: 2 | top | sheet 1 | front | rightside-up>
    <Block: 7 | bottom | sheet 1 | front | rightside-up>
    <Block: 1 | top | sheet 1 | back | upside-down>
    <Block: 8 | bottom | sheet 1 | back | upside-down>
    <Block: 4 | top | sheet 2 | front | rightside-up>
    <Block: 5 | bottom | sheet 2 | front | rightside-up>
    <Block: 3 | top | sheet 2 | back | upside-down>
    <Block: 6 | bottom | sheet 2 | back | upside-down>

    # special case with 14 pecha pages
    >>> p = Pecha(blockCount=14)
    >>> p
    <Pecha: 4 child sheets | 14 child blocks>

    >>> p.blockCount, p.sheetCount
    (14, 4)
    >>> len(p.sheets) == p.sheetCount
    True
    >>> for b in chain(*[sh.blocks for sh in p.sheets]):
    ...   print b
    <Block: 2 | top | sheet 1 | front | rightside-up>
    <Block: 1 | top | sheet 1 | back | upside-down>
    <Block: 4 | top | sheet 2 | front | rightside-up>
    <Block: 13 | bottom | sheet 2 | front | rightside-up>
    <Block: 3 | top | sheet 2 | back | upside-down>
    <Block: 14 | bottom | sheet 2 | back | upside-down>
    <Block: 6 | top | sheet 3 | front | rightside-up>
    <Block: 11 | bottom | sheet 3 | front | rightside-up>
    <Block: 5 | top | sheet 3 | back | upside-down>
    <Block: 12 | bottom | sheet 3 | back | upside-down>
    <Block: 8 | top | sheet 4 | front | rightside-up>
    <Block: 9 | bottom | sheet 4 | front | rightside-up>
    <Block: 7 | top | sheet 4 | back | upside-down>
    <Block: 10 | bottom | sheet 4 | back | upside-down>


    >>> len(p.getSheet(1).blocks)
    2

    >>> print p.getSheetByBlock(11)
    <Sheet: sheet 3 | 4 child blocks>

    """

    def __init__(self, blockCount=0, blocksPerSheet=4):
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
            pp = Sheet(self, sheetNum, self.blocksPerSheet)
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

    def getPageList(self):
        pass

    def getSheet(self, sheetNumber):
        for sheet in self.sheets:
            if sheet.number == sheetNumber:
                return sheet

    def getSheetByBlock(self, blockNumber):
        for sheet in self.sheets:
            for block in sheet.blocks:
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
    >>> p.cleanupBlocks()
    >>> p.sheets[0] == s
    True
    >>> for block in p.sheets[0].blocks:
    ...   print block
    <Block: 1 | top | sheet 1 | back | upside-down>

    >>> len(p.sheets[0].blocks) == 1
    True

    >>> p = Pecha(4)
    >>> s = Sheet(p, 1)
    >>> len(s.blocks) == 4
    True
    >>> for block in s.blocks:
    ...   print block
    <Block: 2 | top | sheet 1 | front | rightside-up>
    <Block: 3 | bottom | sheet 1 | front | rightside-up>
    <Block: 1 | top | sheet 1 | back | upside-down>
    <Block: 4 | bottom | sheet 1 | back | upside-down>

    >>> p = Pecha(6)
    >>> s = Sheet(p, 1)
    >>> p.cleanupBlocks()

    # the first page should have 2 blocks and the second should have 4 for a
    # total of 6 blocks (but we're just creating and checking the first page)
    >>> len(p.sheets[0].blocks) == 2
    True
    >>> for block in p.sheets[0].blocks:
    ...   print block
    <Block: 2 | top | sheet 1 | front | rightside-up>
    <Block: 1 | top | sheet 1 | back | upside-down>


    """
    def __init__(self, document, number, blocks=4):
        self.document = document
        self.number = number
        self.blocks = []
        self.blocksPerSheet = blocks
        self.remainder = number * blocks - document.blockCount
        self.maxBlocks = int(math.ceil(document.blockCount/float(blocks)) *
                             blocks)
        self.setupBlocks()
        self.document.cleanupBlocks()

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

        To generalize for more than just the 2-sheet (8 block max) example, we
        make one change:
            (((LOC * (MAX - 1)) + 1) + 2 * ((LOC * 2 * -1) + 1) * (SHEET - 1)) +
                ((LOC * 2 * -1) + 1) * (abs(SIDE - 1))

        This final form is what was used as the algorithm for determining the
        block number.
        """
        if self.document.blockCount < 0:
            print 'called!!!'
            print self.blocks
        for side in xrange(2):
            orientation = side
            sideModifier = abs(side - 1)
            for location in xrange(2):
                signModifier = ((location * - 2) + 1)
                minMaxModifier = ((location * (self.maxBlocks - 1)) + 1)
                relativeBlockNum = (
                    minMaxModifier + 2 * signModifier * (self.number - 1)
                    + sideModifier * signModifier)
                #sheetSet = int(math.ceil(self.number/2.0))
                #blockNum = (relativeBlockNum + (sheetSet - 1) *
                #    (self.blocksPerSheet * 2))
                blockNum = relativeBlockNum
                if self.document.blockCount > 14:
                    print sheetSet, self.number, relativeBlockNum, blockNum
                p = Block(self, orientation, side, location, blockNum)
                self.blocks.append(p)
        #self.r = (self.number, self.blocksPerSheet, self.document.blockCount, self.remainder)
        #print self.document.blockCount, self.number, self.number * self.blocksPerSheet, remainder
        if self.document.blockCount > 14:
            print 'halfway!!!'
            print self.blocks
        # now for some cleanup - we may need to trim the blocks
        #
        # since we have a remainder, we know this is the last sheet (and
        # thus last set of blocks) in the pecha; what we now want to do is
        # remove all blocks higher than the index implied by the remainder,
        # but this is tricky since the blocks are non-sequential and spread
        # across both sides of the sheet

        stopIndex = self.blocksPerSheet - self.remainder
        #if self.document.blockCount < 0:
        #    for i, sheet in enumerate(self.document.sheets):
        #        if i < 1:
        #            print '            .'
        #            print "Before (%s/%s)" % (self.document.blockCount, self.maxBlocks)
        #        print sheet
        #        for block in sheet.blocks:
        #            print block
        '''
        for i, sheet in enumerate(self.document.sheets):
            newBlocks = []
            for j, block in enumerate(sheet.blocks):
                if self.document.blockCount < 0:
                    print block.number, stopIndex, block, self.maxBlocks
                if block.number <= self.document.blockCount:
                    newBlocks.append(block)
            #print stopIndex, self.remainder, self.blocks
            if self.document.blockCount < 2:
                print self.document.sheets[i].number, self.number, len(self.blocks), len(newBlocks)
                print self.document.sheets[i].blocks == self.blocks
            self.document.sheets[i].blocks = newBlocks
            if self.document.sheets[i].number == self.number:
                self.blocks = newBlocks
        '''
        #i = 0
        #if self.document.blockCount < 0:
        #    for i, sheet in enumerate(self.document.sheets):
        #        if i < 1:
        #            print "After (%s/%s)" % (self.document.blockCount, self.maxBlocks)
        #        print sheet
        #        for block in sheet.blocks:
        #            print block
        #    if i:
        #        print '            .'
        #if self.document.blockCount < 0:
        #    print self.blocks
        #    print 'finished!!!'

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

