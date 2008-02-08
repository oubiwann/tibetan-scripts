#!/usr/bin/env python2.4
from pyPdf import PdfFileWriter, PdfFileReader
from pyPdf.generic import NumberObject

from pecha.base import UPSIDEDOWN
from pecha.layouts.booklet import pechaFactory

inch = 72.0
pechaHeight = 8.5 * inch / 2
pechaShortWidth = 11 * inch
pechaLongWidth = 14 * inch

def cropPDFPage(page, startX=0, startY=pechaHeight, endX=11*inch, endY=8.5*inch):
    for index, amount in enumerate([startX, startY, endX, endY]):
        page.mediaBox[index] = NumberObject(amount)
    return page

def _prepFiles(inFilename, outFilename):
    """
    """
    source = PdfFileReader(file(inFilename, "rb"))
    outPDF = PdfFileWriter()
    outStream = file(outFilename, "wb")
    return (source, outPDF, outStream)

def cropPDFFile(inFilename, outFilename):
    """
    """
    text, output, cropped = _prepFiles(inFilename, outFilename)
    for index in xrange(text.getNumPages()):
        page = cropPDFPage(text.getPage(index))
        output.addPage(page)
    output.write(cropped)
    cropped.close()

def cropAndRotateFile(inFilename, outFilename):
    text, output, cropped = _prepFiles(inFilename, outFilename)
    pf = pechaFactory(text.getNumPages())
    for index, block in enumerate(pf.getBlockList()):
        page = cropPDFPage(text.getPage(index))
        if block.orientation == UPSIDEDOWN:
            page.rotateClockwise(180)
        output.addPage(page)
    output.write(cropped)
    cropped.close()

inFile = 'test/sources/1perpage_test.pdf'
outFile = 'cropped.pdf'
cropAndRotateFile(inFile, outFile)
