"""
 Main functions for obsinfo-makeStationXML

 Creates obsinfo objects starting with a network object in a hierarchy which
 strongly follows the hierarchy of StationXML files.
 Then converts the objects to a StationXML file using obspy.
"""
import sys
import warnings
from pathlib import Path  # , PurePath
from argparse import ArgumentParser

from ..misc.const import EXIT_SUCCESS
from ..helpers import init_logging
from .stationxml import main as xml_main
from .setup import main as setup_main
from .print import main as print_main
from .plot import main as plot_main
from .configurations import main as config_main
from .schema import main as schema_main
from .template import main as template_main

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = init_logging("makeStationXML")

basedir = Path(__file__).parent.parent
schema_types = [x.stem.split('.')[0]
                for x in basedir.joinpath('data', 'schemas').glob('*.json')]
# Get template types, sort and put filters at end
tt = [x.stem for x in basedir.joinpath('_templates').glob('*.yaml')]
tt.sort()
# template_types = ([x.replace('TEMPLATE.', '') for x in tt if '.filter' not in x] +
#                   [x.replace('TEMPLATE.', '').replace('.filter','') for x in tt if '.filter' in x])
template_types = [x.replace('TEMPLATE.', '') for x in tt]


def _print_version(args):
    file = Path(__file__).parent.parent.joinpath("version.py")
    version = {}
    with open(file) as fp:
        exec(fp.read(), version)
    version = version['__version__']

    print(f"{version=}")


def main():
    """
    Entry point all obsinfo sub-commands
    """
    # create the top-level parser
    parser = ArgumentParser(prog="obsinfo")

    subparsers = parser.add_subparsers(title='subcommands')

    # "version" subcommand
    parser_version = subparsers.add_parser(
        'version', help='Print obsinfo version',
        description='Print obsinfo version')
    parser_version.set_defaults(func=_print_version)

    # "setup" subcommand
    p = subparsers.add_parser(
        'setup',
        description='Set up the obsinfo environment',
        help='Set up obsinfo environment')
    # flags
    p.add_argument("-c", "--no_copy", action='store_true', default=False,
                   help="Don't import anything at all, don't create "
                        "dest directory, which will be removed from datapath")
    p.add_argument("-n", "--no_remote", action='store_true', default=False,
                   help="Install obsinfo without access to a gitlab repository.\n"
                        "May be needed in some operating systems for compatibility")
    p.add_argument("-r", "--invert_datapath", action='store_true', default=False,
                   help="Put remote gitlab repository first. "
                        "All local directories will keep their order")
    p.add_argument("-b", "--branch", action='store_true', default=False,
                   help="Specifies the git branch to use, if not master")
    # optional arguments
    p.add_argument("-d", "--dest", default=None,
                   help="Destination directory for examples.")
    p.add_argument("-g", "--gitlab", default="https://www.gitlab.com",
                   help="Gitlab repository)")
    p.add_argument("-p", "--project", default="resif/obsinfo",
                   help="path to project and the directory where "
                        "information files lie within the Gitlab repository")
    p.add_argument("-l", "--local_repository", default=None,
                   help="Specify local repository for information "
                        "files and include it as first or second option in datapath")
    p.add_argument("-w", "--working_directory", default=None,
                   help="Specify working directory for obsinfo and "
                        "include it as first option in datapath")
    p.add_argument("-P", "--remote_path",
                   default="obsinfo/_examples/instrumentation_files",
                   help="Specify remote directory under project")
    p.set_defaults(func=setup_main)

    # "schema" subcommand
    p = subparsers.add_parser(
        'schema', aliases=['validate'],
        description='Validate an information file against its schema',
        help='Validate an information file against its schema')
    p.add_argument("-q", "--quiet", action='store_true', default=False,
                   help="Don't print informative messages")
    p.add_argument("-s", "--schema", choices=schema_types,
                   help="Force validation against the given schema file "
                        "(sets --check_schema)")
    p.add_argument("--output_schema", action='store_true', default=False,
                   help="Output associated schema file, instead of checking "
                        "against it.")
    p.add_argument("-r", "--remote", action='store_true', default=False,
                   help="Search for the input_filename in the DATAPATH repositories")
    p.add_argument("-d", "--debug", action='store_true', default=False,
                   help="Print traceback for exceptions")
    p.add_argument("--drilldown", action='store_true', default=False,
                   help="Drill down through all subdirectories (if a directory "
                        "was specified)")
    p.add_argument("--continue_on_fail", action='store_true', default=False,
                   help="Continue validating if a file fails (and a directory "
                        "was specified)")
    p.add_argument("--check_schema", action='store_true', default=False,
                   help="Check the schema before validating")
    # positional arguments
    p.add_argument("input", type=str,
                   help="Information file or directory to work on. "
                        "If a directory, works on all files in the "
                        "directory.  If 'DATAPATH', works on all files "
                        "in the DATAPATH (sets --drilldown)")
    p.set_defaults(func=schema_main)

    # "print" subcommand
    p = subparsers.add_parser(
        'print',
        help='Print the obsinfo class created by a file',
        description='Print the obsinfo class created by a file')
    p.add_argument("-n", "--n_levels", type=int, default=1,
                   help="Prints up to N levels (default: %(default)d)")
    p.add_argument("-d", "--debug", action='store_true', default=False,
                   help="Print traceback for exceptions")
    p.add_argument("--drilldown", action='store_true', default=False,
                   help="Drill down through all subdirectories (if a "
                        "directory was specified)")
    p.add_argument("-v", "--verbose", action='store_true', default=False,
                   help="Be verbose")
    p.add_argument("-q", "--quiet", action='store_true', default=False,
                   help="Don't print class string (for debugging only)")
    # positional arguments
    p.add_argument("input", type=str,
                   help="Information file or directory to work on. "
                        "If a directory, works on all files in the "
                        "directory.  If 'DATAPATH', works on all files "
                        "in the DATAPATH (sets --drilldown and "
                        "--n_sublevels=0)")
    p.set_defaults(func=print_main)

    # "plot" subcommand
    p = subparsers.add_parser(
        'plot',
        help='Plot information in the given file',
        description='Plot map, data span and/or response found in a file',
        epilog="Valid file_types are:\n"
               "  subnetwork, instrumentation_base, datalogger, preamplifer, "
               "  sensor, stages, filter \n"
               "The level hierarchy is:\n"
               "  subnetwork->(stations)->instrumentation_base->"
               "{datalogger, preamplifer, sensor}->stages->(stage)->filter")
    # n_levels == 0 means use the default value for the file type
    p.add_argument("-n", "--n_levels", type=int, default=0,
                   help="Plots up to N levels (default: %(default)d)")
    p.add_argument("-d", "--debug", action='store_true', default=False,
                   help="Print traceback for exceptions")
    p.add_argument("--noshow", action='store_true', default=False,
                   help="Don't show plots on screen")
    p.add_argument("--min_map_extent", type=float, default=50.,
                   help="Minimum extent (km) for maps (default: %(default)f)")
    p.add_argument("--show_minutes", action='store_true', default=False,
                   help="Show minutes (instead of dec degrees) on map plots")
    p.add_argument("-o", "--out_dir", type=str, default=None,
                   help="Save a plot file in the specified directory")
    p.add_argument("-v",  "--verbose", action='store_true', default=False,
                   help="Be verbose")
    p.add_argument("-q", "--quiet", action='store_true', default=False,
                   help="Don't print informative messages, and stop showing plot after 5 seconds")
    p.add_argument("--drilldown", action='store_true', default=False,
                   help="Drill down through all subdirectories (if a "
                        "directory was specified)")
    # positional arguments
    p.add_argument("input", type=str,
                   help="Information file or directory to work on. "
                        "If a directory, works on all files in the "
                        "directory.  If 'DATAPATH', works on all files "
                        "in the DATAPATH (sets --drilldown")
    p.set_defaults(func=plot_main)

    # "xml" subcommand
    p = subparsers.add_parser(
        'xml', aliases=['stationxml'],
        description='Create a stationxml file from a subnetwork file',
        help='Create a stationxml file from a subnetwork file')
    # positional arguments
    p.add_argument("input_filename", type=str, nargs=1,
         help="is required and must be a single value")
    # optional arguments
    p.add_argument("-t", "--test", action='store_true', default=False,
                   help="Produces no output")
    p.add_argument("-S", "--station", action="store_true", default=False,
                   help="Create a StationXML file with no instrumentation")
    p.add_argument("-o", "--output", default=None,
                   help="Names the output file. Default is <input stem>.station.xml")
    p.add_argument("-v", "--verbose", action='store_true', default=False,
                   help="Prints processing progression")
    p.add_argument("-q", "--quiet", action='store_true', default=False,
                   help="Don't print informative messages")
    p.add_argument("-d", "--debug", action='store_true', default=False,
                   help="Turns on exception traceback")
    p.add_argument("-r", "--remote", action='store_true', default=False,
                   help="Assumes input filename is discovered through OBSINFO_DATAPATH "
                        "environment variable. Does not affect treatment of $ref in "
                        "info files")
    p.set_defaults(func=xml_main)

    # "template" subcommand
    p = subparsers.add_parser(
        'template', help='Output an information file template')
    # positional arguments
    p.add_argument("filetype", type=str, choices=template_types,
                   help="Information file type")
    p.add_argument("-q", "--quiet", action='store_true', default=False,
                   help="Don't print output file name")
    p.set_defaults(func=template_main)

    # "configurations" subcommand
    p = subparsers.add_parser(
        'configurations', aliases=['configs'],
        help='Print obsinfo information file configurations',
        description='Print obsinfo information file configurations')
    p.add_argument("-d", "--debug", action='store_true', default=False,
                   help="Print traceback for exceptions")
    p.add_argument("--drilldown", action='store_true', default=False,
                   help="Drill down through all subdirectories (if a "
                   "directory was specified)")
    p.add_argument("-v", "--verbose", action='store_true', default=False,
                   help="Print configuration descriptions, as well")
    p.add_argument("-q", "--quiet", action='store_true', default=False,
                   help="Don't print class string (for debugging only)")
    # positional arguments
    p.add_argument("input", type=str,
                   help="Information file or directory to work on. "
                        "If a directory, works on all files in the "
                        "directory.  If 'DATAPATH', works on all files "
                        "in the DATAPATH (sets --drilldown and "
                        "--n_sublevels=0)")
    p.set_defaults(func=config_main)

    args = parser.parse_args()
    if not "func" in args:
        parser.print_help()
    else:
        args.func(args)  # run the appropriate function
    sys.exit(EXIT_SUCCESS)


if __name__ == '__main__':
    main()
