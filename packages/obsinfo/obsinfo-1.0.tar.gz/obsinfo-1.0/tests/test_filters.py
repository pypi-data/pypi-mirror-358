#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test instrumnetation, stages and filter classes
"""
import warnings
from pathlib import Path
import unittest

import yaml
import obspy.core.inventory.response as op_resp
import obspy.core.inventory.util as op_util

# obsinfo modules
from obsinfo.instrumentation import (Filter, Coefficients, FIR, PolesZeros,
                                     ResponseList, Polynomial, ADConversion,
                                     Analog, Digital)
from obsinfo.obsmetadata import ObsMetadata

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False


class FilterTest(unittest.TestCase):
    """
    Test elements in the filter/ directory

    Attributes:
        testing_path (str): path to datafiles to be tested aside from the
            examples
    """

    def setUp(self):
        """
        Set up default values and paths
        """
        self.testing_path = Path(__file__).parent.joinpath("data_filters")

    def read_yaml_root(self, filename):
        with open(str(self.testing_path / filename), 'r') as f:
            return yaml.safe_load(f)

    def _test_against_schema(self, root, schema_file, sublevels):
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
        self.assertTrue(ObsMetadata()._report_errors(root, schema),
                        f'file does not match schema {schema_name}')

    def test_poles_zeros(self):
        """Test reading and converting a PolesZeros object"""
        root = self.read_yaml_root('poles_zeros.yaml')
        self._test_against_schema(root,'filter',['definitions','POLESZEROS'])
        obj = Filter.construct(root, 0, 'test')
        print(obj)  # Only prints if something fails
        self.assertIsInstance(obj, PolesZeros)
        self.assertEqual(obj.delay_seconds, 0.001)
        self.assertEqual(len(obj.poles), 7)

    def test_FIR(self):
        """Test reading and converting a FIR object"""
        root = self.read_yaml_root('FIR.yaml')
        self._test_against_schema(root,'filter',['definitions','FIR'])
        obj = Filter.construct(root, 0, 'test')
        print(obj)  # Only prints if something fails
        self.assertIsInstance(obj, FIR)
        self.assertEqual(obj.delay_samples, 5.)
        self.assertEqual(len(obj.coefficients), 11)

    def test_Coefficients(self):
        """Test reading and converting a Coefficients object"""
        root = self.read_yaml_root('coefficients.yaml')
        self._test_against_schema(root,'filter',['definitions','COEFFICIENTS'])
        obj = Filter.construct(root, 0, 'test')
        print(obj)  # Only prints if something fails
        self.assertIsInstance(obj, Coefficients)
        self.assertEqual(obj.delay_samples, 5.)
        self.assertEqual(len(obj.numerator_coefficients), 11)
        self.assertEqual(len(obj.denominator_coefficients), 11)

    def test_ResponseList(self):
        """Test reading and converting a ResponseList object"""
        root = self.read_yaml_root('response_list.yaml')
        self._test_against_schema(root,'filter',['definitions','RESPONSELIST'])
        obj = Filter.construct(root, 0, 'test')
        print(obj)  # Only prints if something fails
        self.assertIsInstance(obj, ResponseList)
        self.assertEqual(obj.delay_seconds, 0.15)
        self.assertEqual(len(obj.elements), 6)

    def test_Polynomial(self):
        """Test reading and converting a Polynomial object"""
        root = self.read_yaml_root('polynomial.yaml')
        self._test_against_schema(root,'filter',['definitions','POLYNOMIAL'])
        obj = Filter.construct(root, 0, 'test')
        print(obj)  # Only prints if something fails
        self.assertIsInstance(obj, Polynomial)
        self.assertEqual(len(obj.coefficients), 11)
        obj = Polynomial(root)
        print(obj)  # Only prints if something fails
        self.assertIsInstance(obj, Polynomial)
        self.assertEqual(len(obj.coefficients), 11)

    def test_ADConversion_signed(self):
        """Test low-level signed two's complement calculations'"""
        self.assertEqual(ADConversion.s16(eval('0xFFFF')), -1)
        self.assertEqual(ADConversion.s16(eval('0x8000')), -2**15)
        self.assertEqual(ADConversion.s16(eval('0x7FFF')), 2**15 - 1)
        self.assertEqual(ADConversion.s24(eval('0xFFFFFF')), -1)
        self.assertEqual(ADConversion.s24(eval('0x800000')), -2**23)
        self.assertEqual(ADConversion.s24(eval('0x7FFFFF')), 2**23 - 1)
        self.assertEqual(ADConversion.s32(eval('0xFFFFFFFF')), -1)
        self.assertEqual(ADConversion.s32(eval('0x80000000')), -2**31)
        self.assertEqual(ADConversion.s32(eval('0x7FFFFFFF')), 2**31 - 1)
        self.assertEqual(ADConversion.s32(eval('0x17c7cc6e')), 398969966)
        self.assertEqual(ADConversion.s32(eval('0xc158a854')), -1051154348)

    def test_ADConversion_calc_counts(self):
        """Test low-level ADConversion count-calculating function"""
        m, p = ADConversion._calc_counts('0x0000', '0xFFFF', 'uint16')
        self.assertEqual(m, 0)
        self.assertEqual(p, 2**16-1)
        m, p = ADConversion._calc_counts(0, '0xFFFFFF', 'uint24')
        self.assertEqual(m, 0)
        self.assertEqual(p, 2**24-1)
        m, p = ADConversion._calc_counts(0, '0xFFFFFFFF', 'uint32')
        self.assertEqual(m, 0)
        self.assertEqual(p, 2**32-1)
        m, p = ADConversion._calc_counts(5, 10, 'uint24')
        self.assertEqual(m, 5)
        self.assertEqual(p, 10)
        m, p = ADConversion._calc_counts('5', '10', 'uint24')
        self.assertEqual(m, 5)
        self.assertEqual(p, 10)
        m, p = ADConversion._calc_counts('0x8000', '0x7FFF', 'int16')
        self.assertEqual(m, -2**15)
        self.assertEqual(p, 2**15 - 1)
        m, p = ADConversion._calc_counts('0x800000', '0x7FFFFF', 'int24')
        self.assertEqual(m, -2**23)
        self.assertEqual(p, 2**23 - 1)
        m, p = ADConversion._calc_counts('0x80000000', '0x7FFFFFFF', 'int32')
        self.assertEqual(m, -2**31)
        self.assertEqual(p, 2**31 - 1)

        # Bad inputs
        # Unknown dtype
        with self.assertRaises(TypeError):
            m, p = ADConversion._calc_counts(0, '0xFFFF', 'uint44')
        # Malformed hexadecimal
            m, p = ADConversion._calc_counts(0, '9xFFFF', 'uint32')
        # count_plus out of range
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(0, '0xFFFFFF', 'uint16')
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(0, '0xFFFFFFFF', 'uint24')
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(0, '0xFFFFFFFFF', 'uint32')
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(0, '0xFFFFFFF', 'int16')
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(0, '0xFFFFFFFFF', 'int24')
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(0, '0xFFFFFFFFFF', 'int32')
        # hexadecimal has too few digits
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(0, '0xFFFF', 'int32')
        # count_minus >= count_plus
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(10, -10, 'uint32')
        with self.assertRaises(ValueError):
            m, p = ADConversion._calc_counts(10, 10, 'uint32')

    def test_ADConversion(self):
        """Test reading and converting an ADConversion object"""
        # Test reading a valid file
        root = self.read_yaml_root('AD_conversion.yaml')
        self._test_against_schema(root,'filter',['definitions','ADCONVERSION'])
        obj = Filter.construct(root, 0, 'test')
        self.assertIsInstance(obj, ADConversion)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.delay_samples, None)
        self.assertEqual(obj.v_minus, -4.5)
        self.assertEqual(obj.v_plus, 4.5)
        self.assertEqual(obj.counts_plus, ADConversion.s24(0x4FFFFF))
        self.assertEqual(obj.counts_minus, ADConversion.s24(0xB00000))
        self.assertEqual(obj.gain, 1165084 + 1./3)
        self.assertEqual(len(obj.numerator_coefficients), 1)
        self.assertEqual(obj.numerator_coefficients[0], 1.)
        self.assertEqual(len(obj.denominator_coefficients), 0)
        # Test reading an invalid file (counts_plus too big for the declared dtype)
        with self.assertRaises(ValueError):
            root = self.read_yaml_root('AD_conversion_bad.yaml')
            obj = Filter.construct(root, 0, 'test')

    def test_Analog(self):
        """Test reading and converting an Analog object"""
        root = self.read_yaml_root('analog.yaml')
        self._test_against_schema(root,'filter',['definitions','ANALOG'])
        obj = Filter.construct(root, 0, 'test')
        print(obj)  # Only prints if something fails
        self.assertIsInstance(obj, Analog)
        self.assertEqual(obj.delay_seconds, 0.)

    def test_Digital(self):
        """Test reading and converting an Digital object"""
        root = self.read_yaml_root('digital.yaml')
        self._test_against_schema(root,'filter',['definitions','DIGITAL'])
        obj = Filter.construct(root, 0, 'test')
        print(obj)  # Only prints if something fails
        self.assertIsInstance(obj, Digital)
        self.assertEqual(obj.delay_samples, 0.)
        self.assertEqual(len(obj.numerator_coefficients), 1)
        self.assertEqual(obj.numerator_coefficients[0], 1.)
        self.assertEqual(len(obj.denominator_coefficients), 0)


def suite():
    return unittest.makeSuite(FilterTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

