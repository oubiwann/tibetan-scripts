#!/usr/bin/env python
from optparse import OptionParser

from pyPdf import PdfFileWriter, PdfFileReader


usage = '''%prog [options] oddPagedFile evenPagedFile'''
parser = OptionParser(usage=usage)
(opts, args) = parser.parse_args()
if not args or len(args) != 2:
    msg = ('You must pass the filenames for the two documents you are '
           'merging.\n\tThe first document will become the odd-numbered pages '
           'the second document will\n\tbecome the even-numbered pages.')
    parser.error(msg)
oddFile, evenFile = args
prefix = evenFile.split('_even.pdf')[0]
odds = PdfFileReader(file(oddFile, "rb"))
evens = PdfFileReader(file(evenFile, "rb"))
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
outName = '%s.pdf' % prefix
merged = file(outName, "wb")
output.write(merged)
merged.close()
