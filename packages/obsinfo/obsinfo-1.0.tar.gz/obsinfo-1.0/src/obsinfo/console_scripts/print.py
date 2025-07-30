#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application to print obsinfo information files.
"""
import os
import warnings
import logging
from pathlib import Path

# obsinfo modules
from ._helpers import file_list
from ..obsmetadata import ObsMetadata
from ..instrumentation import (Instrumentation, Stage, Filter,
                               Preamplifier, Sensor, Datalogger)
from ..helpers import Location, Locations, Person, init_logging, null_location
from ..subnetwork import (Subnetwork, Network, Operator)
from ..misc.datapath import Datapath

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False

logger = init_logging("print", console_level='WARNING')


def main(args):
    """
    Entry point for obsinfo-print. Print an information file according to its
    type, and levels below up to the specified level.

     Captures all exceptions
    """
    files, skipped = file_list(args.input, args.drilldown, ('.yaml', '.json'))
    for f in files:
        print_single_file(str(f), args.n_levels, args.verbose, args.quiet)


def print_single_file(info_file, n_sublevels=0, verbose=True, quiet=False):
    """
    Print a single obsinfo file.

    Args:
        info_file (str): info file to validate.
        n_sublevels (int): number of sublevels to print_directory
    """
    filetype = ObsMetadata.get_information_file_type(info_file)
    try:
        dp = Datapath()
        attributes_dict = ObsMetadata().read_info_file(info_file, dp,
                                                       quiet=True)
    except Exception as e:
        print(str(e))
        return False
    if quiet is False:
        print(f'{Path(info_file).name}: ', end='', flush=True)
    no_class_msg = f"Can't print {filetype} files (no associated class)"
    if filetype == 'subnetwork':
        obj = Subnetwork(attributes_dict[filetype])
    elif filetype == 'network':
        obj = Network(attributes_dict[filetype])
    elif filetype == 'instrumentation_base':
        x = logger.level
        logger.setLevel(logging.CRITICAL)   # Avoids error message for locations=None
        obj = Instrumentation({'base': attributes_dict[filetype]},
                              None, '00',
                              '2000-01-01', '3000-01-01')
        logger.setLevel(x)
    elif filetype == 'datalogger_base':
        obj = Datalogger({'base': attributes_dict[filetype]})
    elif filetype == 'sensor_base':
        obj = Sensor({'base': attributes_dict[filetype]})
    elif filetype == 'preamplifier_base':
        obj = Preamplifier({'base': attributes_dict[filetype]})
    elif filetype == 'location_base':
        obj = Location({'base': attributes_dict[filetype],
                        'position': {'lat.deg': 0, 'lon.deg': 0, 'elev.m': 0}})
    elif filetype == 'stage_base':
        obj = Stage({'base': attributes_dict[filetype]})
    elif filetype == 'operator':
        obj = Operator(attributes_dict[filetype])
    elif filetype == 'filter':
        obj = Filter.construct(attributes_dict[filetype], 1, 'print')
    elif filetype == 'person':
        obj = Person(attributes_dict[filetype])
    elif filetype == 'timing_base':
        if quiet is False:
            print(no_class_msg)
        return
    else:
        if quiet is False:
            print(f"Unknown information file type: '{filetype}")
        return
    if quiet is False:
        print("\n    " + obj.__str__(indent=4, n_subclasses=n_sublevels))


if __name__ == '__main__':
    raise ValueError('Do not try to run from the command line')
