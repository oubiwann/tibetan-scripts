#!/usr/bin/env python
"""
%prog [options] oddPagedFile evenPagedFile
"""
from pecha import scripts


usage = __doc__
script = scripts.InterLeave(usage)
script.run()
