import os.path
from optparse import OptionParser
from subprocess import Popen, PIPE
import sys

from pyPdf import PdfFileWriter, PdfFileReader

from pecha import const
from pecha.assembler import addCropMarks, assembleBooklet, cropPDFFile


class AddCropMarks(object):
    """
    """
    def __init__(self, usage):
        parser = OptionParser(usage=usage)
        parser.set_defaults(
            shade=0.75, suffix='marked', flip=False,
            pageLimit=None, drawTopCrop=False, drawBottomCrop=False,
            style='default', paperSize='legal')
        parser.add_option('-s', '--shade', dest='shade')
        parser.add_option('-p', '--paperSize', dest='paperSize')
        parser.add_option('-u', '--suffix', dest='suffix')
        parser.add_option('-f', '--flip', dest='flip')
        parser.add_option('-n', '--pageLimit', dest='pageLimit')
        parser.add_option('-t', '--drawTopCrop', dest='drawTopCrop')
        parser.add_option('-b', '--drawBottomCrop', dest='drawBottomCrop')
        parser.add_option('-y', '--style', dest='style')
        (self.opts, args) = parser.parse_args()
        if not args:
            parser.error('You must pass the filename of the pdf to mark.')

        # setup filenames
        self.inFile = args[0]
        origBase = os.path.splitext(self.inFile)[0]
        self.outFile = '%s_%s.pdf' % (origBase, self.opts.suffix)

    def run(self):
        """
        Create the crop marked file
        """
        addCropMarks(self.inFile, self.outFile, self.opts)


class CreateBooklet(object):
    """
    """
    def __init__(self, usage):
        parser = OptionParser(usage=usage)
        parser.set_defaults(suffix='booklet', flip=False, pageLimit=None,
                          paperSize='legal', orientation='landscape')
        parser.add_option('-p', '--paperSize', dest='paperSize')
        parser.add_option('-o', '--orientation', dest='orientation')
        parser.add_option('-u', '--suffix', dest='suffix')
        parser.add_option('-f', '--flip', dest='flip')
        parser.add_option('-n', '--pageLimit', dest='pageLimit')
        (self.opts, args) = parser.parse_args()
        if not args:
            parser.error('You must pass the filename of the pdf to mark.')

        # setup filenames
        self.inFile = args[0]
        origBase = os.path.splitext(self.inFile)[0]
        self.outFile = '%s_%s.pdf' % (origBase, self.opts.suffix)

    def run(self):
        """
        """
        assembleBooklet(self.inFile, self.outFile, self.opts)


class InterLeave(object):
    """
    """
    def __init__(self, usage):
        parser = OptionParser(usage=usage)
        (opts, args) = parser.parse_args()
        if not args or len(args) != 2:
            msg = ('You must pass the filenames for the two documents you are '
                   'merging.\n\tThe first document will become the odd- '
                   'numbered pages the second document will\n\tbecome the '
                   'even-numbered pages.')
            parser.error(msg)
        self.oddFile, self.evenFile = args
        prefix = evenFile.split('_even.pdf')[0]
        self.outName = '%s.pdf' % prefix

    def run(self):
        odds = PdfFileReader(file(self.oddFile, "rb"))
        evens = PdfFileReader(file(self.evenFile, "rb"))
        output = PdfFileWriter()
        largest = [odds.getNumPages(), evens.getNumPages()]
        largest.sort()
        for index in xrange(largest[-1]):
            output.addPage(odds.getPage(index))
            print "Merged page %s (pecha pages %s and %s)." % (
                index*2+1, (index+1)*2-1, (index+1)*2+1)
            try:
                output.addPage(evens.getPage(index))
                print "Merged page %s (pecha pages %s and %s)." % (
                    index*2+2, (index+3)*2-2, (index+3)*2)
            except IndexError:
                # no even page corresponding to the odd page; we're done
                pass
        merged = file(outName, "wb")
        output.write(merged)
        merged.close()


class TrimAsPechaPDF(object):
    """
    """
    def __init__(self, usage):
        parser = OptionParser(usage=usage)
        parser.set_defaults(suffix='trimmed', flip=False, pageLimit=None,
                          paperSize='legal', orientation='landscape',
                          pechaPagesPerPage=2)
        parser.add_option('-p', '--paperSize', dest='paperSize')
        parser.add_option('-o', '--orientation', dest='orientation')
        parser.add_option('-u', '--suffix', dest='suffix')
        parser.add_option('-f', '--flip', dest='flip')
        parser.add_option('-n', '--pageLimit', dest='pageLimit')
        parser.add_option(
            '-g', '--pechaPagesPerPage', dest='pechaPagesPerPage', type="int")
        (self.opts, args) = parser.parse_args()
        if not args:
            parser.error('You must pass the filename of the pdf to crop.')
        # setup filenames
        self.inFile = args[0]
        origBase = os.path.splitext(self.inFile)[0]
        self.outFile = '%s_%s.pdf' % (origBase, self.opts.suffix)

    def run(self):
        """
        Create the crop marked file
        """
        cropPDFFile(self.inFile, self.outFile, self.opts)
        print "\nThe PDF pecha '%s' is ready to be read.\n" % self.outFile


class UpperTransliteration(object):
    """
    """
    def __init__(self, usage, debug=False):
        parser = OptionParser(usage=usage)
        parser.set_defaults(debug=debug)
        parser.add_option(
            "-d", "--debug", action="store_true", dest="debug",
            help="")
        (self.opts, args) = parser.parse_args()
        self.filename = args[0]
        self.outputFilename = None
        if len(args) > 1:
            self.outputFilename = args[1]

    def runPerl(self):
        command = [
            "perl",
            "third-party/Lingua-BO-Wylie-dev/bin/pronounce.pl",
            "-j", "' '",
            self.filename,
            "-",
            ]
        output = Popen(command, stdout=PIPE).communicate()[0]
        return output.decode("utf-8").upper().split("\n")

    def parseResults(self, results):
        badlines = []
        data = ""
        for lineNumber, line in enumerate(reults):
            lineNumber += 1
            if len(line) > 0:
                line = "%s /  " % line
            if self.opts.debug:
                line = "%s  %s" % (str(lineNumber).rjust(6, " "), line)
                if "?" in line:
                    badlines.append(line)
            if self.outputFilename and not self.opts.debug:
                data += line + "\n"
            else:
                print line
            if data:
                fh = open(self.outputFilename, "w+")
                fh.write(data.encode("utf-8"))
                fh.close()
        if self.opts.debug and badlines:
            print "\nThe following lines have ambiguous words (marked"
            print "by question marks):\n"
            for line in badlines:
                print line
            print "\n"

    def run(self):
        results = self.runPerl()
        self.parseResults(results)


class ImposePecha(object):
    """
    """
    def __init__(self, usage):
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
        (self.opts, args) = parser.parse_args()
        self.infile, self.outfile = args
        if not args or len(args) != 2:
            msg = ("You must pass the filenames for the source and "
                   "destination documents.")
            parser.error(msg)

    def run(self):
        def getSrcDim(srcPage):
            return (float(srcPage.mediaBox.getWidth()),
                    float(srcPage.mediaBox.getHeight()))

        def getDestDim():
            if self.opts.orientation == const.PORTRAIT:
                return self.opts.size
            elif self.opts.orientation == const.LANDSCAPE:
                return (self.opts.size[1], self.opts.size[0])

        def getScale(srcPage):
            destWidth, destHeight = getDestDim()
            return (getSrcDim(srcPage)[const.WIDTH]/float(destWidth))


        def getScaledDestDim(srcPage):
            return [x * int(getScale(srcPage)) for x in getDestDim()]


        reader = PdfFileReader(file(self.infile, "rb"))
        writer = PdfFileWriter(
            documentInfo=reader.getDocumentInfo(), authors=["Vimala"])

        #self.opts.count

        srcPage = reader.getPage(0)
        height = getSrcDim(srcPage)[const.HEIGHT]
        totalHeight = self.opts.count * height

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
        writer.write(open(self.outfile, "wb"))
