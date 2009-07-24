"""
Convert a lower-case transliterated file to an upper-case transliterated file.

Usage:
    python %s <unicode file>

where the unicode file contains lower-case Tibetan transliteration text.
"""
import sys


def main(filename):
    fh = open(filename)
    data = fh.read()
    fh.close()
    print data.decode("utf-8").upper()


if __name__ == "__main__":
    script = sys.argv[0]
    try:
        filename = sys.argv[1]
    except IndexError:
        print __doc__ % script
    else:
        main(filename)
