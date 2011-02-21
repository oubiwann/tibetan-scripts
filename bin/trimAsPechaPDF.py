#!/usr/bin/env python
import os.path
from optparse import OptionParser

from pecha.assembler import cropPDFFile


usage = '''%prog [options] infile'''
optp = OptionParser(usage=usage)
optp.set_defaults(suffix='trimmed', flip=False, pageLimit=None,
                  paperSize='legal', orientation='landscape',
                  pechaPagesPerPage=2)
optp.add_option('-p', '--paperSize', dest='paperSize')
optp.add_option('-o', '--orientation', dest='orientation')
optp.add_option('-u', '--suffix', dest='suffix')
optp.add_option('-f', '--flip', dest='flip')
optp.add_option('-n', '--pageLimit', dest='pageLimit')
optp.add_option(
    '-g', '--pechaPagesPerPage', dest='pechaPagesPerPage', type="int")
(opts, args) = optp.parse_args()
if not args:
    optp.error('You must pass the filename of the pdf to crop.')

# setup filenames
inFile = args[0]
origBase = os.path.splitext(inFile)[0]
outFile = '%s_%s.pdf' % (origBase, opts.suffix)

# Create the crop marked file
cropPDFFile(inFile, outFile, opts)
print "\nThe PDF pecha '%s' is ready to be read.\n" % outFile
