#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test instrumnetation, stages and filter classes
"""
import warnings
from pathlib import Path
import unittest

import yaml

# obsinfo modules
from obsinfo.instrumentation import (Orientation, Equipment,
                                     Stage, Stages, InstrumentComponent,
                                     Datalogger, Sensor, Preamplifier,
                                     Instrument, Channel, Instrumentation)
from obsinfo.obsmetadata import ObsMetadata
from obsinfo.helpers import (Locations, OIDate)

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
        self.testing_path = Path(__file__).parent.joinpath("data_instrumentation")
        loc_base = {'uncertainties.m': {'lat': 2, 'lon': 2, 'elev': 5},
                    'depth.m': 0,
                    'geology': 'seafloor',
                    'vault': 'floor of sea'}
        self.test_locations = Locations.from_locations_dict({
            "00": {'base': loc_base,
                   'position': {'lat.deg': 45, 'lon.deg': 10, 'elev.m': 200}},
            "01": {'base': loc_base,
                   'position': {'lat.deg': 45.1, 'lon.deg': 10.1, 'elev.m': 201}}
            })

    def _read_yaml_root(self, filename, schema_file=None, schema_path=None):
        with open(str(self.testing_path / filename), 'r') as f:
            root = yaml.safe_load(f)
        # get rid of yaml anchor section, if any
        if 'temporary' in root:
            del root['temporary']
        if schema_file is not None:
            print(schema_file)
            self._test_against_schema(root, schema_file, schema_path)
        return root

    def _test_against_schema(self, root, schema_file, sublevels,
                             check_schema=False):
        """
        Test an infodict against a schema

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

    def test_Orientation(self):
        """Test reading an Orientation object"""
        root = self._read_yaml_root('orientation.yaml', 'instrumentation_base',
                                    ['definitions', 'orientation'])
        obj = Orientation(root)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.azimuth.value, 90)
        self.assertEqual(obj.azimuth.uncertainty, 2)
        self.assertEqual(obj.azimuth.measurement_method, "gyrocompass")
        self.assertEqual(obj.dip.value, 0)
        self.assertEqual(obj.dip.measurement_method, "bubble level")

    def test_Equipment(self):
        """Test reading an Equipment object"""
        root = self._read_yaml_root('equipment.yaml', 'definitions',
                                    ['equipment'])
        obj = Equipment(root)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.resource_id, "gfz:01920.992.288")
        self.assertEqual(obj.serial_number, '01')

    def test_stage(self):
        """Test reading a Stage object"""
        root = self._read_yaml_root('stage.yaml', 'stage_base',
                                    ['definitions', 'stage'])
        obj = Stage(root)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.input_units, "m/s")
        self.assertEqual(obj.input_sample_rate, 500.)
        self.assertEqual(obj.output_sample_rate, 100.)
        self.assertEqual(obj.configuration, "differential")
        self.assertEqual(obj.gain, 20.)
        self.assertEqual(obj.gain_frequency, 10.)
        self.assertEqual(obj.delay, 0.2)
        self.assertEqual(obj.name, 'MS_METER [config: differential]')
        # Add stage_modifications
        resp_mods = {'1': {"gain": {'value': 3000}},
                     '2': {"configuration": 'single-sided',
                           "gain": {'value': 5000}}}
        obj = Stage(root,
                    {'stage_modifications': resp_mods},
                    sequence_number=1)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.gain, 3000.)
        obj = Stage(root,
                    {'stage_modifications': resp_mods},
                    sequence_number=2)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.gain, 5000.)
        self.assertEqual(obj.gain_frequency, 1.)
        self.assertEqual(obj.name, 'MS_METER [config: single-sided]')
        obj = Stage(root,
                    {'stage_modifications': resp_mods,
                     'configuration': 'flowers!'},
                    sequence_number=2)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.gain, 5000.)
        self.assertEqual(obj.gain_frequency, 1.)
        # remove stage-level configuration, make sure base-level is used
        root.pop('configuration')
        obj = Stage(root)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.gain, 10.)
        # # Test changing values at stage level
        root['configuration'] = "single-sided"
        root['modifications']['delay'] = 1.1
        obj = Stage(root)
        self.assertEqual(obj.configuration, "single-sided")
        self.assertEqual(obj.gain, 10.)
        self.assertEqual(obj.gain_frequency, 1.)
        self.assertEqual(obj.delay, 1.1)
        # Test adding a global response_modification
        obj = Stage(root, {'stage_modifications': {'*': {'delay': 5.0}}})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.delay, 5.0)
        # Test adding a non-specific modification
        obj = Stage(root, {'modifications': {'delay': 5.0}})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.delay, 5.0)
        # Test adding both, should take the specific value
        obj = Stage(root, {'stage_modifications': {'*': {'delay': 15.0}},
                           'modifications': {'delay': 25.0}})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.delay, 15.0)
        # Test adding a an external configuration
        obj = Stage(root, {'configuration': 'flowers!'})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.gain, 12345.0)
        # # Test adding a non-existant external configuration_name
        with self.assertRaises(ValueError):
            Stage(root, {'configuration': 'bacon!'})

    def test_stages(self):
        """Test reading a Stages object"""
        root = self._read_yaml_root('stages.yaml', 'stages',
                                    ['definitions', 'stages'])
        obj = Stages(root)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.input_units, "m/s")
        self.assertEqual(obj.output_units, "counts")
        self.assertEqual(obj[2].output_sample_rate, 100.)
        # Test changing values using stage-level config
        obj = Stages(root,
                     {'stage_modifications': {
                        '1': {'configuration': 'differential'},
                        '2': {"gain": {"value": 12345.}},
                        '3': {"decimation_factor": 4}}})
        print(obj)  # Only prints if something fails
        for stage in obj:
            print(stage)
        self.assertEqual(obj[0].gain, 20.)
        self.assertEqual(obj[1].gain, 12345.)
        self.assertEqual(obj[2].output_sample_rate, 125.)

    def test_instrument_component(self):
        """Test reading an Instrument_Component object"""
        root = self._read_yaml_root('instrument_component_base.yaml')
        obj = InstrumentComponent({'base': root})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.equipment.type, "A/D Converter")
        self.assertEqual(obj.equipment.model, "AMG-64b")
        self.assertIsNone(obj.configuration,)
        self.assertIsNone(obj.configuration_description)
        self.assertEqual(obj.stages[0].gain, 2000.)
        self.assertEqual(obj.base_dict, {})

    def test_datalogger(self):
        """Test reading a Datalogger object"""
        root = self._read_yaml_root('datalogger_base.yaml', 'datalogger_base',
                                    ['definitions', 'base'])
        obj = Datalogger({'base': root})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.sample_rate, 200.)
        self.assertEqual(obj.configuration, "200sps")
        self.assertEqual(obj.correction, 0.2)
        obj = Datalogger({'base': root,
                          'configuration': '400sps'})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.sample_rate, 400.)
        obj = Datalogger({'base': root,
                          'configuration': '400sps',
                          'modifications': {'sample_rate': 12345.}})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.sample_rate, 12345.)

    def test_sensor(self):
        """Test reading a Sensor object"""
        root = self._read_yaml_root('sensor_base.yaml', 'sensor_base',
                                    ['definitions', 'base'])
        obj = Sensor({'base': root})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.configuration, "single-sided")
        self.assertEqual(obj.stages[0].gain, 375.)
        self.assertEqual(obj.stages[0].gain_frequency, 1.)
        self.assertEqual(obj.seed_band_base, 'broadband')
        self.assertEqual(obj.seed_instrument_code, 'H')
        self.assertEqual(obj.equipment.description,
                         "Magical seismometer [config: single-sided]")
        obj = Sensor({'base': root, 'configuration': 'differential'})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.stages[0].gain, 750)
        self.assertEqual(obj.stages[0].gain_frequency, 2.)
        self.assertEqual(obj.equipment.description,
                         "Magical seismometer [config: differential]")

    def test_preamplifier(self):
        """Test reading a Preamplifier object"""
        root = self._read_yaml_root('preamplifier_base.yaml',
                                    'preamplifier_base',
                                    ['definitions', 'base'])
        obj = Preamplifier({'base': root})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.configuration, "128x gain")
        self.assertEqual(obj.stages[0].gain, 128.)
        self.assertEqual(obj.stages[0].gain_frequency, 10.)
        self.assertEqual(obj.equipment.description,
                         "Multiplicative preamplifier [config: 128x gain]")
        obj = Preamplifier({'base': root, 'configuration': '32x gain'})
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.stages[0].gain, 32.)
        self.assertEqual(obj.stages[0].gain_frequency, 10.)

    def test_instrument(self):
        """
        Test reading an Instrument object

        There is no instrument level in the information files, an instrument is
        the combination of the datalogger, preamplifier and sensor parts
        of a channel definition
        """
        root = self._read_yaml_root('instrument.yaml', 'instrumentation_base',
                                    ['definitions', 'channel'])
        obj = Instrument(root)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.sample_rate, 200.)
        self.assertEqual(obj.delay, 0.125)
        self.assertEqual(obj.stages[-1].correction, 0.025)
        self.assertEqual(obj.seed_band_base, 'broadband')
        self.assertEqual(obj.seed_band_code, 'H')
        self.assertEqual(obj.seed_instrument_code, 'H')

    def test_channel(self):
        """Test reading a Channel object"""
        root = self._read_yaml_root('channel_default.yaml',
                                    'instrumentation_base',
                                    ['definitions','channel_default'])
        root['start_date'] = '2008-01-01'
        root['end_date'] = '2008-07-04'
        equipment = Equipment({'name': 'MyEquip', 'model': 'XTCp5'})
        obj = Channel(root, {}, location=self.test_locations[0],
                      equipment=equipment)
        print(obj)  # Only prints if something fails
        self.assertEqual(obj.instrument.sample_rate, 400)
        self.assertEqual(obj.instrument.delay, 0)
        self.assertEqual(obj.instrument.stages[-1].correction, 0)
        self.assertEqual(obj.instrument.seed_band_base, 'broadband')
        self.assertEqual(obj.instrument.seed_band_code, 'C')
        self.assertEqual(obj.instrument.seed_instrument_code, 'H')
        # Channel-specific fields
        self.assertEqual(obj.equipment.model, 'XTCp5')
        self.assertEqual(obj.location.code, '00')
        self.assertEqual(obj.location.latitude.value, 45)
        self.assertEqual(obj.start_date, OIDate('2008-01-01'))
        self.assertEqual(obj.end_date, OIDate('2008-07-04'))
        self.assertEqual(obj.comments[0].value, 'comment 1')
        self.assertEqual(obj.comments[1].value, 'comment 2')
        self.assertEqual(obj.orientation.code, 'Z')
        self.assertEqual(obj.orientation.azimuth.value, 0)
        self.assertEqual(obj.orientation.dip.value, -90)

    def test_select_channel_modifs(self):
        """Test Instrumentation._select_channel_modifs"""
        channel_modifs = {'Z':    {'A': 42},
                          'Z-01': {'A': 43},
                          '*':    {'A': 44},
                          'Y':    {'A': 45},
                          '*-01': {'A': 46}}
        sm = Instrumentation._select_channel_modifs
        print(sm({'orientation': {'code': 'Z'}, 'location_code': '00'},
                            channel_modifs))
        self.assertEqual(sm({'orientation': {'code': 'Z'},
                             'location_code': '00'},
                            channel_modifs)[0]['A'],
                         42)
        self.assertEqual(sm({'orientation': {'code': 'Z'},
                             'location_code': '01'},
                            channel_modifs)[0]['A'],
                         43)
        self.assertEqual(sm({'orientation': {'code': 'E'},
                             'location_code': '00'},
                            channel_modifs)[0]['A'],
                         44)
        self.assertEqual(sm({'orientation': {'code': 'Y'},
                             'location_code': '00'},
                            channel_modifs)[0]['A'],
                         45)
        self.assertEqual(sm({'orientation': {'code': 'E'},
                             'location_code': '01'},
                            channel_modifs)[0]['A'],
                         46)

    def test_instrumentation(self):
        """Test reading an Instrumentation object"""
        root = self._read_yaml_root('instrumentation_base.yaml',
                                    'instrumentation_base',
                                    ['definitions', 'base'])
        obj = Instrumentation({'base': root},
                              locations=self.test_locations,
                              station_location_code='00',
                              station_start_date='2016-07-01',
                              station_end_date='2017-06-02')
        print(obj)
        self.assertEqual(obj.equipment.model, 'IPGPno1')
        self.assertEqual(len(obj.channels), 4)


def suite():
    return unittest.makeSuite(InstrumentationTest, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
