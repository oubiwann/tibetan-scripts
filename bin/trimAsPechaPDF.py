#!/usr/bin/env python
"""
%prog [options] infile
"""
from pecha import scripts


usage = __doc__
script = scripts.TrimAsPechaPDF(usage)
script.run()
