"""
Common helper functions
"""
from pathlib import Path

from ..misc.datapath import Datapath

def file_list(info_dir, drilldown, suffixes=('.yaml', '.json'), quiet=False):
    """
    Create a list of files to process
    
    Args:
        info_dir (string): file, directory, or 'DATAPATH'
        drilldown (bool): drill down through subdirectories?
        suffixes (tuple): only accept files whose lower(suffix) matches one of
            these
    """
    if info_dir == 'DATAPATH':
        info_dir = Datapath().datapath_list[0]
        drilldown = True
        if quiet is False:
            print('Validating first DATAPATH dir')
    info_dir = Path(info_dir)
    if not info_dir.is_absolute():
        info_dir = Path.cwd().joinpath(info_dir).resolve()

    if info_dir.is_file():
        files = [info_dir]
    else:
        if not info_dir.is_dir():
            raise ValueError(f'"{info_dir}" is neither a file nor a directory!')
        if drilldown is True:
            if quiet is false:
                print(f'Processing files in and below directory {info_dir}')
            files = info_dir.glob('**/*.*')
        else:
            if quiet is False:
                print(f'Processing files in directory {info_dir}')
            files = info_dir.glob('*.*')
    skip, keep = [], []
    for file in files:
        if file.suffix.lower() not in suffixes:
            # print(f'Skipping {str(file.relative_to(info_dir))}')
            skip.append(file)
        else:
            keep.append(file)
    if len(skip) > 0:
        if quiet is False:
            print('Skipping files whose suffix is not in {}: {}'.format(
                suffixes, [x.name for x in sorted(skip)]))
    return sorted(keep), sorted(skip)
