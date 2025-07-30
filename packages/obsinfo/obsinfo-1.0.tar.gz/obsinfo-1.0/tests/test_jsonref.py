#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application to test and print obsinfo information files.

Includes class TestObsinfo, class JsonRefTest and entry points.

   # JsonRefTest tests the reading functions of JSON and YAML files.
   # TestObsinfo tests information files content

 Uses $HOME/.obsinforc to determine the information file base, so if you
 want to test the example files, extract them using obsinfo-setup -d or
 put the path to the example files in $HOME/.obsinforc

 Much the SAME functions and methods are called whether printing or testing,
 as there is little difference between both functionalities.
 Entry points vary for each functionality and the distinction is achieved by
 naming the executable with two different names (i.e. a named link):


    * obsinfo-print has entry point print_obs.

    * obsinfo-test has entry point run_suite_info_files. It is meant to be
      used by developers. In this vein, contrary to obsinfo-validate,
      obsinfo-print calls private methods which are not callable from the
      command line but which can be called from the interpreter.

    * JsonRefTest is meant to be called from the interpreter. It has no
      entry point.


 There are two types of testing functionalities.

    a) If the file name includes "test--attributes" the output of the
       corresponding obsinfo test function will be checked against data
       contained in this class.

    b) If the file name is "normal", it will simply run through to make
       sure there are no errors

 Testing for type (a) uses data from
 `obsinfo/tests/data/instrumentation_files/responses/_filters``.
 Testing for type (b) uses data from `obsinfo/_examples/instrumentation_files`

 WARNING: many tests are critically dependent on file hierarchy, including
 names. Do not change names  in tests or _examples hierarchy, or else change
 the names here.

The following methods use four specific file names:

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
from pathlib import Path, PurePath
import unittest
import difflib

# obsinfo modules
from obsinfo.obsmetadata import (ObsMetadata)
from obsinfo.misc.datapath import Datapath
# from obsinfo.misc.const import *

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)

verbose = False


class JsonRefTest(unittest.TestCase):
    """
    Class of test methods for information file format

    Attributes:
        testing_path (str): path to datafiles to be tested aside
            from the examples
        level (str): level to be printed
        test (boolean): determines if this is test mode
        print_output (boolean): determines if this is print mode.
            Both can coexist.
    """
    def setUp(self, test=True, print_output=False, level=None):
        """
        Set up default values and paths
        """
        self.testing_path = Path(__file__).parent.joinpath("data_jsonref").resolve()
        self.level = level
        self.test = test
        self.print_output = print_output

    def assertTextFilesEqual(self, first, second, msg=None):
        with open(first) as f:
            str_a = f.read()
        with open(second) as f:
            str_b = f.read()

        if str_a != str_b:
            first_lines = str_a.splitlines(True)
            second_lines = str_b.splitlines(True)
            delta = difflib.unified_diff(
                first_lines, second_lines,
                fromfile=first, tofile=second)
            message = ''.join(delta)
            if msg:
                message += " : " + msg
            self.fail("Multi-line strings are unequal:\n" + message)

    def test_readJSONREF_json(self):
        """Tests JSONref using a JSON file"""
        fname_A = str(PurePath(self.testing_path).joinpath("jsonref_A.json"))
        fname_AB = str(PurePath(self.testing_path).joinpath("jsonref_AB.json"))
        dp = Datapath(str(self.testing_path))
        AB = ObsMetadata.read_json_yaml_ref(fname_AB, dp, None)
        A = ObsMetadata.read_json_yaml_ref(fname_A, dp, None)
        self.assertTrue(A == AB)

    def test_readJSONREF_yaml(self):
        """Tests JSONref using a YAML file"""
        fname_A = str(PurePath(self.testing_path).joinpath("jsonref_A.yaml"))
        fname_AB = str(PurePath(self.testing_path).joinpath("jsonref_AB.yaml"))
        dp = Datapath(str(self.testing_path))
        A = ObsMetadata.read_json_yaml_ref(fname_A, dp, None)
        AB = ObsMetadata.read_json_yaml_ref(fname_AB, dp, None)
        self.assertTrue(A == AB)

    def test_validate_json(self):
        """
        Test validation of a YAML file.

        The test file has a $ref to a file that doesn't exist, has a field that
        is not specified in the the schema, and lacks a field required in
        the schema
        """
        test_file = PurePath(self.testing_path).joinpath('json_testschema.json')
        test_schema = PurePath(self.testing_path).joinpath(
                                   'json_testschema.schema.json')
        test_schema = 'json_testschema.schema.json'
        self.assertFalse(ObsMetadata().validate(
            str(test_file), str(self.testing_path),
            schema_filename=test_schema, quiet=True,
            dp=Datapath(str(self.testing_path))))


def report_result_summary(result):
    """
    Report a summary of errors and failures

    :param: result - Contains result stats, errors and failures.
    :type result: object returned by unittest TextTestRunner
    """
    n_errors = len(result.errors)
    n_failures = len(result.failures)

    if n_errors or n_failures:
        print('\n\nSummary: {:d} errors and {:d} failures reported\n'.format(
              n_errors, n_failures))


def run_suite_jsonref():
    """
    Create and run test suite for jsonref
    """
    suite_yaml = unittest.TestSuite()
    suite_yaml.addTests(unittest.makeSuite(JsonRefTest))

    result = unittest.TextTestRunner(verbosity=1).run(suite_yaml)

    report_result_summary(result)

    return suite_yaml


if __name__ == '__main__':
    run_suite_jsonref()
