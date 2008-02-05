def printLayoutReport(totalPechaPages):
    div, mod = divmod(totalPechaPages, 4)
    if mod == 0:
        totalActualPages = div
    else:
        totalActualPages = div + 1

    for currentPage in xrange(1, totalPechaPages + 1):
        if currentPage <= totalPechaPages / 2.0:
            firstHalf = True
        else:
            firstHalf = False
        secondHalf = not firstHalf
        if firstHalf:
            currentActualPage = int(currentPage / 2.0 + 0.5)
        else:
            currentActualPage = totalPechaPages - int(currentPage / 2.0 + 0.5)# - 3
        if ((firstHalf and (currentPage % 2) == 1) or (secondHalf and (currentPage % 2) == 0)):
            orientation = 'upsidedown'
            side = '2nd'
        else:
            orientation = 'rightsideup'
            side = '1st'
        print currentPage, currentActualPage, side, orientation, firstHalf, secondHalf

for tpp in xrange(1,8 + 1):
    printLayoutReport(tpp)
    print "\n"

def getOrientation():
    pass


# XXX move into pecha.base
RIGHTSIDEUP = 0
UPSIDEDOWN = 1
FRONT = 0
BACK = 1

# XXX move into pecha.base
class Pecha(object):
    """
    A object representing a complete pecha document.

    pages: number of pecha blocks (pecha pages) in the document
    blocks: number of pecha pages per physical sheet of paper (front and back)
    # check page counts
    >>> for x in xrange(1,14+1):
    ...   p = Pecha(pages=x)
    ...   p.pageCount, p.physicalPageCount
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
    >>> p = Pecha(pages=1)
    >>> p.pageCount, p.physicalPageCount
    (1, 1)

    # spectial case with two pecha pages
    >>> p = Pecha(pages=2)
    >>> p.pageCount, p.physicalPageCount
    (2, 1)

    # spectial case with six pecha pages
    >>> p = Pecha(pages=6)
    >>> p.pageCount, p.physicalPageCount
    (6, 2)

    # spectial case with eight pecha pages
    >>> p = Pecha(pages=8)
    >>> p.pageCount, p.physicalPageCount
    (8, 2)

    # spectial case with 14 pecha pages
    >>> p = Pecha(pages=14)
    >>> p.pageCount, p.physicalPageCount
    (14, 4)
    >>> len(p.pages) == p.physicalPageCount
    True
    """

    def __init__(self, pages, blocks=4):
        self.pageCount = pages
        self.blocks = blocks
        self.pages = []
        self.setupPages()

    def _determinePhysicalPageCount(self):
        div, mod = divmod(self.pageCount, 4)
        if mod == 0:
            self.physicalPageCount = div
        else:
            self.physicalPageCount = div + 1

    def setPageCount(self, number):
        self._pageCount = number
        self._determinePhysicalPageCount()

    def getPageCount(self):
        return self._pageCount
    pageCount = property(getPageCount, setPageCount)

    def setPhysicalPageCount(self, number):
        self._physicalPageCount = number

    def getPhysicalPageCount(self):
        return self._physicalPageCount
    physicalPageCount = property(getPhysicalPageCount, setPhysicalPageCount)

    def setupPages(self):
        for pageNum in xrange(1, self.physicalPageCount + 1):
            pp = PhysicalPage(self, pageNum, self.blocks)
            self.pages.append(pp)

# layouts are determined by how pecha pages are displayed on the physical
# page. The logic for these decisions is the responsibility of the physical
# page object. As such, there will need to be a different physical page object
# for each type of page layout desired.

# XXX Once this code has passing tests, we need to move the Pecha and PechaPage
# objects into a "base" module, leaving PhysicalPage in the booklet module. The
# pecha object will need to be updated to have the ability to create different
# physical page instances, depending upon parameters passed to the constructor.

# XXX move into pecha.layouts.booklet; will need to import orientation and side
# constants
class PhysicalPage(object):
    """
    An object representing a two-sided, pysical piece of paper.

    number: page number
    blocks: number of pecha pages per physical sheet of paper (front and back)

    # check that the "child" pecha pages get created properly
    >>> p = Pecha(1)
    >>> pp = PhysicalPage(p, 1)
    >>> len(pp.blocks) == 1
    True

    >>> p = Pecha(4)
    >>> pp = PhysicalPage(p, 1)
    >>> len(pp.blocks) == 4
    True
    >>> for block in pp.blocks:
    ...   print block
    <PechaPage: block 1 | page 1 | back side | upside-down>
    <PechaPage: block 2 | page 1 | front side | rightside-up>
    <PechaPage: block 3 | page 1 | front side | rightside-up>
    <PechaPage: block 4 | page 1 | back side | upside-down>

    >>> p = Pecha(6)
    >>> pp = PhysicalPage(p, 2)

    # the first page shoudl have 4 blocks and the second should have 2 for a
    # total of 6 blocks (but we're just checking the second page)
    >>> len(pp.blocks) == 2
    True
    >>> for block in pp.blocks:
    ...   print block
    <PechaPage: block 5 | page 2 | front side | rightside-up>
    <PechaPage: block 6 | page 2 | back side | upside-down>

    """
    def __init__(self, document, number=1, blocks=4):
        self.document = document
        self.number = number
        self.blocks = []
        self.blockCount = blocks
        self.setupPages()


    def setupPages(self):
        """
        Created the pecha pages needed for this physical page.
        """
        for blockNum in xrange(1, self.blockCount + 1):
            # "startCount" is the varaible used to caculate the current pecha
            # page. The current physical page number times the number of
            # blocks per physical page will give us the highest block number
            # for the current page -- not what we want: if we're on block 13,
            # that would give us 16. For 13-16, we want to start with the
            # total block count for the previous physical page, in this
            # example, 12.
            startCount = (self.number - 1) * self.blockCount
            currentPage = startCount + blockNum
            if currentPage > self.document.pageCount:
                break
            if currentPage <= self.document.pageCount / 2.0:
                firstHalf = True
            else:
                firstHalf = False
            secondHalf = not firstHalf
            #print blockNum, startCount + blockNum, self.number, self.document.pageCount
            # determine oritentation and side of paper for block
            if ((firstHalf and (currentPage % 2) == 1) or
                (secondHalf and (currentPage % 2) == 0)):
                orientation = UPSIDEDOWN
                side = BACK
            else:
                orientation = RIGHTSIDEUP
                side = FRONT
            p = PechaPage(self, orientation, side, currentPage)
            self.blocks.append(p)

# XXX move into pecha.base
class PechaPage(object):
    """
    An object representing a block of text, classically presented on a side of
    paper with borders and text within those borders.

    orientation: whether the pecha text block is rightside-up on the paper or
        upside-down
    side: the front or back of the physcial paper
    number: the pecha block number

    >>> pp = PechaPage(None, RIGHTSIDEUP, FRONT)
    >>> pp.orientation == RIGHTSIDEUP
    True
    >>> pp.side == FRONT
    True

    >>> pp = PechaPage(None, UPSIDEDOWN, BACK)
    >>> pp.orientation == UPSIDEDOWN
    True
    >>> pp.side == BACK
    True
    """
    def __init__(self, paper, orientation=RIGHTSIDEUP, side=FRONT, number=1):
        self.paper = paper
        self.orientation = orientation
        self.side = side
        self.number = number

    def __repr__(self):
        if self.side == FRONT:
            side = 'front'
        else:
            side = 'back'
        if self.orientation == RIGHTSIDEUP:
            orient = 'rightside-up'
        else:
            orient = 'upside-down'
        return "<%s: block %s | page %s | %s side | %s>" % (
            self.__class__.__name__, self.number, self.paper.number, side, orient)

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



def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()

