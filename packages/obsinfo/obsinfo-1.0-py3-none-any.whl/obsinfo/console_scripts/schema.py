#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Main functions for obsinfo-validate.

 obsinfo strongly follows the hierarchy of StationXML files.

 Module contains the class ValidateObsinfo and a main entry point for
 `obsinfo schema`.  Should probably put the class elsewhere.
"""
import os
from pathlib import Path
import glob
import re
import sys

from ._helpers import file_list
from ..misc.datapath import Datapath
from ..obsmetadata import ObsMetadata
from ..misc.const import EXIT_SUCCESS
from ..helpers import init_logging

logger = init_logging("schema")


def main(args):
    """
    Entry point for obsinfo-validate.

     1) Sets up status variables from command line arguments.
     2) Validates file according to file type contained in name
     3) Manages all uncaught exceptions
    """

    args.verbose = not args.quiet

    if args.input == 'DATAPATH':
        args.input = Datapath().datapath_list[0]
        args.drilldown = True
        print('Validating first DATAPATH dir')

    if args.schema is not None:
        args.check_schema = True
        
    if args.output_schema == True:
        # Output schema file(s) instead of checking input file(s)
        if filetype is not None:
            _output_schema(filetype)
        files, skipped = file_list(args.input, args.drilldown, ('.yaml', '.json'))
        filetypes = []
        for f in files:
            filetype = ObsMetadata.get_information_file_type(str(args.input))
            if not filetype in filetypes:
                _output_schema(filetype)
                filetypes.append(filetype)
        return

    args.input = Path(args.input)
    if not args.input.is_absolute():
        args.input = Path(os.getcwd()).joinpath(args.input).resolve()
        

    val = ValidateObsinfo(verbose=args.verbose, remote=args.remote,
                          debug=args.debug)

    filetype = None
    if args.schema:
        if ObsMetadata.is_valid_type(args.schema):
            filetype = args.schema
        else:
            raise ValueError(f'Unknown schema type: {args.schema}')

    if args.input.is_file():
        if filetype is None:
            filetype = ObsMetadata.get_information_file_type(str(args.input))
        if args.verbose:
            print(f'Validating {filetype} file')
        val.validate_single_file(str(args.input), filetype,
                                 check_schema=args.check_schema)
    elif args.input.is_dir():
        if args.schema and args.drilldown:
            raise ValueError("Cannot specify schema for a drill-down "
                             "directory validation")
        val.validate_directory(args.input, filetype, args.drilldown,
                               args.continue_on_fail,
                               check_schema=args.check_schema)

    sys.exit(EXIT_SUCCESS)


def _output_schema(filetype):
    """
    Output schema file
    """
    schema_path = Path(__file__).parent.parent.joinpath('data', 'schemas')
    schema_file = f'{filetype}.schema.json'
    shutil.copy(schema_path / schema_file, schema_file)
    

class ValidateObsinfo():
    """
    Methods to validate each level of information files.

    Attributes:
        datapath (:class:`/.Datapath`): Store datapath list(s)
        verbose (bool): Prints progress messages
        remote (bool): Indicates file in command line argument is to be found
            using datapath
        debug (bool): Print more detailed messages.
    """
    def __init__(self, verbose=True, remote=False, debug=False):
        """
        Set up status variables according to .obsinforc and command line args

        Args:
            verbose (bool): Print several progress messages
            remote (bool): Find file in command line argument using datapath
            debug (bool): Print more detailed messages and enable traceback
                of exceptions
        Returns: self
        """
        dp = Datapath()
        self.datapath = dp
        self.datapath.infofiles_path = dp.datapath_list
        self.datapath.validate_path = Path(__file__).parent.parent.joinpath('data', 'schemas')

        self.verbose = verbose
        self.remote = remote
        self.debug = debug

    def validate_single_file(self, info_file, filetype, file_format='yaml',
                             quiet=False, check_schema=False):
        """
        Validate a single obsinfo file.

        Args:
            info_file (str): info file to validate. No assumptions made about
                path.
            filetype (str): the information file type
            file_format (str): the information file format ('json' or 'yaml')
            check_schema (bool): validate schema file as well
        Returns:
            (bool): True if validated, False if not
        """
        if file_format not in ('json', 'yaml'):
            logger.error(f'{file_format=} not in ("json", "yaml")')
            raise ValueError(f'{file_format=} not in ("json", "yaml")')
        try:
            ret = ObsMetadata().validate(info_file,
                                         self.datapath.validate_path,
                                         self.remote,
                                         file_format,
                                         filetype,
                                         self.verbose,
                                         filetype + '.schema.json',
                                         quiet,
                                         check_schema=check_schema)
        except Exception as e:
            logger.error(e)
            return False
        if self.verbose:
            self._print_passed(f'{filetype} test for: {info_file}', ret)
        return ret

    def validate_directory(self, dir, forced_filetype=None, drilldown=False,
                           continue_on_fail=False, check_schema=False):
        """
        Validate all information files in a directory.

        Args:
            dir (:class:`Path`): directory where files reside
            forced_filetype (str): file type.  If None, determine it.
            drilldown (bool): drill down through directories beneath the
                specified one
            continue_on_fail (bool): continue testing if a validation fails
            check_schema (bool): check schema on first use
        Returns:
            false if any file failed
        """
        files, skipped = file_list(dir, drilldown, ('.yaml', '.json'))

        checked_schemas = []
        self_verbose = self.verbose
        filetype = forced_filetype
        any_false = False
        self.verbose = False
        check_this_schema = False
        results = {'passed': 0, 'failed': 0, 'skipped': len(skipped)}
        for file in files:
            if forced_filetype is None:
                filetype = ObsMetadata.get_information_file_type(str(file))
                if filetype is None:
                    print("Could not find a schema for {}, skipping..."
                          .format(str(file.relative_to(dir))))
                    results['skipped'] += 1
                    continue
            print(f"Validating {str(file.relative_to(dir))} against "
                  f"{filetype}.schema.json ... ", end='', flush=True)
            if check_schema is True:
                if filetype in checked_schemas:
                    check_this_schema = False
                else:
                    check_this_schema = True
                    checked_schemas.append(filetype)
            validated = self.validate_single_file(
                str(file), filetype, check_schema=check_this_schema)
            if validated is not True:
                results['failed'] += 1
                print("FAILED")
                any_false = True
                if continue_on_fail is False:
                    print('Quitting on first error')
                    self.verbose = self_verbose
                    return False
            else:
                print("PASSED")
                results['passed'] += 1
        print(80 * '=')
        print('{:d} passed, {:d} failed, {:d} skipped'.format(
            results['passed'], results['failed'], results['skipped']))
        self.verbose = self_verbose
        if any_false is True:
            return False
        return True

    def validate_filters_in_directory(self, dir):
        """
        Validate all information files in filter directory.

        Args:
            dir (str): directory where filter files reside
        """
        if dir.is_dir():
            for file in dir.iterdir():
                self.validate_single_file(file, "filter")

    def validate_stages_in_directory(self, dir):
        """
        Validate all information files in stage directory as given by datapath.

        Args:
            1dir (str): directory where stage files reside
        """
        datalogger_dir_re = re.compile(".*/dataloggers")
        sensor_dir_re = re.compile(".*/sensors")
        exception_re = re.compile(".*/test-with")
        if re.match(datalogger_dir_re, str(dir)) or re.match(sensor_dir_re, str(dir)):
            for file in (Path(dir).joinpath("responses")).iterdir():
                if not file.is_dir() and re.match(exception_re, str(file)) is None:
                    self.validate_single_file(file, "stage")

    def validate_all_components(self):
        """
        Validate all information files in each components

        (sensor, preamplifier, datalogger) subdirectory as given by datapath
        """
        components_list = ("sensors", "preamplifiers", "dataloggers")
        for dir in self.datapath.infofiles_path:
            for comp in components_list:
                # includes sensors, preamplifiers and dataloggers
                files_in_validate_dir = Path(dir).joinpath(comp, "*.yaml")
                self.validate_files(files_in_validate_dir, comp)

    def validate_all_filters(self):
        """
        Validate all filter files in datapath/<component>/responses/filters/"
        """
        for dir in self.datapath.infofiles_path:
            # "*rs includes sensors, preamplifiers and dataloggers"
            files_in_validate_dir = Path(dir).joinpath("*rs", "responses",
                                                       "filters", "*.yaml")
            self.validate_files(files_in_validate_dir, "filter")

    def validate_all_stages(self):
        """
        Validate all stage files in datapath/<component>/responses/
        """
        for dir in self.datapath.infofiles_path:
            # "*rs includes sensors, preamplifiers and dataloggers"
            files_in_validate_dir = Path(dir).joinpath("*rs", "responses",
                                                       "*.yaml")
            self.validate_files(files_in_validate_dir, "stage")

    def validate_all_instrumentations(self):
        """
        Validate all instrumentation files in datapath/instrumentation/
        """
        for dir in self.datapath.infofiles_path:
            # includes sensors, preamplifiers and dataloggers
            files_in_validate_dir = Path(dir).joinpath(
                "instrumentation/*.yaml")
            self.validate_files(files_in_validate_dir, "instrumentation")

    def validate_all_networks(self):
        """
        Validate all network files in datapath/network/
        """
        for dir in self.datapath.infofiles_path:
            # includes sensors, preamplifiers and dataloggers
            files_in_validate_dir = Path(dir).joinpath("network/*.yaml")
            self.validate_files(files_in_validate_dir, "network")

    def validate_files(self, files, filetype):
        """
        Validate all files of a given type

        Args:
            files (:class:`Path`): Full paths of files (including wildcards)
            filetype (str): information file type
        """
        assert ObsMetadata.is_valid_type(filetype)

        filelist = glob.glob(str(files))
        for file in filelist:
            self.validate_single_file(file, filetype)

    @staticmethod
    def _print_passed(text, passed):
        if passed:
            print(f'{text}: PASSED')
        else:
            print(f'{text}: FAILED')


if __name__ == '__main__':
    raise ValueError('This is not a command line program')
