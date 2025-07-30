#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application to print obsinfo information file configurations
"""
import os
import warnings
from pathlib import Path

# obsinfo modules
from ._helpers import file_list
from ..obsmetadata import ObsMetadata
from ..helpers import init_logging
from ..misc.datapath import Datapath

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False

logger = init_logging("print", console_level='WARNING')


def main(args):
    """
    Entry point for obsinfo-configurations. Print defined configuration of
    the given file(s)
    """
    files, skipped = file_list(args.input, args.drilldown, ('.yaml', '.json'),
                               args.quiet)
    bad_types, no_configs, exceptions = [], [], []
    for f in files:
        status = print_single_file_configs(str(f), args.verbose, args.quiet)
        if status == 'bad_type':
            bad_types.append(f.name)
        elif status == 'no_configs':
            no_configs.append(f.name)
        elif status == 'exception':
            exceptions.append(f.name)
    n_files = len(files)
    if args.quiet is False:
        _print_errors(bad_types, n_files, 'file_type does not allow configurations', 'whose')
        _print_errors(exceptions, n_files, 'raised an exception')
        _print_errors(no_configs, n_files, 'did not specify any configurations')

def _print_errors(err_list, n_files, err_message, that_whose='that'):
    if len(err_list) > 0:
        if n_files == 1:
            print(f'{str(err_list[0])}: {err_message}')
        else:
            print(f'Files {that_whose} {err_message}:')
            for x in err_list:
                print(f'   {x}')
            print()

def print_single_file_configs(info_file, verbose=True, quiet=False):
    """
    Print a single obsinfo file's configurations

    Args:
        info_file (str): info file to validate.
    Returns:
        result (str):
            'exception' if exception raised
            'bad_type': if file_type allows no configurations
            'no_configs': if no configurations found in a good file_type
            'ok': everything works
            
    """
    filetype = ObsMetadata.get_information_file_type(info_file)
    try:
        dp = Datapath()
        attributes_dict = ObsMetadata().read_info_file(info_file, dp,
                                                       quiet=True)
    except Exception as e:
        print(str(e))
        return 'exception'
    if filetype in ('instrumentation_base', 'datalogger_base',
                    'sensor_base' 'preamplifier_base',
                    'location_base', 'stage_base', 'timing_base'):
        base = attributes_dict[filetype]
        # print(f'{base=}')
        configs = base.get('configurations', {})
        keys = list(configs.keys())
        if len(keys) > 0:
            if verbose:
                if 'configuration_default' in base:
                    default_str = f'default={base["configuration_default"]}'
                else:
                    default_str = 'no default'
                if quiet is False:
                    print(f'{Path(info_file).name}: ({default_str})')
                for k, v in configs.items():
                    if quiet is False:
                        print(f" {k:>25}: {v.get('configuration_description','No description')}")
            else:
                if quiet is False:
                    print(f'{Path(info_file).name}: {list(configs.keys())}')
        else:
            return 'no_configs'
    else:
        return 'bad_type'
    return 'ok'


if __name__ == '__main__':
    raise ValueError('Do not try to run from the command line')
