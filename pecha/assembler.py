from copy import copy
from StringIO import StringIO

from pyPdf import PdfFileWriter, PdfFileReader
from pyPdf.generic import NumberObject

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import pagesizes
from reportlab.lib.pagesizes import legal, landscape

from pecha import const
from pecha.layouts import booklet


inch = 72.0
pechaHeight = 8.5 * inch / 2
pechaShortWidth = 11 * inch
pechaLongWidth = 14 * inch


def _invertBoxParams(params):
    """
    """
    return [params[1], params[0], params[3], params[2]]


def placeBlock(page, location):
    """
    """
    # XXX this isn't working yet
    if location == const.TOP:
        x1, y1, x2, y2 = (0, 0, 11 * inch, 8.5 * inch)
        page = cropPDFPage(page, x1, y1, x2, y2)
    else:
        x1, y1, x2, y2 = (0, pechaHeight, 11 * inch, pechaHeight + 8.5 * inch)
        for index, amount in enumerate([x1, y1, x2, y2]):
            page.artBox[index] = NumberObject(amount)
    return page


def cropPDFPage(page, startX=0, startY=pechaHeight, endX=14*inch,
                endY=8.5*inch):
    """
    """
    contents = page.get("/Contents").getObject()
    contents.getData()
    print page.getAllText()
    # Check for landscape orientation
    if int(page.get("/Rotate")) in [90, 270]:
        #import pdb;pdb.set_trace()
        page.mediaBox.upperLeft = ((startY, startX))
        page.mediaBox.lowerRight = ((endY, endX))
        page.trimBox.upperLeft = ((startY, startX))
        page.trimBox.lowerRight = ((endY, endX))
        page.cropBox.upperLeft = ((startY, startX))
        page.cropBox.lowerRight = ((endY, endX))
        page.bleedBox.upperLeft = ((startY, startX))
        page.bleedBox.lowerRight = ((endY, endX))
    # Otherwise, it's portrait
    else:
        page.mediaBox.upperLeft = ((startX, startY))
        page.mediaBox.lowerRight = ((endX, endY))
        page.trimBox.upperLeft = ((startX, startY))
        page.trimBox.lowerRight = ((endX, endY))
        page.cropBox.upperLeft = ((startX, startY))
        page.cropBox.lowerRight = ((endX, endY))
        page.bleedBox.upperLeft = ((startX, startY))
        page.bleedBox.lowerRight = ((endX, endY))
    return page


def createMarkedPDF(filenameOrFH, opts):
    """
    """
    # setup lengths
    length = opts.paperSize[1] / inch
    if opts.style == 'default':
        boxParamsMid = [0, 4, length, 0.5]
    if opts.style == 'trim':
        opts.drawTopCrop = True
        opts.drawBottomCrop = True
        boxParamsTop = [0, 0, length, 0.2]
        boxParamsMid = [0, 3.85, length, 0.8]
        boxParamsBot = [0, 8.3, length, 0.2]
    # with PDF files that have been converted from PS files via the command
    # line tool pstopdf, we've found that we need to invert the crop box
    # dimensions
    if opts.flip:
        boxParamsMid = _invertBoxParams(boxParamsMid)
        if opts.drawTopCrop:
            boxParamsTop = _invertBoxParams(boxParamsTop)
        if opts.drawBottomCrop:
            boxParamsBot = _invertBoxParams(boxParamsBot)
    # now create the PDF page
    canvas = Canvas(filenameOrFH, pagesize=landscape(opts.paperSize))
    canvas.setStrokeColorRGB(*opts.shade)
    canvas.setFillColorRGB(*opts.shade)
    canvas.rect(*[inch*x for x in boxParamsMid], **{'fill': 1})
    if opts.drawTopCrop:
        canvas.rect(*[inch*x for x in boxParamsTop], **{'fill': 1})
    if opts.drawBottomCrop:
        canvas.rect(*[inch*x for x in boxParamsBot], **{'fill': 1})
    canvas.showPage()
    canvas.save()
    return (filenameOrFH, canvas)


def createBlankPDF(filenameOrFH, opts):
    """
    """
    orientation = getattr(pagesizes, opts.orientation)
    canvas = Canvas(filenameOrFH, pagesize=orientation(opts.paperSize))
    canvas.showPage()
    canvas.save()
    return (filenameOrFH, canvas)


def _prepFiles(inFilename, outFilename):
    """
    """
    reader = PdfFileReader(file(inFilename, "rb"))
    writer = PdfFileWriter()
    stream = open(outFilename, "wb")
    return (reader, writer, stream)


def addCropMarks(inFilename, outFilename, opts):
    """
    """
    # setup color and sizes
    opts.shade = [float(opts.shade)] * 3
    opts.paperSize = getattr(pagesizes, opts.paperSize)
    fileObj, canvas = createMarkedPDF(StringIO(), opts)
    markPage = PdfFileReader(fileObj).getPage(0)
    reader, writer, marked = _prepFiles(inFilename, outFilename)
    for index in xrange(reader.getNumPages()):
        page = reader.getPage(index)
        page.mergePage(markPage)
        writer.addPage(page)
    writer.write(marked)
    marked.close()
    fileObj.close()


def _doublePages(reader):
    writer = PdfFileWriter()
    for index in xrange(reader.getNumPages()):
        page = reader.getPage(index)
        writer.addPage(page)
        # If we don't copy, then the later operations will execute against
        # both, leaving us with all even or all odd pecha pages, depending on
        # which is worked on first (or last?).
        writer.addPage(copy(page))
    return writer


def _cropOddPechaPage(reader, index, opts):
    """
    The following does the top of the pecha page (odd pecha pages)
    """
    params = (
        reader.getPage(index), 
        0, 0,
        float(opts.paperSize[1]), float(opts.paperSize[0])/2)
    return cropPDFPage(*params)


def _cropEvenPechaPage(reader, index, opts):
    """
    The following does the bottom of the pecha page (even pecha pages)
    """
    params = (
        reader.getPage(index), 
        0, pechaHeight,
        float(opts.paperSize[1]), float(opts.paperSize[0]))
    return cropPDFPage(*params)


def _crop2PerPage(reader, writer, opts):
    """
    Double the pages, since one page has two pecha pages on it, and we'll
    need to crop it twice to get all the pecha pages (crop to the top to get
    the odd pecha pages and again, crop to the bottom to get the even pecha
    pages).

    Note that this will work for PDF readers that render a page respecting the
    media box, etc. There are some readers that don't, so you could get some
    strange-looking, duplicate pages with those readers.
    """
    reader = _doublePages(reader)
    for index in xrange(reader.getNumPages()):
        if index % 2 == 0:
            page = _cropOddPechaPage(reader, index, opts)
        else:
            page = _cropEvenPechaPage(reader, index, opts)
        writer.insertPage(page, index)
    return writer


def _crop1PerPage(reader, writer, opts):
    for index in xrange(reader.getNumPages()):
        page = _cropOddPechaPage(reader, index, opts)
        writer.addPage(page)
    return writer


def cropPDFFile(inFilename, outFilename, opts=None):
    """
    """
    opts.paperSize = getattr(pagesizes, opts.paperSize)
    reader, writer, stream = _prepFiles(inFilename, outFilename)
    if opts.pechaPagesPerPage == 2:
        writer = _crop2PerPage(reader, writer, opts)
    elif opts.pechaPagesPerPage == 1:
        writer = _crop1PerPage(reader, writer, opts)
    writer.write(stream)
    stream.close()


def cropAndRotateFile(inFilename, outFilename, opts=None):
    """
    """
    reader, writer, stream = _prepFiles(inFilename, outFilename)
    pf = booklet.pechaFactory(reader.getNumPages())
    for index, block in enumerate(pf.getBlockList()):
        page = cropPDFPage(reader.getPage(index))
        if block.orientation == const.UPSIDEDOWN:
            page.rotateClockwise(180)
        writer.addPage(page)
    writer.write(stream)
    stream.close()


def assembleBooklet(inFilename, outFilename, opts):
    """
    """
    opts.paperSize = getattr(pagesizes, opts.paperSize)
    blank, canvas = createBlankPDF(StringIO(), opts)
    reader, writer, stream = _prepFiles(inFilename, outFilename)
    pf = booklet.pechaFactory(reader.getNumPages())
    for sheet in pf.sheets:
        page = side = None
        for block in sheet.blocks:
            if side != block.side:
                if page != None:
                    # finish up the old page
                    writer.addPage(page)
                # make new PDF page
                page = PdfFileReader(blank).getPage(0)
            side = block.side
            blockPDF = reader.getPage(block.number - 1)
            # crop the page to pecha size
            params = (
                reader.getPage(index), 0, pechaHeight,
                float(opts.paperSize[1]), float(opts.paperSize[0]))
            blockPDF = cropPDFPage(*params)
            # rotate if need be
            if block.orientation == UPSIDEDOWN:
                blockPDF.rotateClockwise(180)
            # figure out where on the page to put it
            blockPDF = placeBlock(blockPDF, block.location)
            page.mergePage(blockPDF)
    writer.write(stream)
    stream.close()
    blank.close()
