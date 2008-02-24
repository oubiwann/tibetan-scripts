import unittest
import doctest

# to add a new module to the test runner, simply include is in the list below:
modules = [
    'pecha.base',
    'pecha.layouts.booklet',
    'pecha.rtf',
    'pecha.util',
]

suite = unittest.TestSuite()
for modname in modules:
    mod = __import__(modname)
    components = modname.split('.')
    if len(components) == 1:
        suite.addTest(doctest.DocTestSuite(mod))
    else:
        for comp in components[1:]:
            mod = getattr(mod, comp)
            suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner()
runner.run(suite)

