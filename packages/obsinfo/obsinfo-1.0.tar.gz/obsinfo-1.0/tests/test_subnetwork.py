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

    def _test_against_schema(self, root, schema_file, sublevels,
                             check_schema=False):
        """Test an infodict against a schema
        
        Args:
            root (dict or :class:`ObsMetadata`): the infodict
            schema_file (str): the schema filename (w/o '.schema.json')
            sublevels (list): sublevels to traverse to get to proper
                comparison level
        """
        if '.schema.json' not in schema_file:
            schema_file += '.schema.json' 
        schema = ObsMetadata._read_schema_file(schema_file)[0]
        schema_name = schema_file + '#'
        for level in sublevels:
            if level not in schema:
                raise ValueError(f'{schema_name} has no "{level}" sublevel')
            schema = schema[level]
            schema_name += f'{level}/'
        self.assertTrue(ObsMetadata()._report_errors(root, schema,
                        check_schema=check_schema),
                        f'file does not match schema {schema_name}')

    def test_site(self):
        """Test reading a Site object"""
        obj = Site('seafloor')
        obspy_obj = obj.to_obspy()
        print(obj)
        self.assertEqual(obj.name, "seafloor")
        self.assertEqual(str(obj), "Site: seafloor")

    def test_read_operator(self):
        """Test reading an Operator object"""
        root = self._read_yaml_root('operator.yaml','operator',
                                    ['definitions', 'operator'])
        obj = Operator(root)
        obspy_obj = obj.to_obspy()
        # print(obj)
        self.assertEqual(obj.agency, "Screen Actors Guild")
        self.assertEqual(obj.website, "contact@safaftra.org")

    def test_read_stations(self):
        """Test reading a Station object"""
        root = self._read_yaml_root('stations.yaml')
        obj = Stations(root, Operators([{"agency": "CIA"}]), None)
        print(obj)
        print(obj[0].location)
        obspy_obj = obj.to_obspy()
        self.assertEqual(len(obj), 2)
        self.assertEqual(obj[0].code, "STA1")
        self.assertEqual(obj[0].site.name, "bob")
        self.assertEqual(obj[1].code, "STA2")

    def test_read_network(self):
        """Test reading a Network object"""
        root = self._read_yaml_root('network.yaml','network',
                                    ['definitions', 'network'])
        obj = Network(root)
        print(obj.__str__(n_subclasses=1))
        self.assertEqual(obj.code, '4G')

    def test_read_subnetwork(self):
        """Test reading a Subnetwork object"""
        root = self._read_yaml_root('subnetwork.yaml','subnetwork',
                                    ['definitions', 'subnetwork'])
        obj = Subnetwork(root)
        print(obj.__str__(n_subclasses=1))
        obspy_obj = obj.to_obspy()
        self.assertEqual(obj.network.code, '4G')
        self.assertEqual(len(obj.stations), 4)

def suite():
    return unittest.makeSuite(SubnetworkTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

