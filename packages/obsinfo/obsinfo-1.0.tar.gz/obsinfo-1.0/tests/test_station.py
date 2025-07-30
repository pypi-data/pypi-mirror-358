#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test network and station classes
"""
import warnings
from pathlib import Path
import unittest
from pprint import pprint

import yaml

# obsinfo modules
from obsinfo.subnetwork import (Station, Stations, Network, Subnetwork, Site,
                                Operator, Operators)
from obsinfo.obsmetadata import ObsMetadata

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False


class SubnetworkTest(unittest.TestCase):
    """
    Test elements in the subnetwork/ directory

    Attributes:
        testing_path (str): path to datafiles to be tested aside from the
            examples
    """

    def setUp(self):
        """
        Set up default values and paths
        """
        self.testing_path = Path(__file__).parent.joinpath("data_subnetwork")

    def _read_yaml_root(self, filename, schema_file=None, schema_path=None):
        with open(str(self.testing_path / filename), 'r') as f:
            root = yaml.safe_load(f)
        # get rid of yaml anchor section, if any
        if 'temporary' in root:
            del root['temporary']
        if schema_file is not None:
            self._test_against_schema(root, schema_file, schema_path)
        return root

    def test_location_code(self):
        """Test reading location code, or creating one"""
        location_dict = {'base': {'uncertainties.m': {'lat': 100, 'lon': 100, 'elev':10},
                                  'depth.m': 0,
                                  'geology': 'unknown',
                                  'vault': 'seafloor'
                                 },
                         'position': {'lat.deg': 0,
                                      'lon.deg': 0,
                                      'elev.m': 0}
                        }
        sd = '2022-07-24T00:00:00'
        ed = '2023-07-24T00:00:00'
        
        # If location_code in locations, should work
        obj = Station('CODE',
                      {'start_date': sd, 'end_date': ed, 'instrumentation': 'TEXT',
                       'location_code': '00',
                       'locations': {'00': location_dict}
                      }
                     )
        self.assertEqual(obj.location_code, '00')
        # If no location_code provided and only one location, should use that location
        obj = Station('CODE',
                      {'start_date': sd, 'end_date': ed, 'instrumentation': 'TEXT',
                       'locations': {'04': location_dict}
                      }
                     )
        self.assertEqual(obj.location_code, '04')
        # If location_code provided but NOT in locations, should raise ValueError
        with self.assertRaises(ValueError):
            obj = Station('CODE',
                          {'start_date': sd, 'end_date': ed, 'instrumentation': 'TEXT',
                           'location_code': '00',
                           'locations': {'01': location_dict}
                          }
                         )
        # If no location_code not provided and there are multiple locations, should raise ValueError
        with self.assertRaises(ValueError):
            obj = Station('CODE',
                          {'start_date': sd, 'end_date': ed, 'instrumentation': 'TEXT',
                           'locations': {'00': location_dict, '01': location_dict}
                          }
                         )

def suite():
    return unittest.makeSuite(SubnetworkTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

