#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test base_configurations_modifications system
"""
import warnings
from pathlib import Path
import unittest

import yaml

# obsinfo modules
from obsinfo.instrumentation import (Stage)
from obsinfo.obsmetadata import ObsMetadata

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False


class BaseConfigTest(unittest.TestCase):
    """
    Test base-configuration-modifications implementation

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

    def test_stage_get_stage_modifications(self):
        """Test Stage._get_stage_modifications"""
        sm_dict = {'1': {'a': 1},
                   '*': {'a': 2, 'b': 2}}
        self.assertEqual(Stage._get_stage_modifications(sm_dict, 1),
                         {'a': 1, 'b': 2})
        self.assertEqual(Stage._get_stage_modifications(sm_dict, 2),
                         {'a': 2, 'b': 2})

def suite():
    return unittest.makeSuite(BaseConfigTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

