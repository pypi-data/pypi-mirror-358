"""
Write a script to convert LCHEAPO data to SDS* using the lcheapo** python package

Includes clock drift and leap-second correction
Script is a BASH shell script
*SDS = SeisComp Data Structure
**THIS PROGRAM DOES NOT CREATE DATA-CENTER QUALITY DATA:
    - drift correction is calculated for each day, not each record
    - does not set drift correction record header flags
    - does not fill in record header time_correction field
"""
import os.path
from pathlib import Path
import warnings

from obspy.core import UTCDateTime

# import obsinfo classes
from ..subnetwork import Subnetwork
from ..misc.datapath import (Datapath)
from ..obsmetadata import (ObsMetadata)
# import information about LCHEAPO reference codes
from .LCHEAPO import get_ref_code

SEPARATOR_LINE = "\n# " + 60 * "=" + "\n"


def process_script(network_code, stations, station_data_path, input_dir=".",
                   output_dir="../", include_header=True,
                   no_drift_correct=False):
    """
    Writes script to transform raw OBS data to SeisComp Data Structure

    Arguments:
        network_code (str): FDSN network_code
        stations (list of :class:`.Station`): the stations to process
        station_data_path (str): the base directory beneath the station data dirs
        input_dir (str): directory beneath station_dir for LCHEAPO data
        output_dir (str): directory beneath station_dir for SDS directory
        include_header (bool): include the header that sets up paths
                               (should be done once)
        no_drift_correct (bool): Do NOT drift correct
    """
    fixed_dir = "lcheapo_fixed"
    s = _header(station_data_path)
    s += _run_station_function(fixed_dir, output_dir)
    for station in stations:
        # station_dir = os.path.join(station_data_path, station.code) ## PSmod 202309
        s += _run_station_call(network_code, station, no_drift_correct)
    return s


def _header(station_data_path):
    s = "#!/bin/bash\n\n"
    s += f'DATA_DIR={station_data_path}\n\n'
    return s


def _run_station_function(fixed_dir='lcheapo_fixed', output_dir="../"):
    s = ('run_station () {\n'
         '    # Run lcfix and lc2SDS_py for one station\n'
         '    # $1: network code\n'
         '    # $2: station code\n'
         '    # $3: obs type\n'
         '    # $4: lc2SDS_py command-line timing options\n'
         '    echo "Working on station $2"\n'
         '    STATION_DIR=$DATA_DIR/$2\n'
         '    echo "------------------------------------------------------------"\n'
         '    echo "Running LCFIX"\n'
         f'    mkdir $STATION_DIR/{fixed_dir}\n'
         '    command cd $STATION_DIR\n'
         '    lchfiles=$(command ls *.lch)\n'
         '    command cd -\n'
         '    echo "lchfiles:" $lchfiles\n'
         f'    lcfix $lchfiles -d "$STATION_DIR" -o "{fixed_dir}"\n'
         '    echo "------------------------------------------------------------"\n'
         '    echo "Running lc2SDS_py"\n'
         f'    mkdir -p $STATION_DIR/{output_dir}\n'
         f'    command cd $STATION_DIR/{fixed_dir}\n'
         '    lchfiles=$(command ls *.fix.lch)\n'
         '    command cd -\n'
         '    echo "lchfiles:" $lchfiles\n'
         '    cmd="lc2SDS_py $lchfiles -d \\"$STATION_DIR\\" -i \\"lcheapo_fixed\\" -o \\"../\\" --network \\"$1\\" --station \\"$2\\" --obs_type \\"$3\\" $4"\n'
         '    echo "Running: $cmd"\n'
         '    eval $cmd\n'
         '    echo "------------------------------------------------------------"\n'
         '    echo "Removing intermediate files"\n'
         f'    command rm -r $STATION_DIR/{fixed_dir}\n'
         '}\n\n')
    return s


def _run_station_call(network_code, station, no_drift_correct):

    """
    Write a call to the run_station() function

    Args:
        network_code (str): network code
        station (:class:`.Station`): station information
        no_drift_correct (bool): do NOT drift correct
    Returns:
        s (str): single-line call
    """
    # Start the command-line options string with NETWORK, STATION and OBS_TYPE
    station_code = station.code ## PSmod 202309
    obs_type = get_ref_code(station.instrumentations[0])
    s = f'run_station "{network_code}" "{station_code}" "{obs_type}"'
    
    # Get clock correction information (synchronizations and leapseconds)
    leaptimes, leaptypes = [], []
    syncs = dict(start_ref=None)
    leaptimes_str, leaptypes_str = "", ""
    for proc in station.processing.attributes:
        if 'clock_correction' in proc:
            cc = proc['clock_correction']
            if "drift" in cc:
                x = "piecewise_linear"
                if not cc["drift"]["type"] == x:
                    raise ValueError(f'clock drift type is "{cc["drift"]["type"]}", LC2SDS only handles "{x}"')
                x = cc["drift"]["syncs_instrument_reference"]
                if not len(x) == 2:
                    raise ValueError('len(syncs_instrument_reference)={len(x)}, not 2')
                syncs = dict(start_ref=x[0][1], start_inst=x[0][0],
                             end_ref=x[1][1], end_inst=x[1][0])
            if 'leapseconds' in cc:
                lsec = cc['leapseconds']
                # Only add leapsecond corrections if the basic miniseed
                # isn't already corrected
                if lsec['applied_corrections']['not_clock_corrected_miniseed'] is False:
                    for x in lsec['list_file_entries']:
                        # The first column of line_text is seconds since 1900-01-01T00:00:00
                        offset = float(x['line_text'].split()[0])
                        utc = UTCDateTime(1900,1,1) + offset
                        leaptimes.append(utc.isoformat())
                        leaptypes.append(x['leap_type'])

    # Add clock correction information to the command-line options string
    tc_strs=[]
    if no_drift_correct is False and None not in list(syncs.values()):
        tc_strs.append("--sync_start_times \'{}\' \'{}\'".format(syncs["start_ref"], syncs["start_inst"]))
        tc_strs.append("--sync_end_times \'{}\' \'{}\'".format(syncs["end_ref"], syncs["end_inst"]))
    if leaptimes:
        tc_strs.append("--leapsecond_times \'{}\'".format(" ".join(leaptimes)))
        tc_strs.append("--leapsecond_types \'{}\'".format(" ".join(leaptypes)))
    s += ' "{}"\n'.format(" ".join(tc_strs))
    
    return s


def _parse_args(argv=None):
    """
    Create argparser and return result
    """
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser = ArgumentParser(prog="obsinfo-makescripts_LS2SDS",
                            description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("subnetwork_file", help="Subnetwork information file")
    parser.add_argument("station_data_path",
                        help="Base path containing the station directories")
    parser.add_argument("-i", "--input_dir", default=".",
                        help="subdirectory of station_data_path/{STATION}/ "
                             "containing input *.lch files "
                             "(default: %(default)s)")
    parser.add_argument("-o", "--output_dir", default="../",
                        help="subdirectory of station_data_path/{STATION}/ "
                             "to put output SDS directory "
                             "(default: %(default)s)")
    parser.add_argument("--suffix", default="_LC2SDS",
                        help="suffix for script filename "
                             "(default: %(default)s)")
    # parser.add_argument("--append", action="store_true",
    #                     help="append to existing script file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("--no_header", action="store_true",
                        help="do not include a script header")
    parser.add_argument("--no_drift_correct", action="store_true",
                        help="do not correct for instrument drift")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="run silently")
    args = parser.parse_args()
    
    return args

def _console_script(argv=None):
    """
    Create a bash-script to convert LCHEAPO data to SDS, with time correction
    """
    args = _parse_args(argv)
    if not args.quiet:
        print("Creating LC2SDS process script, ", end="", flush=True)
    if args.verbose:
        print(f'Reading subnetwork file: {args.subnetwork_file}')

    # READ SUBNETWORK FILE AND EXTRACT ``subnetwork`` sub-dict
    args.subnetwork_file = str(Path(os.getcwd()).joinpath(args.subnetwork_file))
    info_dict = ObsMetadata.read_info_file(args.subnetwork_file, Datapath(), False)
    subnet_dict = info_dict.get('subnetwork', None)
    if not subnet_dict:
        return
    if args.verbose:
        print(f'Processing subnetwork file: {args.subnetwork_file}')

    # CONVERT ``subnetwork`` dict to  Subnetwork object
    subnetwork = Subnetwork(ObsMetadata(subnet_dict))
    if not args.quiet:
        print(f"network {subnetwork.network.code}, stations ", end="", flush=True) ## PSmod 202310
        if args.verbose:
            print("")

    # CREATE SCRIPT
    script = process_script(subnetwork.network.code,
                            subnetwork.stations,
                            args.station_data_path,
                            input_dir=args.input_dir,
                            output_dir=args.output_dir,
                            no_drift_correct=args.no_drift_correct)
    if not args.quiet:
        print(', '.join([s.code for s in subnetwork.stations]))
    
    # WRITE SCRIPT TO A TEXT FILE
    fname = "process" + args.suffix + ".sh"
    if args.verbose:
        print(f" ... writing file {fname}", flush=True)
    with open(fname, 'w') as f:
        f.write(script)
        f.close()
    if not args.verbose and not args.quiet:
        print("")
