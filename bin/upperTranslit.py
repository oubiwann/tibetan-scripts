#!/usr/bin/env python
"""
Convert a lower-case transliterated file to an upper-case transliterated file.

Usage:
    python %prog <unicode input file> [<output file>]

where the unicode file contains lower-case Tibetan transliteration text.
"""
import sys
from optparse import OptionParser
from subprocess import Popen, PIPE


def main():
    parser = OptionParser(usage=__doc__)
    parser.set_defaults(debug=False)
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug",
        help="")
    (options, args) = parser.parse_args()
    filename = args[0]
    outputFilename = None
    if len(args) > 1:
        outputFilename = args[1]
    command = [
        "perl",
        "third-party/Lingua-BO-Wylie-dev/bin/pronounce.pl",
        "-j", "' '",
        filename,
        "-",
        ]
    output = Popen(command, stdout=PIPE).communicate()[0]
    lines = output.decode("utf-8").upper().split("\n")
    badlines = []
    data = ""
    for lineNumber, line in enumerate(lines):
        lineNumber += 1
        if len(line) > 0:
            line = "%s /  " % line
        if options.debug:
            line = "%s  %s" % (str(lineNumber).rjust(6, " "), line)
            if "?" in line:
                badlines.append(line)
        if outputFilename and not options.debug:
            data += line + "\n"
        else:
            print line
        if data:
            fh = open(outputFilename, "w+")
            fh.write(data.encode("utf-8"))
            fh.close()
    if options.debug and badlines:
        print "\nThe following lines have ambiguous words (marked"
        print "by question marks):\n"
        for line in badlines:
            print line
        print "\n"

if __name__ == "__main__":
    main()
