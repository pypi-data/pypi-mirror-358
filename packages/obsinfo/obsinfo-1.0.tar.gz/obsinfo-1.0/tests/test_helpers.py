#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test helper classes
"""
import warnings
from pathlib import Path
import unittest

import yaml
from obspy.core.util.obspy_types import (FloatWithUncertaintiesFixedUnit,
                                         FloatWithUncertaintiesAndUnit)

# obsinfo modules
from obsinfo.helpers import (FloatWithUncert, Location, Locations,
                             str_indent, ObsinfoClassList, Comments,
                             Person, Phone, ExternalReferences,
                             Identifiers, OIDate, OIDates)
from obsinfo.obsmetadata import ObsMetadata
from obsinfo.instrumentation import (Datalogger)

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
        self.datalogger_dict =  {
            'equipment': {
                'type': 'A/D Converter',
                'model': "AMG-64b"},
            'sample_rate': 200,
            'stages': [{
                'base': {
                    'input_units': {'name': "V", 'description': "VOLTS"},
                    'output_units': {'name': "counts", 'description': "DIGITAL UNITS"},
                    'gain': {'value': 2000, 'frequency': 10.},
                    'name': "DELTA-SIGMA A-D CONVERTER",
                    'input_sample_rate': 8000,
                    'decimation_factor': 5,
                    'filter': {
                        'type': "FIR",
                        'symmetry': 'NONE',
                        'coefficients': [1, 2, 3, 4, 3, 2, 1],
                        'coefficient_divisor': 16,
                        'delay.samples': 3
                    }
                }
            }]
        }


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

    def test_float_with_uncert(self):
        """Test FloatWithUncert object"""
        root = self._read_yaml_root('float_with_uncert.yaml')
        obj = FloatWithUncert.from_dict(root)
        print(obj)
        self.assertEqual(obj.value, 10.)
        self.assertEqual(obj.uncertainty, 0.1)
        self.assertEqual(obj.measurement_method, 'blind guess')
        self.assertIsInstance(obj.to_obspy(), FloatWithUncertaintiesFixedUnit)

    def test_float_with_uncert_unit(self):
        """Test FloatWithUncert object"""
        root = self._read_yaml_root('float_with_uncert_and_unit.yaml')
        obj = FloatWithUncert.from_dict(root)
        print(obj)
        self.assertEqual(obj.value, 10.)
        self.assertEqual(obj.unit, 'degrees')
        self.assertEqual(obj.uncertainty, 0.1)
        self.assertEqual(obj.measurement_method, 'blind guess')
        self.assertIsInstance(obj.to_obspy(), FloatWithUncertaintiesAndUnit)

    def test_Location(self):
        """Test reading a Location object"""
        root = self._read_yaml_root('location.yaml')
        obj = Location(root, '01')
        print(obj)
        print(obj.__repr__())
        self.assertEqual(obj.geology, "rocky")
        self.assertEqual(obj.code, "01")
        self.assertEqual(obj._uncert_m['lat'], 10)
        self.assertEqual(obj._measurement_method, "Deployed using a short-baseline transponder")

    def test_Locations(self):
        """Test creating a Locations object"""
        root = self._read_yaml_root('location.yaml')
        obj = Locations([Location(root, '01'), Location(root, '02')])
        print(obj)
        print(obj.__repr__())
        self.assertEqual(obj[0].geology, "rocky")
        self.assertEqual(obj[0].code, "01")
        self.assertEqual(obj[1].code, "02")
        self.assertIsInstance(obj.get_by_loc_code('01'), Location)
        self.assertIsNone(obj.get_by_loc_code('03'))

    def test_phone_str_convert(self):
        """Tests reading and writing a phone string"""
        obj = Phone("001 (415) 123-4567")
        # print(obj)
        self.assertEqual(obj.country_code, "1")
        self.assertEqual(obj.area_code, 415)
        self.assertEqual(obj.phone_number, "1234567")
        self.assertEqual(str(obj), "Phone: +1 4151234567")

        obj = Phone("+1 (415) 123-4567")
        # print(obj)
        self.assertEqual(obj.country_code, "1")
        self.assertEqual(obj.area_code, 415)
        self.assertEqual(obj.phone_number, "1234567")
        self.assertEqual(str(obj), "Phone: +1 4151234567")

        obj = Phone("+33 6 12345678")
        # print(obj)
        self.assertEqual(obj.country_code, "33")
        self.assertEqual(obj.area_code, 0)
        self.assertEqual(obj.phone_number, "612345678")
        self.assertEqual(str(obj), "Phone: +33 612345678")

    def test_read_phone_object(self):
        """Tests reading a phone object"""
        root = self._read_yaml_root('phone.yaml','definitions', ['phone'])
        obj = Phone(root)
        obspy_obj = obj.to_obspy()
        # print(obj)
        self.assertEqual(obj.country_code, "33")
        self.assertEqual(obj.area_code, 0)
        self.assertEqual(obj.phone_number, "612345678")
        self.assertEqual(str(obj), 'Phone: +33 612345678')

    def test_read_phone_string(self):
        """Test reading a phone string"""
        obj = Phone("+33 6 12345678")
        obspy_obj = obj.to_obspy()
        # print(obj)
        self.assertEqual(obj.country_code, "33")
        self.assertEqual(obj.area_code, 0)
        self.assertEqual(obj.phone_number, "612345678")
        obj = Phone("001 (415) 123-4567")
        obspy_obj = obj.to_obspy()
        # print(obj)
        self.assertEqual(obj.country_code, "1")
        self.assertEqual(obj.area_code, 415)
        self.assertEqual(obj.phone_number, "1234567")
        self.assertEqual(str(obj), "Phone: +1 4151234567")

    def test_read_person(self):
        """Test reading a Person object"""
        root = self._read_yaml_root('person.yaml','person',
                                    ['definitions', 'person'])
        obj = Person(root)
        obspy_obj = obj.to_obspy()
        # print(obj)
        self.assertEqual(obj.names[0], "Tyra Banks")

    def test_comments(self):
        """Test Comments objects"""
        root = self._read_yaml_root('comments.yaml','definitions', ['comments'])
        obj = Comments(root)
        print(obj)
        print(obj[0])
        print(obj[1])
        self.assertEqual(obj[0].value, "First comment")
        self.assertEqual(obj[1].value, "Second comment")
        self.assertIsNone(obj[0].begin_effective_time.to_obspy())
        self.assertEqual(obj[1].begin_effective_time.__str__(), "2021-01-01T00:00:00")
        self.assertEqual(str(obj[0]), "Comment:\n    value: First comment")
        self.assertEqual(str(obj[1]), "Comment:\n"
                                      "    value: Second comment\n"
                                      '    authors: Persons: [Person ["The Boss"]]\n'
                                      "    begin_effective_time: 2021-01-01T00:00:00\n"
                                      "    end_effective_time: 2022-01-01T01:01:01")

    def test_comments_from_extras(self):
        """Test Comments.from_extras()"""
        obj = Comments.from_extras({'a': {'b': 1, 'c': 'Hi'}, 'b': "Hello"})
        print(obj)
        self.assertEqual(obj[0].value, 'Extra attributes: {"a": {"b": 1, "c": "Hi"}, "b": "Hello"}')
        self.assertIsNone(obj[0].begin_effective_time.to_obspy())

    def test_external_references(self):
        """Test ExternalReferences objects"""
        root = self._read_yaml_root('external_references.yaml','definitions', ['external_references'])
        obj = ExternalReferences(root)
        print(obj)
        print(obj[0])
        print(obj[1])
        obj.to_obspy()
        self.assertEqual(obj[0].uri, "blah:1010/2020/3030")
        self.assertEqual(obj[1].uri, "https://www.happy.clam/1010/2020/3030")

    def test_identifiers(self):
        """Test ExternalReferences objects"""
        inputs = ['GFZ:102020.456.789','IPGP:homonuque.paluque.dom']
        obj = Identifiers(inputs)
        print(obj)
        self.assertEqual(obj.to_obspy(), inputs)
        with self.assertRaises(ValueError):
            temp = Identifiers(['10.1024.567'])
        self.assertEqual(obj[0].uri, 'GFZ:102020.456.789')
        self.assertEqual(obj[1].uri, 'IPGP:homonuque.paluque.dom')

    def test_oi_date(self):
        """Test OIDate objects"""
        input = '2007-01-04'
        obj = OIDate(input)
        self.assertEqual(obj.to_obspy(), input)
        obj = OIDate('2007-12-01T00:12:00') 
        self.assertEqual(obj.to_obspy(), '2007-12-01T00:12:00')
        # Test bad input (non-date)
        with self.assertLogs('obsinfo', 'ERROR'):
            obj = OIDate('hello')
        with self.assertLogs('obsinfo', 'ERROR'):
            obj = OIDate('2007-13-01')
        with self.assertLogs('obsinfo', 'ERROR'):
            obj = OIDate('2007-12-01T00:61:00') 

    def test_oi_dates(self):
        """Test OIDate objects"""
        input = ['2007-01-04', '2016-03-06']
        obj = OIDates(input)
        self.assertEqual(obj.to_obspy(), input)
        obj = OIDates([input[0]])
        self.assertEqual(obj.to_obspy(), [input[0]])
        obj += OIDates([input[1]])
        self.assertEqual(obj.to_obspy(), input)
        # Test bad input (non-date)
        with self.assertLogs('obsinfo', 'ERROR'):
            obj = OIDates(['hello', '2007-01-04'])
        with self.assertLogs('obsinfo', 'ERROR'):
            obj = OIDate(['2007-13-01', '2007-12-01'])
# 
    def test_str_indent(self):
        """Test string indentation"""
        a = ("First line\nSecond line\nThird line\n4")
        self.assertEqual(str_indent(a, 2),
                         "First line\n  Second line\n  Third line\n  4")
        self.assertEqual(str_indent(a, -2),
                         "  First line\n  Second line\n  Third line\n  4")

    def test_object_str(self):
        """
        Test object_str
        
        (returns string of an object + n_subclasses-1 subclasses)
        """
        obj = Datalogger({'base': self.datalogger_dict})
        print(obj)
        print(obj.__str__(n_subclasses=1))
        print(obj.__str__(n_subclasses=2))
        print(obj.__str__(n_subclasses=3))
        self.assertEqual(str(obj),
                         'Datalogger:\n'
                         '    sample_rate: 200\n'
                         '    correction: 0\n'
                         "    equipment: <class 'obsinfo.instrumentation.equipment.Equipment'>\n"
                         '    stages: Stages: [Stage "DELTA-SIGMA A-D CONVERTER"]')
        self.assertEqual(obj.__str__(n_subclasses=1),
                         'Datalogger:\n'
                         '    sample_rate: 200\n'
                         '    correction: 0\n'
                         "    equipment: Equipment:\n"
                         "        type: A/D Converter\n"
                         "        description: None\n"
                         "        model: AMG-64b\n"
                         '    stages: Stages: [Stage "DELTA-SIGMA A-D CONVERTER"]')

    def test_obsinfo_class_list(self):
        """
        Test ObsinfoClassList template
        
        (returns string of an object + n_subclasses-1 subclasses)
        """
        dobj = Datalogger({'base': self.datalogger_dict})
        obj = ObsinfoClassList([dobj for x in (1,2,3)], Datalogger)
        print(obj)
        self.assertEqual(str(obj),
                         "ObsinfoClassList:\n"
                         "    - <class 'obsinfo.instrumentation.instrument_component.Datalogger'>\n"
                         "    - <class 'obsinfo.instrumentation.instrument_component.Datalogger'>\n"
                         "    - <class 'obsinfo.instrumentation.instrument_component.Datalogger'>")
        print(obj.__str__(n_subclasses=2))
        self.assertEqual(obj.__str__(n_subclasses=2),
                         'ObsinfoClassList:\n'
                         '    - Datalogger:\n'
                         '          sample_rate: 200\n'
                         '          correction: 0\n'
                         "          equipment: Equipment:\n"
                         "              type: A/D Converter\n"
                         "              description: None\n"
                         "              model: AMG-64b\n"
                         '          stages: Stages: [Stage "DELTA-SIGMA A-D CONVERTER"]\n'
                         '    - Datalogger:\n'
                         '          sample_rate: 200\n'
                         '          correction: 0\n'
                         "          equipment: Equipment:\n"
                         "              type: A/D Converter\n"
                         "              description: None\n"
                         "              model: AMG-64b\n"
                         '          stages: Stages: [Stage "DELTA-SIGMA A-D CONVERTER"]\n'
                         '    - Datalogger:\n'
                         '          sample_rate: 200\n'
                         '          correction: 0\n'
                         "          equipment: Equipment:\n"
                         "              type: A/D Converter\n"
                         "              description: None\n"
                         "              model: AMG-64b\n"
                         '          stages: Stages: [Stage "DELTA-SIGMA A-D CONVERTER"]')

def suite():
    return unittest.makeSuite(HelperClassesTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

