#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application to print obsinfo information files.
"""
import os
import warnings
from pathlib import Path
from argparse import ArgumentParser

# obsinfo modules
from ..obsmetadata import ObsMetadata
from ..instrumentation import (Instrumentation, Stage, Filter,
                                     Preamplifier, Sensor, Datalogger)
from ..helpers import Location, Locations, Person, init_logging
from ..subnetwork import (Subnetwork, Network, Operator)
from ..misc.datapath import Datapath

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False

logger = init_logging("print", console_level='WARNING')


def print_single_file(info_file, n_sublevels=0, configs=False, verbose=True):
    """
    Print a single obsinfo file.

    Args:
        info_file (str): info file to validate.
        n_sublevels (int): number of sublevels to print_directory
        configs (boolean): print configurations instead of object
    """
    filetype = ObsMetadata.get_information_file_type(info_file)
    try:
        dp = Datapath()
        attributes_dict = ObsMetadata().read_info_file(info_file, dp, quiet=True)
    except Exception as e:
        print(str(e))
        return False
    if configs is not True:
        print(f'{Path(info_file).name}: ', end='', flush=True)
        no_class_msg = f"Can't print {filetype} files (no associated class)"
        if filetype == 'subnetwork':
            obj = Subnetwork(attributes_dict[filetype])
        elif filetype == 'network':
            obj = Network(attributes_dict[filetype])
        elif filetype == 'instrumentation_base':
            location_code='00'
            locations = Locations(
                [Location({'position': {'lat': 0, 'lon': 0, 'elev': 0},
                           'base': {'uncertainties.m': {'lat': 0, 'lon': 0, 'elev':0},
                                    'depth.m': 0,
                                    'geology': 'seafloor',
                                    'vault': 'seafloor'},
                           'code': '00'})
                ])
            obj = Instrumentation({'base': attributes_dict[filetype]},
                                  locations, location_code,
                                  '2000-01-01', '3000-01-01')
        elif filetype == 'datalogger_base':
            obj = Datalogger({'base': attributes_dict[filetype]})
        elif filetype == 'sensor_base':
            obj = Sensor({'base': attributes_dict[filetype]})
        elif filetype == 'preamplifier_base':
            obj = Preamplifier({'base': attributes_dict[filetype]})
        elif filetype == 'location_base':
            obj = Location({'base': attributes_dict[filetype],
                             'position': {'lat': 0, 'lon': 0, 'elev': 0}})
        elif filetype == 'stage_base':
            obj = Stage({'base': attributes_dict[filetype]})
        elif filetype == 'network':
            print(no_class_msg)
            return
        elif filetype == 'operator':
            obj = Operator(attributes_dict[filetype])
        elif filetype == 'filter':
            obj = Filter.construct(attributes_dict[filetype], 1, 'print')
        elif filetype == 'person':
            obj = Person(attributes_dict[filetype])
        elif filetype == 'timing_base':
            print(no_class_msg)
            return
        else:
            print(f"Unknown information file type: '{filetype}")
            return
        print("\n    " + obj.__str__(indent=4, n_subclasses=n_sublevels))
    else:
        if filetype in ('instrumentation_base', 'datalogger_base',
                        'sensor_base' 'preamplifier_base',
                        'location_base', 'stage_base', 'timing_base'):
            configs = attributes_dict[filetype].get('configurations', {})
            keys = list(configs.keys())
            if verbose or len(keys) > 0:
                print(f'{Path(info_file).name}: ', end='', flush=True)
                print(f"{list(configs.keys())}")
        else:
            if verbose:
                print(f'{Path(info_file).name}: ', end='', flush=True)
                print(f"file type: '{filetype}' has no configurations")
            return


def print_directory(info_dir, n_sublevels=1, configs=False,
                    drilldown=False, verbose=False):
    """
    Validate all information files in a directory.

    Args:
        info_dir (:class:`Path`): directory where files reside
        drilldown (bool): drill down through subdirectories
        n_sublevels (int): number of sublevels to print_directory
        configs (boolean): print configurations instead of object
    Returns:
        false if any file failed
    """
    suffixes = ['.yaml', '.json']
    if not info_dir.is_dir():
        raise ValueError(f'"{info_dir}" is not a directory!')
    if drilldown is True:
        print(f'Printing files in and below directory {info_dir}')
        files = info_dir.glob('**/*.*')
    else:
        print(f'Validating files in directory {info_dir}')
        files = info_dir.glob('*.*')
    print(f'Will skip files whose suffix is not in "{suffixes}"')
    for file in files:
        if file.suffix.lower() not in suffixes:
            print(f'Skipping {str(file.relative_to(info_dir))}')
            continue
        print_single_file(str(file), n_sublevels=n_sublevels,
                          configs=configs, verbose=verbose)


def main():
    """
    Entry point for obsinfo-print. Print an information file according to its
    type, and levels below up to the specified level.

     Captures all exceptions

    """

    args = retrieve_arguments()

    if args.input.is_file():
        print_single_file(str(args.input), args.n_levels, args.configs,
                          args.verbose)
    elif args.input.is_dir():
        print_directory(args.input, args.n_levels, args.configs, args.drilldown,
                        args.verbose)


def retrieve_arguments():
    """
    Retrieve arguments from command line.

    Setup several status variables and get information file name

    Returns:
        (dict): all status variables and information file name.
    """

    # Parse the arguments
    parser = ArgumentParser(prog="obsinfo-print")

    # flags
    parser.add_argument("-n", "--n_levels", type=int, default=1,
                        help="Prints up to N levels")
    parser.add_argument("-d", "--debug", action='store_true', default=False,
                        help="Print traceback for exceptions")
    parser.add_argument("--drilldown", action='store_true', default=False,
                        help="Drill down through all subdirectories (if a "
                        "directory was specified)")
    parser.add_argument("--configs", action='store_true', default=False,
                        help="Print configurations instead of object")
    parser.add_argument("--verbose", action='store_true', default=False,
                        help="Be verbose")
    # positional arguments
    parser.add_argument("input", type=str,
                        help="Information file or directory to be validated. "
                             "If a directory, tests all files in the "
                             "directory.  If 'DATAPATH', will test all files "
                             "in the DATAPATH (sets --drilldown and "
                             "--n_sublevels=0)")

    args = parser.parse_args()

    if args.input == 'DATAPATH':
        args.input = Datapath().datapath_list[0]
        args.drilldown = True
        print('Validating first DATAPATH dir')
    args.input = Path(args.input)
    if not args.input.is_absolute():
        args.input = Path(os.getcwd()).joinpath(args.input).resolve()

    return args


if __name__ == '__main__':
    main()
