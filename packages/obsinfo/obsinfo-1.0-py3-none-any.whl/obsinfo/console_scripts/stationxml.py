"""
 Creates obsinfo objects starting with a network object in a hierarchy which
 strongly follows the hierarchy of StationXML files.
 Then converts the objects to a StationXML file using obspy.
"""
# General library imports
import sys
import os
# import re
import warnings
from time import perf_counter
import subprocess

from pathlib import Path  # , PurePath

# Third party imports
# import obspy
from obspy.core.inventory import Inventory, Network  # , Station, Channel, Site
# from obspy.clients.nrl import NRL

# obsinfo imports
from ..subnetwork import Subnetwork
from ..obsmetadata import ObsMetadata
from ..misc.datapath import Datapath
from ..misc.const import EXIT_USAGE
from ..helpers import init_logging
from ..version import __version__

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = init_logging("xml")


def main(args, dp=None, debug=False):
    """
    Entry point for ``obsinfo xml``.

     1) Setups status variables from command line arguments.
     2) Read yaml or jason file invoking read_info_file, which returns a
        dictionary. Optionally validates dictionary schema.
     3) Creates obsinfo objects starting from network object from the
        dictionary
     4) Converts these to StationXML using obpsy libraries.

    Manages all uncaught exceptions.

    Args:
        args (:class:~`NameSpace`): command-line arguments from argParser
        dp (Datapath): Datapath object specifying where to look for files.
            If None, will use values specified in .obsinforc
    """
    if debug is True:
        tic = perf_counter()
        
    if not args.input_filename:
        print("No input filename specified")
        sys.exit(EXIT_USAGE)

    # schemas must always be installed under obsinfo/data/schemas
    args.schemapath = Path(__file__).parent.joinpath('data', 'schemas')

    assert isinstance(args.input_filename, list)
    x = args.input_filename[0]
    args.input_filename = str(Datapath.build_datapath(x)
                              if args.remote
                              else Path(os.getcwd()).joinpath(x))

    # create list of directories to search for files
    dp = Datapath()

    if args.verbose:
        print(f'Using OBSINFO_DATAPATH: {dp.datapath_list}')

    logger.info(f'Using OBSINFO_DATAPATH: {dp.datapath_list}')

    file = Path(args.input_filename).name

    if debug is True:
        tic = _timing_message(tic, 'Setup')
    
    if not args.quiet:
        print('Reading subnetwork file...', end='', flush=True)
    info_dict = ObsMetadata.read_info_file(args.input_filename, dp,
                                           remote=args.remote,
                                           verbose=args.verbose,
                                           debug=debug)

    if debug is True:
        tic = _timing_message(tic, 'ObsMetadata.read_info_file()')

    if args.verbose:
        print(f'Processing subnetwork file: {file}')
    logger.info(f'Processing subnetwork file: {file}')

    subnet_dict = info_dict.get('subnetwork', None)
    if subnet_dict is None:
        raise ValueError('No subnetwork element in top-level of file')

    if not args.quiet:
        print('Creating Subnetwork object...', end='', flush=True)
    subnet = Subnetwork(ObsMetadata(subnet_dict), args.station)

    if debug is True:
        tic = _timing_message(tic, 'Create obsinfo Subnetwork')

    if args.verbose:
        print(f'Subnetwork file parsed successfully for: {file}')
    logger.info(f'Subnetwork file parsed successfully for: {file}')

    obspy_network = subnet.to_obspy()
    if not isinstance(obspy_network, Network):
        print("Not a network object")
        logger.error("Not a network object")

    if debug is True:
        tic = _timing_message(tic, 'Create obspy network')

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
                    module=f"obsinfo xml {__version__}",
                    module_uri="https://gitlab.com/resif/smm/obsinfo")

    if debug is True:
        tic = _timing_message(tic, 'Create obspy inventory')

    if not args.test:  # Generate Stationxml file
        if not args.output:
            stem_name = Path(file).stem       # remove .yaml
            stem_name = Path(stem_name).stem  # Remove .network
            output_filename = stem_name + ".station.xml"
        else:
            output_filename = args.output

        _ = inv.write(output_filename, format="stationxml", validate=False)

        if debug is True:
            tic = _timing_message(tic, 'Write obspy inventory')

    if not args.quiet and not args.test:
        print(f'StationXML file created: {output_filename}')
        logger.info(f'StationXML file created: {output_filename}')

        _validate_stationxml(output_filename, args.quiet)
    


def _timing_message(tic, message):
        toc = perf_counter()
        print(f'{toc-tic:.1f} seconds: {message}')
        return toc

def _validate_stationxml(filename, quiet, validator_path=None):
    if validator_path is None:
        validator_path = Path(__file__).parent.parent.joinpath('stationxml-validator')
    validators = list(validator_path.glob('*.jar'))
    if len(validators) == 0:
        raise(ValueError(f'No jar-file found in stationxml-validator directory: {str(validator_path)}'))
    elif len(validators) > 1 :
        raise(ValueError(f'More one jar file in stationxml-validator directory: {validators}'))
    else:
        validator = str(validators[0])
    try:
        print(f'Running {validator} ... ', flush=True, end='')
        logger.info(f'Running {validator} ... ')
        outp = subprocess.run(['java', '-jar', validator, filename],
                              capture_output=True, text=True)
    except Exception as e:
        logger.error(f'stationxml-validator error: {e}')
    logger.info(outp.stdout)    
    print(outp.stdout)    
    if quiet is not True:
        'stationxml-validator finished'
    
if __name__ == '__main__':
    main()
