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


RIGHTSIDEUP = 0
UPSIDEDOWN = 1
FRONT = 0
BACK = 1

class Pecha(object):
    """
    A object representing a complete pecha document.

    pages: number of pecha blocks (pecha pages) in the document

    # check page counts
    >>> for x in xrange(1,8+1):
    ...   p = Pecha(pages=x)
    ...   p.pageCount, p.physicalPageCount

    """

    def __init__(self, pages):
        self.pageCount = pages

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

class PhysicalPage(object):
    """
    An object representing a two-sided, pysical piece of paper.

    number: page number
    blocks: number of pecha pages per physical sheet of paper (front and back)
    """
    def __init__(self, number=1, blocks=4):
        self.number = number

class PechaPage(object):
    """
    An object representing a block of text, classically presented on a side of
    paper with borders and text within those borders.

    orientation: whether the pecha text block is rightside-up on the paper or
        upside-down
    side: the front or back of the physcial paper
    number: the pecha block number

    >>> pp = PechaPage(RIGHTSIDEUP, FRONT)
    >>> pp.orientation == RIGHTSIDEUP
    """
    def __init__(self, orientation=RIGHTSIDEUP, side=FRONT, number=1):
        self.orientation = orientation
        self.number = number

    def setOrientation(self, const):
        pass

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()

