#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test all classes with a to_obspy() method
"""
import warnings
from pathlib import Path
import unittest

import yaml
import obspy.core.inventory.response as op_resp
import obspy.core.inventory.util as op_util
from obspy.core.util.obspy_types import (FloatWithUncertaintiesFixedUnit,
                                         FloatWithUncertaintiesAndUnit)

# obsinfo modules
from obsinfo.instrumentation import (Filter, Coefficients, FIR, PolesZeros,
                                     ResponseList, Polynomial, ADConversion,
                                     Analog, Digital, Orientation, Equipment,
                                     Stage, Stages, Datalogger)
from obsinfo.subnetwork import (Station, Stations, Subnetwork,
                                Operator, Operators)
from obsinfo.helpers import (FloatWithUncert, Location, Person, Phone)
from obsinfo.obsmetadata import ObsMetadata

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False


class InstrumentationTest(unittest.TestCase):
    """
    Test elements in the instrumentation/ directory

    Attributes:
        testing_path (str): path to datafiles to be tested aside from the
            examples
    """

    def setUp(self):
        """
        Set up default values and paths
        """
        self.instrumentation_path = Path(__file__).parent.joinpath("data_instrumentation")
        self.helpers_path = Path(__file__).parent.joinpath("data_helpers")
        self.subnetwork_path = Path(__file__).parent.joinpath("data_subnetwork")

    def _read_yaml_root(self, path, filename, schema_file=None, schema_path=None):
        with open(str(path / filename), 'r') as f:
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

    def test_operator(self):
        """Test Operator.to_obspy()"""
        root = self._read_yaml_root(self.subnetwork_path, 'operator.yaml', 'operator',
                                    ['definitions', 'operator'])
        obj = Operator(root)
        self.assertIsInstance(obj.to_obspy(), op_util.Operator)

    def test_person(self):
        """Test Person.to_obspy()"""
        root = self._read_yaml_root(self.helpers_path, 'person.yaml', 'person',
                                    ['definitions', 'person'])
        obj = Person(root)
        self.assertIsInstance(obj.to_obspy(), op_util.Person)

    def test_phone(self):
        """Test Phone.to_obspy()"""
        root = self._read_yaml_root(self.helpers_path, 'phone.yaml', 'definitions',
                                    ['phone'])
        obj = Phone(root)
        self.assertIsInstance(obj.to_obspy(), op_util.PhoneNumber)

    def test_float_with_uncert(self):
        """Test FloatWithUncert.to_obspy()"""
        root = self._read_yaml_root(self.helpers_path, 'float_with_uncert.yaml', 'definitions',
                                    ['float_type'])
        obj = FloatWithUncert.from_dict(root)
        self.assertIsInstance(obj.to_obspy(), FloatWithUncertaintiesFixedUnit)

    def test_float_with_uncert_unit(self):
        """Test FloatWithUncert.to_obspy()"""
        root = self._read_yaml_root(self.helpers_path, 'float_with_uncert_and_unit.yaml',
                                    'definitions',  ['float_type'])
        obj = FloatWithUncert.from_dict(root)
        self.assertIsInstance(obj.to_obspy(), FloatWithUncertaintiesAndUnit)

    def test_obsinfo_class_list(self):
        """Test ObsinfoClassList.to_obspy()"""
        pass

    def test_oi_date(self):
        """Test OIDate.to_obspy()"""
        pass

    def test_Equipment(self):
        """Test Equipment.to_obspy"""
        root = self._read_yaml_root(self.instrumentation_path, 'equipment.yaml',
                                    'definitions',  ['equipment'])
        obj = Equipment(root)
        self.assertIsInstance(obj.to_obspy(), op_util.Equipment)

    def test_stage(self):
        """Test Stage.to_obspy()"""
        root = self._read_yaml_root(self.instrumentation_path, 'stage.yaml',
                                    'stage_base',  ['definitions', 'stage'])
        obj = Stage(root)
        self.assertIsInstance(obj.to_obspy(), op_resp.PolesZerosResponseStage)
        
    def test_stages(self):
        """Test Stages.to_obspy()"""
        pass

    def test_instrument(self):
        """Test Instrument.to_obspy()"""
        pass

    def test_channel(self):
        """Test Channel.to_obspy()"""
        pass

    def test_station(self):
        """Test Station.to_obspy()"""
        pass

    def test_subnetwork(self):
        """Test Subnetwork.to_obspy()"""
        pass


def suite():
    return unittest.makeSuite(SubnetworkTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

