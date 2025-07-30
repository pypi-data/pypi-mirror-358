#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application to test and print obsinfo information files.

Includes class TestDatapath and entry points.

   # TestObsinfo tests information files content (should only test
     DATAPATH-accessed functions)

 Uses $HOME/.obsinforc to determine the information file base, so if you
 want to test the example files, extract them using obsinfo-setup -d or
 put the path to the example files in $HOME/.obsinforc

 Much the SAME functions and methods are called whether printing or testing,
 as there is little difference between both functionalities. Entry points vary
 for each functionality and the distinction is achieved by naming
 the executable with two different names (i.e. a named link):


    * obsinfo-print has entry point print_obs.

    * obsinfo-test has entry point run_suite_info_files. It is meant to be
      used by developers. In this vein, contrary to obsinfo-validate,
      obsinfo-print calls private methods which are not callable from the
      command line but which can be called from the interpreter.

    * JsonRefTest is meant to be called from the interpreter. It has no entry
      point.


 There are two types of testing functionalities.

    a) If the file name includes "test--attributes" the output of the
       corresponding obsinfo test function will be checked against data
       contained in this class.

    b) If the file name is "normal", it will simply run through to make sure
       there are no errors

 Testing for type (a) uses data from
    obsinfo/tests/data/instrumentation_files/responses/_filters.
 Testing for type (b) uses data from obsinfo/_examples/instrumentation_files

 WARNING: many tests are critically dependent on file hierarchy, including
 names. Do not change names
 in tests or _examples hierarchy, or else change the names here.
 Also, the following methods use four specific file names:

     * test_all_stage_types()
     * test_sensor()
     * test_preamplifier()
     * test_datalogger()
     * test_station()

 All current examples of sensors except NANOMETRICS_T240_SINGLESIDED have no
 configuration key and no default.
 Messages to this effect are to be expected.
"""
import warnings

from pathlib import Path
import unittest
import re
import glob
import logging

# Third party imports
from obspy.core.utcdatetime import UTCDateTime
from obspy.core.inventory.util import Site

# obsinfo modules
from ..obsmetadata import (ObsMetadata)
from ..instrumentation import (Instrumentation, InstrumentComponent,
                                     Stage, Filter)
from ..helpers import Location
from ..subnetwork import (Station, Subnetwork)
from ..instrumentation.filter import (PolesZeros, FIR, Coefficients,
                                            ResponseList)
from ..misc.printobs import (PrintObs)
from ..misc.datapath import Datapath

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = True


class TestDatapath(unittest.TestCase):
    """
    Test suite and print methods for obsinfo operations.

    Attributes:
        infofiles_path (str): path to datafiles to be tested
        level (str): level to be printed
        test (boolean): determines if this is test mode
        print_output (boolean): determines if this is print mode.
            Both can coexist.
    """

    def setUp(self, test=True, print_output=False, level=None):
        """
        Set up default values and paths

        Args:
            test (bool): Invoke class methods in test mode, i.e. invoke
                assertions as well as obsinfo object creation
            print_output (bool): Invoke class methods in print mode, no
                                 assertions.
            level (str): In print mode, determine up to which level
                         information will be printed
        """
        self.infofiles_path = Datapath()

        self.level = level
        self.test = test
        self.print_output = print_output

    def test_dp_filters(self):
        """
        Test info files in {DATAPATH}/{INST_COMPONENT}/responses/filters

        {INST_COMPONENT} can be "sensors", "dataloggers" or "preamplifiers".
        If you wish to test individual files, use
        test_filter(file) with file an absolute or
        """
        for dir in self.infofiles_path.datapath_list:
            # '*rs" includes sensors, preamplifiers and dataloggers"'
            for x in ("sensors", "preamplifiers", "dataloggers"):
                globs = (
                    Path(dir)
                    .joinpath(x, "stages", "filters")
                    .glob("*.yaml")
                )
                for file in [str(x.resolve()) for x in globs]:
                    self._test_filter(file)

    def _test_filter(self, info_file):
        """
        Test and/or print a filter file.

        All are actual examples except the info files called
        "test---attributes".
        In this special cases there will also be a comparison against a dict
        of expected results.
        This comparison occurs for all four main types of filters.

        Args:
            info_file (str): Filename to test or print
        """
        test_expected_result = {
            "PolesZeros": {
                "type": "PolesZeros",
                "transfer_function_type": "LAPLACE (RADIANS/SECOND)",
                "zeros": [(0.0 + 0.0j)],
                "poles": [
                    (0.546 + 0.191j),
                    (4.00004e4 + 0.000j),
                ],
                "normalization_frequency": 1.0,
                "normalization_factor": 42833.458122775904,
                "offset": 0,
            },
            "FIR": {
                "type": "FIR",
                "symmetry": "ODD",
                "coefficient_divisor": 8388608,
                "coefficients": [
                    -10944,
                    0,
                    103807,
                    0,
                    -507903,
                    0,
                    2512192,
                    4194304,
                ],
                "offset": 7,
            },
            "Coefficients": {
                "type": "Coefficients",
                "transfer_function_type": "DIGITAL",
                "numerator_coefficients": [1, 0.1, -0.3, 0.6],
                "denominator_coefficients": [-0.2, 0.8, 0.4, -0.3],
                "offset": 0,
            },
            "ResponseList": {
                "type": "ResponseList",
                "offset": 0,
                "response_list": [
                    [0.050, 0.56, 0.0],
                    [0.075, 0.73, 0.0],
                    [1, 1, 0.0],
                    [10, 0.97, -179],
                    [100, 0.96, 179],
                    [1000, 0.96, 179],
                    [5000, 0.82, 143],
                    [7500, 0.69, 129],
                ],
            },
            "AD_CONVERSION": {
                "type": "AD_CONVERSION",
                "input_full_scale": 5,
                "output_full_scale": 4294967292,
                "transfer_function_type": "DIGITAL",
                "numerator_coefficients": [1.0],
                "denominator_coefficients": [],
                "offset": 0,
            },
            "ANALOG": {
                "type": "ANALOG",
                "transfer_function_type": "LAPLACE (RADIANS/SECOND)",
                "zeros": [],
                "poles": [],
                "normalization_frequency": 0.0,
                "normalization_factor": 1.0,
                "offset": 0,
            },
            "DIGITAL": {
                "type": "DIGITAL",
                "transfer_function_type": "DIGITAL",
                "numerator_coefficients": [1.0],
                "denominator_coefficients": [],
                "offset": 0,
            },
        }

        read_stream = ObsMetadata.read_info_file(info_file,
                                                 self.infofiles_path)
        obj = Filter.construct(ObsMetadata(read_stream['filter']), "")

        if verbose:
            print(f'Processing filter file:"{info_file}"')

        if self.test:
            # self.assertTrue(isinstance(obj, obj.type),
            #                 f'Object {info_file} is not a {obj.type} filter')

            # compare with expected result
            if re.match("test---attributes", str(info_file)):
                self._filter_compare(info_file, obj, test_expected_result)

        if verbose:
            print(f"Filter test for: {info_file}: PASSED")

        if self.print_output:
            print(obj)

    def _filter_compare(self, info_file, filter, expected_result):
        """
        Test a created filter object against an expected result

        Args:
            info_file (str): Filename to test or print
            filter (str): type of filter
            expected_result (dict): attributes to test against
        """
        ftype = filter.type
        read_dict = vars(filter)

        # Remove notes and extras
        if read_dict.get("notes", None) == []:
            read_dict.pop("notes")
        if read_dict.get("extras", None) is None:
            read_dict.pop("extras")

        self.assertEqual(
            read_dict,
            expected_result.get(ftype, None),
            f" File: '{info_file}'. Computed result: {read_dict} "
            "and expected result: "
            f"{expected_result.get(ftype, None)} are different",
        )

    def test_dp_stages(self):
        """
        Test information files in {DATAPATH}/{INSTRUMENT_COMPONENT}/responses/
        """
        failed_test = False
        for dir in self.infofiles_path.datapath_list:
            files_in_validate_dir = Path(dir).joinpath(
                "*rs",  # includes sensors, preamplifiers and dataloggers
                "responses/*.yaml",
            )
            filelist = glob.glob(str(files_in_validate_dir))
            for file in filelist:
                self._test_stage(file)
            self.assertFalse(failed_test)

    def _test_stage(self, file):
        """Test or print stage according to contained filter type

        Args:
            file (str): Filename to test or print
        """
        if verbose:
            print(f'Processing stage file:"{file}"')

        info_file_dict = ObsMetadata.read_info_file(file, self.infofiles_path)

        stage_from_info_file = Stage(ObsMetadata(info_file_dict["stage"]))

        obspy_result = stage_from_info_file.to_obspy()

        if self.test:

            self._test_common_attributes(stage_from_info_file, obspy_result)

            if isinstance(filter, FIR):
                self.assertEqual(
                    stage_from_info_file.filter.symmetry,
                    obspy_result._symmetry,
                )
                for (
                    info_file_coeff
                ) in stage_from_info_file.filter.coefficients:
                    for obspy_coeff in obspy_result.decimation_correction:
                        self.assertEqual(info_file_coeff / 512, obspy_coeff(f))
            elif isinstance(filter, PolesZeros):
                self.assertEqual(
                    stage_from_info_file.filter.transfer_function_type,
                    obspy_result.pz_transfer_function_type,
                )
                self.assertEqual(
                    stage_from_info_file.filter.normalization_frequency,
                    obspy_result.normalization_frequency,
                )
                self.assertEqual(
                    stage_from_info_file.filter.normalization_factor,
                    obspy_result.normalization_factor,
                )
                self.assertEqual(
                    stage_from_info_file.filter.zeros, obspy_result.zeros
                )
                self.assertEqual(
                    stage_from_info_file.filter.poles, obspy_result.poles
                )
            elif isinstance(filter, ResponseList):
                self.assertEqual(
                    stage_from_info_file.filter.response_list,
                    obspy_result.response_list_elements,
                )
            elif isinstance(filter, Coefficients):
                self.test_common_attributes(stage_from_info_file, obspy_result)
                self.assertEqual(
                    stage_from_info_file.filter.transfer_function_type,
                    obspy_result.cf_transfer_function_type,
                )
                self.assertEqual(
                    stage_from_info_file.filter.numerator_coefficients,
                    obspy_result.numerator,
                )
                self.assertEqual(
                    stage_from_info_file.filter.denominator_coefficients,
                    obspy_result.denominator,
                )

        if verbose:
            print(f"Stage test for: {file}: PASSED")

        if self.print_output:
            print(self)
            if self.level == "all":
                print(self.filter)

    def _test_common_attributes(self, stage_from_info_file, obspy_result):
        """
        Test attributes common to all stages

        Args:
            stage_from_info_file (:class:`Stage`):  Stage portion of dict
                 with attributes
            obspy_result (:class:`Stage`): Dictionary generated by obspy with
                corresponding attributes
        """
        self.assertEqual(stage_from_info_file.name, obspy_result.name)
        self.assertEqual(stage_from_info_file.description,
                         obspy_result.description)
        self.assertEqual(stage_from_info_file.input_units,
                         obspy_result.input_units)
        self.assertEqual(stage_from_info_file.output_units,
                         obspy_result.output_units)
        self.assertEqual(stage_from_info_file.input_units_description,
                         obspy_result.input_units_description)
        self.assertEqual(stage_from_info_file.output_units_description,
                         obspy_result.output_units_description)
        self.assertEqual(stage_from_info_file.gain, obspy_result.stage_gain)
        self.assertEqual(stage_from_info_file.gain_frequency,
                         obspy_result.stage_gain_frequency)
        self.assertEqual(stage_from_info_file.decimation_factor,
                         obspy_result.decimation_factor)
        self.assertEqual(stage_from_info_file.filter.offset,
                         obspy_result.decimation_offset)
        self.assertEqual(stage_from_info_file.delay,
                         obspy_result.decimation_delay)
        self.assertEqual(stage_from_info_file.correction,
                         obspy_result.decimation_correction)

    def test_dp_components(self):
        """
        Test all information files in {DATAPATH}/{INSTRUMENT_COMPONENTS}
        """
        components_list = ("sensors", "preamplifiers", "dataloggers")

        for dir in self.infofiles_path.datapath_list:
            for comp in components_list:
                files_in_validate_dir = Path(dir).joinpath(comp, "*.yaml")
                filelist = glob.glob(str(files_in_validate_dir))
                for file in filelist:
                    if verbose:
                        print(f"Processing component file: {file}")

                    info_file_dict = ObsMetadata.read_info_file(
                        file, self.infofiles_path)

                    # OJO: no configuraton passed from above.
                    # No correction either.
                    obj = InstrumentComponent.dynamic_class_constructor(
                        comp[:-1], info_file_dict)

                    if self.test:
                        self.assertTrue(type(obj), comp[:-1])
                        self._test_equipment_attributes(
                            obj.equipment, obj.obspy_equipment
                        )

                    if verbose:
                        print(f"{file}: PASSED")

                    if self.print_output:
                        PrintObs.print_component(obj, self.level)

    def _test_equipment_attributes(
        self, equipment_from_info_file, obspy_result
    ):
        """
        Test the equipment portion of a component or instrumentation

        Args:
            equipment_from_info_file (:class:`Stage`): Stage portion of
                dict with attributes
            obspy_result (:class:`obspy.core.inventory.response.Stage`):
                Dictionary generated by obspy with corresponding attributes
        """
        try:
            self.assertEqual(equipment_from_info_file.type, obspy_result.type)
            self.assertEqual(
                equipment_from_info_file.description, obspy_result.description
            )
            self.assertEqual(
                equipment_from_info_file.manufacturer,
                obspy_result.manufacturer,
            )
            self.assertEqual(
                equipment_from_info_file.model, obspy_result.model
            )
            self.assertEqual(
                equipment_from_info_file.vendor, obspy_result.vendor
            )
            self.assertEqual(
                equipment_from_info_file.serial_number,
                obspy_result.serial_number,
            )
            self.assertEqual(
                UTCDateTime(equipment_from_info_file.installation_date)
                if equipment_from_info_file.installation_date
                else None,
                obspy_result.installation_date,
            )
            self.assertEqual(
                UTCDateTime(equipment_from_info_file.removal_date)
                if equipment_from_info_file.removal_date
                else None,
                obspy_result.removal_date,
            )
            for dt, obspy_dt in zip(
                equipment_from_info_file.calibration_dates,
                obspy_result.calibration_dates,
            ):
                self.assertEqual(UTCDateTime(dt) if dt else None, obspy_dt)
            self.assertEqual(
                equipment_from_info_file.resource_id, obspy_result.resource_id
            )
        except TypeError:
            print("TypeError, probably in UTCDateTime conversion")

    def test_dp_instrumentations(self):
        """Test all information files in instrumentation directory"""
        for dir in self.infofiles_path.datapath_list:
            files_in_validate_dir = Path(dir) / "instrumentation/*.yaml"

            filelist = glob.glob(str(files_in_validate_dir))

            for file in filelist:
                self._test_instrumentation(file)

    def _test_instrumentation(self, file):
        """
        Test or print a single instrumentation file

        WARNING: Response is assumed to be checked stage by stage at the stage
        level (test_stage),
        Here some trivial checks are done, such as number of stages
        SENSITIVITY MUST BE CHECKED MANUALLY in the StationXML file

        Args:
            file (str): Filename to test or print
        """
        if verbose:
            print(f'instrumentation file:"{file}"', end=" ", flush=True)

        dict = ObsMetadata.read_info_file(file, self.infofiles_path)

        start_date = end_date = "2021-01-03"

        # create a dummy location dictionary for testing
        location_dict = {
            "00": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 200.0},
                "base": {
                    "depth.m": 100.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 1.0, "lat": 1.0, "elev": 1.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "01": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "02": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "03": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "04": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "05": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "06": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "07": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "08": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
            "09": {
                "position": {"lon": 0.0, "lat": 0.0, "elev": 300.0},
                "base": {
                    "depth.m": 200.0,
                    "geology": "unknown",
                    "vault": "Sea floor",
                    "uncertainties.m": {"lon": 2.0, "lat": 2.0, "elev": 2.0},
                    "localisation_method": "Sea surface release point",
                },
            },
        }

        locations = {c: Location(v) for c, v in location_dict.items()}

        obj = Instrumentation(ObsMetadata(dict["instrumentation"]),
                              locations,
                              start_date,
                              end_date,
                              {})
        if self.test:
            for ch in obj.channels:
                self.assertEqual(ch.channel_code(ch.instrument.sample_rate),
                                 ch.obspy_channel.code)
                self.assertEqual(ch.location_code,
                                 ch.obspy_channel.location_code)
                self.assertEqual(ch.location.obspy_latitude,
                                 ch.obspy_channel.latitude)
                self.assertEqual(ch.location.obspy_longitude,
                                 ch.obspy_channel.latitude)
                self.assertEqual(ch.location.elevation,
                                 ch.obspy_channel.elevation)
                self.assertEqual(ch.location.depth_m,
                                 ch.obspy_channel.depth)
                self.assertEqual(ch.orientation.azimuth,
                                 ch.obspy_channel.azimuth)
                self.assertEqual(ch.orientation.dip,
                                 ch.obspy_channel.dip)
                self.assertEqual(ch.instrument.sample_rate,
                                 ch.obspy_channel.sample_rate)
                self.assertEqual(ch.instrument.sensor.obspy_equipment,
                                 ch.obspy_channel.sensor)
                self.assertEqual(ch.instrument.datalogger.obspy_equipment,
                                 ch.obspy_channel.data_logger)
                preamp = (ch.instrument.preamplifier.obspy_equipment
                          if ch.instrument.preamplifier else None)
                self.assertEqual(preamp, ch.obspy_channel.pre_amplifier)
                self.assertEqual(UTCDateTime(ch.start_date)
                                 if ch.start_date else None,
                                 ch.obspy_channel.start_date)
                self.assertEqual(UTCDateTime(ch.end_date)
                                 if ch.end_date else None,
                                 ch.obspy_channel.end_date)
                # self.assertEqual(ch.channel_id_code,
                #                  ch.obspy_channel.description)
                if ch.instrument.response_stages is None:
                    # self.assertIsNone(ch.obspy_channel.response.response_stages)
                    self.assertEqual(ch.obspy_channel.response.response_stages,
                                     [])
                else:
                    self.assertEqual(len(ch.instrument.response_stages),
                                     len(ch.obspy_channel.response
                                         .response_stages))
                self._test_equipment_attributes(obj.equipment,
                                                obj.equipment.obspy_equipment)
        if verbose:
            print("PASSED")
        if self.print_output:
            PrintObs.print_instrumentation(obj, self.level)

    def _test_station(self, file_name="", info_dict={}, read_file=True):
        """
        Test or print a station.

        Args:
            file_name (str): Filename to test or print
            info_dict (dict or :class:``.ObsMetadata``): If not reading
                file, MUST provide an info_dict with the info
            read_file (bool): indicates whether file should be read or
                info_dict will be provided

        WARNING: Comments, extras & Processing string must be checked visually
        WARNING: Check operator visually
        """
        if self.test and not read_file and not info_dict:
            print("MUST provide info_dict if read_file is False")

        if read_file:
            info_dict = ObsMetadata.read_info_file(
                file_name, self.infofiles_path
            )
            info_dict = info_dict["station"]

        key = list(info_dict.keys())[0]
        value = ObsMetadata(list(info_dict.values())[0])

        obj = Station(key, value)

        if self.test:
            # latitude, longitude = Location.get_obspy_latitude_and_longitude(
            #     obj.location)
            site = Site(
                name=obj.site,
                description=None,
                town=None,
                county=None,
                region=None,
                country=None,
            )
            self.assertEqual(obj.label, obj.obspy_station.code)
            self.assertEqual(site.name, obj.obspy_station.site.name)
            self.assertEqual(
                UTCDateTime(obj.start_date) if obj.start_date else None,
                obj.obspy_station.creation_date,
            )
            self.assertEqual(
                UTCDateTime(obj.end_date) if obj.end_date else None,
                obj.obspy_station.termination_date,
            )
            self.assertEqual(
                obj.restricted_status, obj.obspy_station.restricted_status
            )
            self.assertEqual(
                obj.location.obspy_latitude, obj.obspy_station.latitude
            )
            self.assertEqual(
                obj.location.obspy_longitude, obj.obspy_station.longitude
            )
            self.assertEqual(
                obj.location.elevation, obj.obspy_station.elevation
            )
            self.assertEqual(obj.location.vault, obj.obspy_station.vault)
            self.assertEqual(obj.location.geology, obj.obspy_station.geology)

            if not isinstance(obj.instrumentation, str):
                # Check if locations are correctly assigned to channels
                for ch in obj.instrumentation.channels:
                    try:
                        self.assertEqual(
                            obj.locations[ch.location_code].latitude,
                            ch.location.latitude,
                        )
                    except TypeError:
                        pass

                # Check number of channels OK
                num_channels = len(obj.instrumentation.channels)
                self.assertEqual(num_channels, len(obj.obspy_station.channels))
                self.assertEqual(
                    num_channels, obj.obspy_station.total_number_of_channels
                )
                self.assertEqual(
                    num_channels, obj.obspy_station.selected_number_of_channels
                )

        if verbose:
            print(f"Processing station file: {file_name}: PASSED")

        if self.print_output:
            PrintObs.print_station(obj, self.level)

    def test_dp_networks(self):
        """
        Test all information files in {DATAPATH}/network/
        """
        for dir in self.infofiles_path.datapath_list:
            files_in_validate_dir = Path(dir).joinpath("network/*.yaml")
            filelist = glob.glob(str(files_in_validate_dir))
            for file in filelist:
                self._test_subnetwork(file)

    def _test_subnetwork(self, file_name):
        """
        Test or print a subnetwork information file

        Args:
            file_name (str): Filename to test or print

        WARNING: Check operator visually
        """
        info_dict = ObsMetadata.read_info_file(file_name, self.infofiles_path)

        subnet_dict = info_dict.get("network", None)
        if not subnet_dict:
            return

        if verbose:
            print(f"Processing network file: {file_name}")

        logging.disable()
        obj = Subnetwork(ObsMetadata(subnet_dict))
        logging.disable(logging.NOTSET)

        if self.test:
            # description = obj.fdsn_name + " -" + obj.description
            self.assertEqual(obj.fdsn_code, obj.obspy_network.code)
            self.assertEqual(
                UTCDateTime(obj.start_date) if obj.start_date else None,
                obj.obspy_network.start_date,
            )
            self.assertEqual(
                UTCDateTime(obj.end_date) if obj.end_date else None,
                obj.obspy_network.end_date,
            )
            self.assertEqual(
                obj.restricted_status, obj.obspy_network.restricted_status
            )

            # Check number of channels OK
            num_stations = len(obj.stations)
            self.assertEqual(num_stations, len(obj.obspy_network.stations))
            self.assertEqual(
                num_stations, obj.obspy_network.total_number_of_stations
            )
            self.assertEqual(
                num_stations, obj.obspy_network.selected_number_of_stations
            )

            self._test_station(info_dict=subnet_dict["stations"], read_file=False)

        if verbose:
            print(f"Subnetwork test for: {file_name}: PASSED")

        if self.print_output:
            PrintObs.print_network(obj, self.level)

    def _create_test_subnetwork(self, subnetwork_file):
        """
        Read an network information file and return the corresponding dict

        Args:
            subnetwork_file (str): file name to read and create
        Returns:
            (:class:`Subnetwork`)
        """
        subnetwork_dir = Path(__file__).parent.joinpath(
            "data", "instrumentation_files", "subnetwork")
        subnetwork_file = str(network_dir.joinpath(subnetwork_file).resolve())
        info_dict = ObsMetadata.read_info_file(subnetwork_file,
                                               self.infofiles_path)
        return Subnetwork(ObsMetadata(info_dict.get("network", None)))


def run_suite_datapath(argv=None):
    """
    Create all test suites for information files
    """
    print("This program checks all test cases in the datapath")
    print("WARNING: The following are not checked:")
    print("\t* Comments, extras, including Processing")
    print("\t* Attributes of Operator")
    print("\t* Adequacy of seed code")
    print("\t* Sensitivity")
    print("\tOnly locations '00' to '09' are provided to test channels,")
    print("\tplease check that your examples and test cases do not exceed")
    print("\tthese locations")

    def suite():
        """
        test suite
        """

        suite_info_files = unittest.TestSuite()

        suite_info_files.addTest(TestDatapath("test_dp_filters"))
        suite_info_files.addTest(TestDatapath("test_dp_stages"))
        suite_info_files.addTest(TestDatapath("test_dp_components"))
        suite_info_files.addTest(TestDatapath("test_dp_networks"))
        suite_info_files.addTest(TestDatapath("test_dp_instrumentations"))

        return suite_info_files

    result = unittest.TextTestRunner(verbosity=1).run(suite())
    report_result_summary(result)


def report_result_summary(result):
    """
    Report a summary of errors and failures

    :param: result - Contains result stats, errors and failures.
    :type result: object returned by unittest TextTestRunner

    """

    n_errors = len(result.errors)
    n_failures = len(result.failures)

    if n_errors or n_failures:
        print(
            "\n\nSummary: %d errors and %d failures reported\n"
            % (n_errors, n_failures)
        )


if __name__ == "__main__":
    run_suite_datapath(["--all"])
