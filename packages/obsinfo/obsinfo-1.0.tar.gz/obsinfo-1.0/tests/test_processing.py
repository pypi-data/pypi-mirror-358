#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test processing class
"""
import warnings
import unittest
from pprint import pprint
import json

# obsinfo modules
from obsinfo.helpers import (Comments, Comment)
from obsinfo.subnetwork import (Processing)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False


class ProcessingClassesTest(unittest.TestCase):
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
        self.base_v = {'B': 'B', 'C': {'D': 'D', 'E': [0, 1, 2]}}
        self.pl = [
            {'A': self.base_v},
            {'Powow': self.base_v},
            {'Hi': self.base_v, 'Ho': self.base_v}
        ]

    def test_good(self):
        print('self.pl[:2]=')
        pprint(self.pl[:2])
        print(Processing(self.pl[:2]).to_comments())
        print(Comments([Comment(dict(subject='A', value=json.dumps(self.base_v))),
                              Comment(dict(subject='Powow', value=json.dumps(self.base_v)))
                            ]))
        self.assertEqual(Processing(self.pl[:2]).to_comments(),
                    Comments([Comment(dict(subject='A', value=json.dumps(self.base_v))),
                              Comment(dict(subject='Powow', value=json.dumps(self.base_v)))
                            ])
                   )

    def test_bad(self):
        print(f'{self.pl=}')
        pprint(self.pl)
        with self.assertRaises(ValueError):
            Processing(self.pl[-1:])


def suite():
    return unittest.makeSuite(ProcessingClassesTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
