#!/usr/bin/env python2.4
from StringIO import StringIO

from pyPdf import PdfFileWriter, PdfFileReader
from pyPdf.generic import NumberObject

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import pagesizes
from reportlab.lib.pagesizes import legal, landscape

from pecha.base import UPSIDEDOWN, FRONT, TOP
from pecha.layouts import booklet


inch = 72.0
pechaHeight = 8.5 * inch / 2
pechaShortWidth = 11 * inch
pechaLongWidth = 14 * inch


def _prepFiles(inFilename, outFilename):
    """
    """
    source = PdfFileReader(file(inFilename, "rb"))
    outPDF = PdfFileWriter()
    outStream = open(outFilename, "wb")
    return (source, outPDF, outStream)


def _invertBoxParams(params):
    """
    """
    return [params[1], params[0], params[3], params[2]]


def placeBlock(page, location):
    """
    """
    # XXX this isn't working yet
    if location == TOP:
        x1, y1, x2, y2 = (0, 0, 11 * inch, 8.5 * inch)
        page = cropPDFPage(page, x1, y1, x2, y2)
    else:
        x1, y1, x2, y2 = (0, pechaHeight, 11 * inch, pechaHeight + 8.5 * inch)
        for index, amount in enumerate([x1, y1, x2, y2]):
            page.artBox[index] = NumberObject(amount)
    return page


def cropPDFPage(page, startX=0, startY=pechaHeight, endX=14*inch, endY=8.5*inch):
    """
    """
    for index, amount in enumerate([startX, startY, endX, endY]):
        page.mediaBox[index] = NumberObject(amount)
    return page


def createMarkedPDF(filenameOrFH, opts):
    """
    """
    # setup legths
    length = opts.paperSize[1] / inch
    if opts.style == 'default':
        boxParamsMid = [0, 4, length, 0.5]
    if opts.style == 'trim':
        opts.drawTopCrop = True
        opts.drawBottomCrop = True
        boxParamsTop = [0, 0, length, 0.2]
        boxParamsMid = [0, 3.85, length, 0.8]
        boxParamsBot = [0, 8.3, length, 0.2]
    # with PDF files that have been converted from PS files via the command line
    # tool pstopdf, we've found that we need to invert the crop box dimensions
    if opts.flip:
        boxParamsMid = _invertBoxParams(boxParamsMid)
        if opts.drawTopCrop:
            boxParamsTop = _invertBoxParams(boxParamsTop)
        if opts.drawBottomCrop:
            boxParamsBot = _invertBoxParams(boxParamsBot)
    # now create the PDF page
    c = Canvas(filenameOrFH, pagesize=landscape(opts.paperSize))
    c.setStrokeColorRGB(*opts.shade)
    c.setFillColorRGB(*opts.shade)
    c.rect(*[inch*x for x in boxParamsMid], **{'fill': 1})
    if opts.drawTopCrop:
        c.rect(*[inch*x for x in boxParamsTop], **{'fill': 1})
    if opts.drawBottomCrop:
        c.rect(*[inch*x for x in boxParamsBot], **{'fill': 1})
    c.showPage()
    c.save()
    return (filenameOrFH, c)


def createBlankPDF(filenameOrFH, opts):
    """
    """
    orientation = getattr(pagesizes, opts.orientation)
    c = Canvas(filenameOrFH, pagesize=orientation(opts.paperSize))
    c.showPage()
    c.save()
    return (filenameOrFH, c)


def addCropMarks(inFilename, outFilename, opts):
    """
    """
    # setup color and sizes
    opts.shade = [float(opts.shade)] * 3
    opts.paperSize = getattr(pagesizes, opts.paperSize)
    crop, canvas = createMarkedPDF(StringIO(), opts)
    markPage = PdfFileReader(crop).getPage(0)
    source, output, marked = _prepFiles(inFilename, outFilename)
    for index in xrange(source.getNumPages()):
        page = source.getPage(index)
        page.mergePage(markPage)
        output.addPage(page)
    output.write(marked)
    marked.close()
    crop.close()


def cropPDFFile(inFilename, outFilename, opts=None):
    """
    """
    opts.paperSize = getattr(pagesizes, opts.paperSize)
    source, output, cropped = _prepFiles(inFilename, outFilename)
    for index in xrange(source.getNumPages()):
        params = (
            source.getPage(index), 0, pechaHeight,
            float(opts.paperSize[1]), float(opts.paperSize[0]))
        page = cropPDFPage(*params)
        output.addPage(page)
    output.write(cropped)
    cropped.close()


def cropAndRotateFile(inFilename, outFilename, opts=None):
    """
    """
    source, output, cropped = _prepFiles(inFilename, outFilename)
    pf = booklet.pechaFactory(source.getNumPages())
    for index, block in enumerate(pf.getBlockList()):
        page = cropPDFPage(source.getPage(index))
        if block.orientation == UPSIDEDOWN:
            page.rotateClockwise(180)
        output.addPage(page)
    output.write(cropped)
    cropped.close()


def assembleBooklet(inFilename, outFilename, opts):
    """
    """
    opts.paperSize = getattr(pagesizes, opts.paperSize)
    blank, canvas = createBlankPDF(StringIO(), opts)
    source, output, assembled = _prepFiles(inFilename, outFilename)
    pf = booklet.pechaFactory(source.getNumPages())
    for sheet in pf.sheets:
        page = side = None
        for block in sheet.blocks:
            if side != block.side:
                if page != None:
                    # finish up the old page
                    output.addPage(page)
                # make new PDF page
                page = PdfFileReader(blank).getPage(0)
            side = block.side
            blockPDF = source.getPage(block.number - 1)
            # crop the page to pecha size
            params = (
                source.getPage(index), 0, pechaHeight,
                float(opts.paperSize[1]), float(opts.paperSize[0]))
            blockPDF = cropPDFPage(*params)
            # rotate if need be
            if block.orientation == UPSIDEDOWN:
                blockPDF.rotateClockwise(180)
            # figure out where on the page to put it
            blockPDF = placeBlock(blockPDF, block.location)
            page.mergePage(blockPDF)
    output.write(assembled)
    assembled.close()
    blank.close()
