#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test StationXML creation
"""
from pathlib import Path
import glob
import unittest
import inspect
# from pprint import pprint
import warnings

from obsinfo.obsmetadata import ObsMetadata

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False

     
class obsmetadataTest(unittest.TestCase):
    """
    Test methods for obsmetadata 
    """
    def setUp(self):
        self.testing_path = Path(__file__).parent / "data"
        self.infofiles_path = (Path(__file__).resolve().parents[2]
                               / "_examples" / 'instrumentation_files')

    def test_valid_types(self):
        """
        Test is_valid_type.
        """
        for filetype in ("datalogger_base", "filter",
                         "instrumentation_base", "location_base",
                         "network", "operator", "person",
                         "preamplifier_base", "sensor_base", "stage_base",
                         "subnetwork", "timing_base"):
            self.assertTrue(ObsMetadata.is_valid_type(filetype),
                            msg=f'filetype "{filetype}" is not valid')
        # A couple of old types
        for filetype in ("station"):
            self.assertFalse(ObsMetadata.is_valid_type(filetype),
                            msg=f'filetype "{filetype}" is not valid')
        for filetype in ("wabbit", "bollweevil", "cawwot", "ACME"):
            self.assertFalse(ObsMetadata.is_valid_type(filetype))

    def test_safe_update(self):
        # test using pure ObsMetadata input
        a = ObsMetadata(a='j', b=ObsMetadata(c=5, d=6))
        a.safe_update({'b': {'d': 2, 'e': 3}})
        self.assertEqual(a, {'a': 'j', 'b': {'c': 5, 'd': 2, 'e': 3}})
        
        # test using "impure" ObsMetadata input
        a = ObsMetadata(a='j', b=dict(c=5, d=6))
        a.safe_update({'b': {'d': 2, 'e': 3}})
        self.assertEqual(a, {'a': 'j', 'b': {'c': 5, 'd': 2, 'e': 3}})

        # test using another "impure" ObsMetadata input
        a = ObsMetadata(a='j', b={'c': 5, 'd': 6})
        a.safe_update({'b': {'d': 2, 'e': 3}})
        self.assertEqual(a, {'a': 'j', 'b': {'c': 5, 'd': 2, 'e': 3}})

        # test updating a dict to a float (by default, does so and warns)
        a = ObsMetadata(a='j', b={'c': 5, 'd': 6})
        with self.assertLogs('obsinfo','WARNING'):
            a.safe_update({'b': 5})
        self.assertEqual(a, {'a': 'j', 'b': 5})

        # test updating a dict to a float with allow_overwrite=False (doesn't change, and warns)
        a = ObsMetadata(a='j', b={'c': 5, 'd': 6})
        with self.assertLogs('obsinfo','WARNING'):
            # with self.assertWarns(UserWarning):
            a.safe_update({'b': 5}, allow_overwrite=False)
        self.assertEqual(a, {'a': 'j', 'b': {'c': 5, 'd': 6}})

        # test forcing warning on changed value
        a = ObsMetadata(a='j', b={'bc': 5, 'bd': 6})
        with self.assertLogs('obsinfo','WARNING') as cm:
            # with self.assertWarnsRegex(UserWarning, 'replacing self\["bd"\]\: was 6, now 2'):
            a.safe_update({'b': {'bd': 2, 'be': 3}}, warn_crush=True)
        self.assertEqual(cm.output, ['WARNING:obsinfo:replacing self["bd"]: was 6, now 2'])
        self.assertEqual(a, {'a': 'j', 'b': {'bc': 5, 'bd': 2, 'be': 3}})

        # try updating with a different type of sub-element
        a = ObsMetadata(a='j', b=ObsMetadata(c=5, d=6))
        a.safe_update({'a': 5, 'c': [1, 3]})
        self.assertEqual(a, {'a': 5, 'b': {'c': 5, 'd': 6}, 'c': [1, 3]})

    def test_get_configured_modified_base(self):
        base_a = {'a': 'a', 'b': 'a', 'c': 'a',
                  'configurations': {'E': {'c': 'e'},
                                     'F': {'c': 'f'},
                                     'G': {'c': 'g'}
                                    }
                 }
        base_b = {'a': 'b', 'b': 'b', 'c': 'b',
                  'configurations': {'H': {'b': 'e'},
                                     'I': {'b': 'f'},
                                     'J': {'b': 'g'}
                                    }
                 }
        print('a')
        # Test basic base-configuration
        a = ObsMetadata(base=base_a, configuration='E')
        base_dict = a.get_configured_modified_base()
        self.assertEqual(base_dict['c'], 'e')
        self.assertEqual(base_dict['configuration'], 'E')
        
        # Test bad configuration name
        a = ObsMetadata(base=base_a, configuration='H')
        with self.assertRaisesRegex(
            ValueError,
            r"Requested configuration \('H'\) doesn't match "
            r"specified configurations: \['E', 'F', 'G'\]"):
                base_dict = a.get_configured_modified_base()
        
        # Test extra key in dict
        a = ObsMetadata(base=base_a, configuration='E', blah=1)
        with self.assertRaisesRegex(
            ValueError,
            "base-configuration-modification dict has leftover keys: \{'blah': 1\}"):
                base_dict = a.get_configured_modified_base()
        
        # Test modifications overwriting configuration
        a = ObsMetadata(base=base_a,
                        configuration='E',
                        modifications={'c': 'Wakka!'})
        base_dict = a.get_configured_modified_base()
        self.assertEqual(base_dict['c'], 'Wakka!')
        self.assertEqual(base_dict['configuration'], 'E')
        
        # Test higher-level base overwriting everything below
        a = ObsMetadata(base=base_a,
                        configuration='E',
                        modifications={'c': 'Wakka!'})
        base_dict = a.get_configured_modified_base(dict(base=base_b))
        self.assertEqual(base_dict['c'], 'b')
        self.assertNotIn('configuration', base_dict)
        
        # Higher-level configuration overwrites lower-level configuration
        a = ObsMetadata(base=base_a,
                        configuration='E')
        base_dict = a.get_configured_modified_base(dict(configuration='F'))
        self.assertEqual(base_dict['c'], 'f')
        self.assertEqual(base_dict['configuration'], 'F')
        
        # Higher-level configuration overwries lower-level configuration but not modification
        a = ObsMetadata(base=base_a,
                        configuration='E',
                        modifications={'c': 'Wakka!'})
        base_dict = a.get_configured_modified_base(dict(configuration='F'))
        self.assertEqual(base_dict['c'], 'Wakka!')
        self.assertEqual(base_dict['configuration'], 'F')

        # Higher-level modification overwries lower-level modification
        a = ObsMetadata(base=base_a,
                        configuration='E',
                        modifications={'c': 'Wakka!'})
        base_dict = a.get_configured_modified_base(dict(modifications={'c': 'Peace!'}))
        self.assertEqual(base_dict['c'], 'Peace!')
        self.assertEqual(base_dict['configuration'], 'E')
        

def suite():
    return unittest.makeSuite(obsmetadataTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

