#!/usr/bin/env python
import os.path
from optparse import OptionParser

from pecha.assembler import addCropMarks

usage = '''%prog [options] infile'''
optp = OptionParser(usage=usage)
optp.set_defaults(shade=0.75, suffix='marked', flip=False, pageLimit=None,
                  drawTopCrop=False, drawBottomCrop=False, style='default',
                  paperSize='legal')
optp.add_option('-s', '--shade', dest='shade')
optp.add_option('-p', '--paperSize', dest='paperSize')
optp.add_option('-u', '--suffix', dest='suffix')
optp.add_option('-f', '--flip', dest='flip')
optp.add_option('-n', '--pageLimit', dest='pageLimit')
optp.add_option('-t', '--drawTopCrop', dest='drawTopCrop')
optp.add_option('-b', '--drawBottomCrop', dest='drawBottomCrop')
optp.add_option('-y', '--style', dest='style')
(opts, args) = optp.parse_args()
if not args:
    optp.error('You must pass the filename of the pdf to mark.')

# setup filenames
inFile = args[0]
origBase = os.path.splitext(inFile)[0]
outFile = '%s_%s.pdf' % (origBase, opts.suffix)
# Create the crop marked file
addCropMarks(inFile, outFile, opts)

