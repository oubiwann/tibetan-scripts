#!/usr/bin/env python
"""
Convert a lower-case transliterated file to an upper-case transliterated file.

Usage:
    %prog <unicode input file> [<output file>]

where the unicode file contains lower-case Tibetan transliteration text.
"""
from pecha import scripts


usage = __doc__
script = scripts.UpperTransliteration(usage)
script.run()
