"""
 Main functions for obsinfo-makeStationXML

 Creates obsinfo objects starting with a network object in a hierarchy which
 strongly follows the hierarchy of StationXML files.
 Then converts the objects to a StationXML file using obspy.
"""
# General library imports
import sys
import os
# import re
import warnings

from pathlib import Path  # , PurePath

from argparse import ArgumentParser

# Third party imports
# import obspy
from obspy.core.inventory import Inventory  # , Station, Channel, Site
from obspy.core.inventory import Network
# from obspy.clients.nrl import NRL

# obsinfo imports
from ..subnetwork import (Subnetwork)
from ..obsmetadata import (ObsMetadata)
from ..misc.datapath import (Datapath)
from .print_version import main as print_version
from ..misc.const import EXIT_USAGE, EXIT_SUCCESS
from ..helpers import init_logging
from ..version import __version__

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = init_logging("makeStationXML")


def main(argv=None, dp=None):
    """
    Entry point for obsinfo-makeStationXML.

     1) Setups status variables from command line arguments.
     2) Read yaml or jason file invoking read_info_file, which returns a
        dictionary. Optionally validates dictionary schema.
     3) Creates obsinfo objects starting from network object from the dictionary
     4) Converts these to StationXML using obpsy libraries.

    Manages all uncaught exceptions.

    Args:
        argv (list): list of command-line arguments to pass to ArgumentParser.
            If None, will use sys.argv
        dp (Datapath): Datapath object specifying where to look for files.
            If None, will use values specified in .obsinforc
    """

    # create list of directories to search for files
    if dp is None:
        dp = Datapath()
    args = retrieve_arguments(argv, dp)

    if args.verbose:
        print(f'Using OBSINFO_DATAPATH: {dp.datapath_list}')

    logger.info(f'Using OBSINFO_DATAPATH: {dp.datapath_list}')

    _make_StationXML(logger, args, dp)

    if argv is None:
        sys.exit(EXIT_SUCCESS)


def _make_StationXML(logger, args, dp):
    # try:

    file = Path(args.input_filename).name

    info_dict = ObsMetadata.read_info_file(args.input_filename, dp,
                                           remote=args.remote,
                                           verbose=args.verbose)

    if args.verbose:
        print(f'Processing subnetwork file: {file}')
    logger.info(f'Processing subnetwork file: {file}')

    subnet_dict = info_dict.get('subnetwork', None)
    if subnet_dict is None:
        raise ValueError('No subnetwork element in top-level of file')

    subnet = Subnetwork(ObsMetadata(subnet_dict), args.station)

    if args.verbose:
        print(f'Subnetwork file parsed successfully for: {file}')
    logger.info(f'Subnetwork file parsed successfully for: {file}')

    obspy_network = subnet.to_obspy()
    if not isinstance(obspy_network, Network):
        print("Not a network object")
        logger.error("Not a network object")

    if not args.quiet:
        print(obspy_network)

    logger.info(obspy_network)

    # Set source and sender
    source = "obsinfo"  # default, modified if there is a subnet operator
    sender = "unknown"  # default, modified if subnet operator has a contact
    if len(subnet.operators) > 0:
        x = subnet.operators[0]
        source = x.agency
        if len(x.contacts) > 0:
            c = x.contacts[0]
            name, email = "????", "????"
            if len(c.names) > 0:
                name = c.names[0]
            if len(c.emails) > 0:
                email = c.emails[0]
            sender = f"{name}, Email: {email}"

    inv = Inventory([obspy_network],  # module=version,
                    source=source,
                    sender=sender,
                    module=f"obsinfo-makeStationXML {__version__}",
                    module_uri="https://gitlab.com/resif/smm/obsinfo")

    if not args.test:  # Generate Stationxml file
        if not args.output:
            stem_name = Path(file).stem       # remove .yaml
            stem_name = Path(stem_name).stem  # Remove .network
            output_filename = stem_name + ".station.xml"
        else:
            output_filename = args.output

        _ = inv.write(output_filename, format="stationxml", validate=False)

    if not args.quiet and not args.test:
        print(f'StationXML file created successfully: {output_filename}')
    logger.info(f'StationXML file created successfully: {output_filename}')


def retrieve_arguments(argv, datapath):

    """
    Retrieve arguments from command line. Setup several status variables and get information file name

    Args:
        argv (list): command line arguments.  If None, uses sys.argv
        datapath (:class:`.Datapath`): Object containing paths to find
            repository files, read from .obsinforc
    Returns:
        args (NameSpace): All status variables and the information file name.
    """
    # Parse the arguments
    parser_args = ArgumentParser(prog="obsinfo-makeStationXML")

    # flags
    parser_args.add_argument(
        "-r", "--remote", action='store_true', default=False,
        help="Assumes input filename is discovered through OBSINFO_DATAPATH "
             "environment variable. Does not affect treatment of $ref in info files")
    # parser_args.add_argument("-l", "--validate", action='store_true', default=None,
    #                          help="Performs complete validation, equivalent to obsinfo-validate, before processing")
    parser_args.add_argument("-v", "--verbose", action='store_true', default=False,
                             help="Prints processing progression")
    parser_args.add_argument("-q", "--quiet", action='store_true', default=False,
                             help="Silences a human-readable summary of processed information file")
    parser_args.add_argument("-d", "--debug", action='store_true', default=False,
                             help="Turns on exception traceback")
    parser_args.add_argument("-t", "--test", action='store_true', default=False,
                             help="Produces no output")
    parser_args.add_argument("-V", "--version", action="store_true", default=False,
                             help="Print the version and exit")
    parser_args.add_argument("-S", "--station", action="store_true", default=False,
                             help="Create a StationXML file with no instrumentation")
    # optional arguments
    parser_args.add_argument("-o", "--output", default=None,
                             help="Names the output file. Default is <input stem>.station.xml")
    # positional arguments
    parser_args.add_argument("input_filename", type=str, nargs=1,
                             help="is required and must be a single value")

    if argv is not None:
        args = parser_args.parse_args(argv)
    else:
        args = parser_args.parse_args()

    if args.version:
        print_version()
        sys.exit(EXIT_SUCCESS)

    # schemas must always be installed under obsinfo/data/schemas
    args.schemapath = Path(__file__).parent.joinpath('data', 'schemas')

    if not args.input_filename:
        print("No input filename specified")
        sys.exit(EXIT_USAGE)

    input_filename = args.input_filename[0]

    args.input_filename = str(datapath.build_datapath(input_filename)
                              if args.remote
                              else Path(os.getcwd()).joinpath(input_filename))

    return args


if __name__ == '__main__':
    main()
