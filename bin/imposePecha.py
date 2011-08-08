#!/usr/bin/env python
"""
Given a Tibetan pecha PDF file, with all the pages in order, create a new PDF
such that:
 * when printed and cut, the correct leaves will be front and back to each
   other
 * the number of pecha pages printed per-page is configurable
 * the paper size is configurable

Usage:
    %prof [option] source_file dest_file
"""
from pecha import scripts


usage = __doc__
script = scripts.ImposePecha(usage)
script.run()
