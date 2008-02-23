# -*- coding: utf-8 -*-

import re

def toUpper(string):
    """
    >>> data = ''' Sang gyè
    ...  chag dü
    ...  chö kyi'''
    >>> print toUpper(data)
     SANG GYÈ
     CHAG DÜ
     CHÖ KYI
    """
    # è toÈ 
    string = string.replace('\xc3\xa8', '\xc3\x88')
    # ü to Ü
    string = string.replace('\xc3\xbc', '\xc3\x9c')
    # ö toÖ
    string = string.replace('\xc3\xb6', '\xc3\x96')
    return string.upper()


def normalizeVerseBreak(string):
    """
    >>> data = '  CHANG CHUB SEM CHOG RIN PO CHE'
    >>> normalizeVerseBreak(data)
    'CHANG CHUB SEM CHOG RIN PO CHE'
    >>> data = 'CHANG CHUB SEM CHOG RIN PO CHE /'
    >>> normalizeVerseBreak(data)
    'CHANG CHUB SEM CHOG RIN PO CHE    '
    >>> data = 'CHANG CHUB SEM CHOG RIN PO CHE/ MA KYE PA NAM KYE GUYR CHIG'
    >>> normalizeVerseBreak(data)
    'CHANG CHUB SEM CHOG RIN PO CHE    MA KYE PA NAM KYE GUYR CHIG'
    """
    string = string.strip()
    string = string.replace('/', ' / ')
    string = re.sub('\s+', ' ', string)
    string = string.replace('/', '  ')
    return string

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
