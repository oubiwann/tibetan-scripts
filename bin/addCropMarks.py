#!/usr/bin/env python
"""
Add crop marks to a PDF file.

Usage:
    %prog [options] infile
"""
from pecha import scripts


usage = __doc__
script = scripts.AddCropMarks(usage)
script.run()
