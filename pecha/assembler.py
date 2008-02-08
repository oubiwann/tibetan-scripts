#!/usr/bin/env python2.4
from pyPdf import PdfFileWriter, PdfFileReader
from pyPdf.generic import NumberObject

inch = 72.0
pechaHeight = 8.5 * inch / 2
pechaShortWidth = 11 * inch
pechaLongWidth = 14 * inch

def cropPDFPage(page, startX=0, startY=pechaHeight, endX=11*inch, endY=8.5*inch):
    for index, amount in enumerate([startX, startY, endX, endY]):
        page.mediaBox[index] = NumberObject(amount)
    return page

inFile = 'test/sources/1perpage_test.pdf'
text = PdfFileReader(file(inFile, "rb"))
output = PdfFileWriter()
count = text.getNumPages()
for index in xrange(count):
    page = cropPDFPage(text.getPage(index))
    output.addPage(page)

outName = 'crop.pdf'
cropped = file(outName, "wb")
output.write(cropped)
cropped.close()
