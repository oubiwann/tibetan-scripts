#!/usr/bin/env python
"""
Given a pecha PDF file with odd-numnbered pages and another one with
even-numbdered pages, interleave them in a manner approrpiate for prnting and
cutting.

Usage:
    %prog [options] oddPagedFile evenPagedFile
"""
from pecha import scripts


usage = __doc__
script = scripts.InterLeave(usage)
script.run()
