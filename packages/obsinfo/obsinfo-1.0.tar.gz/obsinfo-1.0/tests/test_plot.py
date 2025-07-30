#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test helper classes
"""
import warnings
from pathlib import Path
import unittest

# obsinfo modules
from obsinfo.console_scripts.plot import _get_map_extent_from_lons_lats

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False


class HelperClassesTest(unittest.TestCase):
    """
    Test elements in the helpers/ directory

    Attributes:
        testing_path (str): path to datafiles to be tested aside from the
            examples
    """

    def setUp(self):
        """
        Set up default values and paths
        """
        self.maxDiff=None
        self.testing_path = Path(__file__).parent.joinpath("data_helpers")


    def test_get_map_extent(self):
        """Test _get_map_extent() function"""
        for a, b in zip(_get_map_extent_from_lons_lats([12],[45], 1),
                        (11.993637, 12.006363, 44.995500, 45.004500)):
            self.assertAlmostEqual(a, b, places=5)
        for a, b in zip(_get_map_extent_from_lons_lats([12],[45], 10),
                        [11.936365, 12.063635, 44.955004, 45.044996]):
            self.assertAlmostEqual(a, b, places=5)
        for a, b in zip(_get_map_extent_from_lons_lats([12, 12.1, 12.2],[45, 46, 45], 1),
                        [11.96, 12.24, 44.8, 46.2]):
            self.assertAlmostEqual(a, b, places=5)
        for a, b in zip(_get_map_extent_from_lons_lats([12, 12.0001, 12.0002],[45, 45.001, 45], 1),
                        [11.993737, 12.006463, 44.996000, 45.005000]):
            self.assertAlmostEqual(a, b, places=5)


def suite():
    return unittest.makeSuite(HelperClassesTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

