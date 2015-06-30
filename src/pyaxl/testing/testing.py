import doctest
import unittest


optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS + doctest.IGNORE_EXCEPTION_DETAIL


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite('../../README.rst',
                             package='pyaxl',
                             )
    ])
    return suite
