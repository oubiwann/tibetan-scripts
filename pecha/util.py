def toUpper(string):
    """
    >>> data = ''' Sang gyè
    ...  chag dü
    ...  chö kyi'''
    >>> print toUpper(data)
    """
    return string


def normalizeVerseBreak(string):
    """
    >>> data= '  CHANG CHUB SEM CHOG RIN PO CHE'
    >>> normalizeVerseBreak(data)
    CHANG CHUB SEM CHOG RIN PO CHE
    >>> data= 'CHANG CHUB SEM CHOG RIN PO CHE/ MA KYE PA NAM KYE GUYR CHIG'
    >>> normalizeVerseBreak(data)
    CHANG CHUB SEM CHOG RIN PO CHE   MA KYE PA NAM KYE GUYR CHIG
    """
    return string

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
