#!/usr/bin/env python2.4
import os
from tempfile import mkstemp
from optparse import OptionParser

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import legal, landscape
from reportlab.lib.units import cm, mm, inch, pica

from pyPdf import PdfFileWriter, PdfFileReader

def invertBoxParams(params):
    return [params[1], params[0], params[3], params[2]]

usage = '''%prog [options] infile'''
optp = OptionParser(usage=usage)
optp.set_defaults(shade=0.75, postfix='marked', flip=False, pageLimit=None,
                  drawTopCrop=False, drawBottomCrop=False, style='default')
optp.add_option('-s', '--shade', dest='shade')
optp.add_option('-p', '--postfix', dest='postfix')
optp.add_option('-f', '--flip', dest='flip')
optp.add_option('-n', '--pageLimit', dest='pageLimit')
optp.add_option('-t', '--drawTopCrop', dest='drawTopCrop')
optp.add_option('-b', '--drawBottomCrop', dest='drawBottomCrop')
optp.add_option('-y', '--style', dest='style')
(opts, args) = optp.parse_args()
if not args:
    optp.error('You must pass the filename of the pdf to mark.')
inFile = args[0]
origBase = os.path.splitext(inFile)[0]
color = [float(opts.shade)] * 3
ign, tmpFile = mkstemp('.pdf', 'pecha_crop_marker_', '/tmp')

#cropMark1 = {
#    'horiz': [0.25, 4.25, 0.5, 4.25],
#    'vert': [0.5, 4.0, 0.5, 4.25]}
#cropMark1 = [0, 4., 14, 4.]
#cropMark2 = [0, 4.5, 14, 4.5]
if opts.style == 'default':
    boxParamsMid = [0, 4, 14, 0.5]
if opts.style == 'trim':
    opts.drawTopCrop = True
    opts.drawBottomCrop = True
    boxParamsTop = [0, 0, 14, 0.2]
    boxParamsMid = [0, 3.85, 14, 0.8]
    boxParamsBot = [0, 8.3, 14, 0.2]
# with PDF files that have been converted from PS files via the command line
# tool pstopdf, we've found that we need to invert the crop box dimensions
if opts.flip:
    boxParamsMid = invertBoxParams(boxParamsMid)
    if opts.drawTopCrop:
        boxParamsTop = invertBoxParams(boxParamsTop)
    if opts.drawBottomCrop:
        boxParamsBot = invertBoxParams(boxParamsBot)

# http://www.reportlab.org/rsrc/userguide.pdf
# Create the crop mark page
#
cropMarks = Canvas(tmpFile, pagesize=landscape(legal))
cropMarks.setStrokeColorRGB(*color)
#cropMarks.line(*[inch*x for x in cropMark1])
#cropMarks.line(*[inch*x for x in cropMark2])
cropMarks.setFillColorRGB(*color)
cropMarks.rect(*[inch*x for x in boxParamsMid], **{'fill': 1})
if opts.drawTopCrop:
    cropMarks.rect(*[inch*x for x in boxParamsTop], **{'fill': 1})
if opts.drawBottomCrop:
    cropMarks.rect(*[inch*x for x in boxParamsBot], **{'fill': 1})
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
