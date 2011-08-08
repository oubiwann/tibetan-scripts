#!/usr/bin/env python
"""
Given a Tibetan pecha PDF file, with all the pages in order, create a new PDF
such that:
 * when printed and cut, the correct leaves will be front and back to each
   other
 * the number of pecha pages printed per-page is configurable
 * the paper size is configurable
"""
from optparse import OptionParser

from pyPdf import PdfFileWriter, PdfFileReader

from pecha import const


usage = "%%prog [options] source_file dest_file\n%s" %  __doc__.rstrip()
parser = OptionParser(usage=usage)
parser.add_option(
    "-c", "--count", dest="count", default=3,
    help="pecha pages per side of the printed sheet")
parser.add_option(
    "-s", "--sheet-size", dest="size", default=const.LEGAL,
    help="width of the printed sheet")
parser.add_option(
    "-o", "--orientation", dest="orientation", default=const.LANDSCAPE,
    help="orientation of the printed sheet (LANDSCAPE or PORTRAIT)")
(opts, args) = parser.parse_args()
if not args or len(args) != 2:
    msg = ("You must pass the filenames for the source and destination "
           "documents.")
    parser.error(msg)


def getSrcDim(srcPage):
    return (float(srcPage.mediaBox.getWidth()),
            float(srcPage.mediaBox.getHeight()))


def getDestDim():
    if opts.orientation == const.PORTRAIT:
        return opts.size
    elif opts.orientation == const.LANDSCAPE:
        return (opts.size[1], opts.size[0])


def getScale(srcPage):
    destWidth, destHeight = getDestDim()
    return (getSrcDim(srcPage)[const.WIDTH]/float(destWidth))


def getScaledDestDim(srcPage):
    return [x * int(getScale(srcPage)) for x in getDestDim()]


infile, outfile = args
reader = PdfFileReader(file(infile, "rb"))
writer = PdfFileWriter(
    documentInfo=reader.getDocumentInfo(), authors=["Vimala"])

opts.count

srcPage = reader.getPage(0)
height = getSrcDim(srcPage)[const.HEIGHT]
totalHeight = opts.count * height

destPage = writer.addBlankPage(*getScaledDestDim(srcPage))

print totalHeight
fitScale = getScaledDestDim(srcPage)[const.HEIGHT] / float(totalHeight)
print fitScale
srcPage.scale(fitScale, fitScale)
#scale = getScale(srcPage)
#srcPage.scale(scale, scale)

destPage.mergeTranslatedPage(srcPage, 0, height * 2 - .2 * height)

srcPage = reader.getPage(1)
srcPage.scale(fitScale, fitScale)
destPage.mergeTranslatedPage(srcPage, 0, height - .1 * height)

srcPage = reader.getPage(3)
srcPage.scale(fitScale, fitScale)
destPage.mergeTranslatedPage(srcPage, 0, 0)

#import pdb;pdb.set_trace()
writer.write(open(outfile, "wb"))
