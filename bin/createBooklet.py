#!/usr/bin/env python
"""
[add description]

Usage:
    %prog [options] infile
"""
from pecha import scripts


usage = __doc__
script = scripts.AddCropMarks(usage)
script.run()
