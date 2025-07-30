#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Subcommand to copy obsinfo information file templates
"""
import os
import warnings
from pathlib import Path
import shutil

# obsinfo modules
from ..helpers import init_logging

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False

logger = init_logging("print", console_level='WARNING')


def main(args):
    """
    Copy a template file to the current directory.
    """
    template_dir = Path(__file__).parent.parent.joinpath('_templates')
    source = template_dir / f'TEMPLATE.{args.filetype}.yaml'
    target = Path(f'TEMPLATE.{args.filetype}.yaml')
    if target.exists():
        raise ValueError(f'Target file "{target}" exists, will not overwrite')
    shutil.copy(source, target)
    if args.quiet is not True:
        print(f'Wrote file {target}')


if __name__ == '__main__':
    raise ValueError('Do not try to run from the command line')
