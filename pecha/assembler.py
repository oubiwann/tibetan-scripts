#!/usr/bin/env python2.4
import os
from tempfile import mkstemp

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import legal, landscape
from reportlab.lib.units import cm, mm, inch, pica

from pyPdf import PdfFileWriter, PdfFileReader

pechaShort = (8.5*inch/2, 11*inch)
pechaLong = (8.5*inch/2, 14*inch)

# http://www.reportlab.com/docs/userguide.pdf
# Create the crop mark page
#
ign, tmpFile = mkstemp('.pdf', 'pecha_blank', '/tmp')
cropMarks = Canvas(tmpFile, pagesize=landscape(pechaShort))
cropMarks.showPage()
cropMarks.save()

# http://pybrary.net/pyPdf/
# test merging the pecha with the crop marks
#
text = PdfFileReader(file(inFile, "rb"))
crop = PdfFileReader(file(tmpFile, "rb")).getPage(0)
output = PdfFileWriter()
count = text.getNumPages()
for index in xrange(count):
    if opts.pageLimit and count > opts.pageLimit:
        break
    page = text.getPage(index)
    page.mergePage(crop)
    output.addPage(page)

outName = '%s_%s.pdf' % (origBase, opts.postfix)
marked = file(outName, "wb")
output.write(marked)
marked.close()

os.unlink(tmpFile)
