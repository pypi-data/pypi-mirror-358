"""
Write extraction script for LCHEAPO instruments (proprietary to miniseed),
using Epos-France SMM A-node tools
"""
# import obsinfo
from obsinfo.subnetwork import Subnetwork
from ..misc.datapath import (Datapath)
from ..obsmetadata import (ObsMetadata)
from pathlib import Path
import os.path

from .LCHEAPO import get_ref_code

SEPARATOR_LINE = "\n# " + 60 * "=" + "\n"


def process_script(subnetwork, station_data_path, distrib_dir,
                   input_dir=".", output_dir="miniseed_basic"):
    """
    Writes script to transform raw OBS data to miniSEED

    Arguments:
        subnetwork (:class: ~obsinfo.Subnetwork): the subnetwork to process
        station_data_path (str): the base directory beneath the station data dirs
        distrib_dir (str or None): directory where the lcheapo executables and
                           property files are found.  If None, use lcheapo_py
                           executables
        input_dir (str): directory beneath station_dir for LCHEAPO data
        output_dir (str): directory beneath station_dir for basic miniseed]
    """
    network_code = subnetwork.network.code
    stations = subnetwork.stations
    # station_dir = os.path.join(args.station_data_path, station.code)

    s =  __header(station_data_path, output_dir, distrib_dir)
    s += _create_run_station_func('fixed', output_dir, distrib_dir)
    for station in stations:
        s += _call_run_station(network_code, station)
    return s


def __header(station_data_path, output_dir, distrib_dir):
    s = ("#!/bin/bash\n\n"
         f'DATA_DIR={station_data_path}\n'
         f'mkdir -p $DATA_DIR/{output_dir}\n'
         '\n')
    if distrib_dir is not None:
        s += (f"LC2MS_EXEC={os.path.join(distrib_dir,'bin','lc2ms')}\n"
              f"LC2MS_CONFIG={os.path.join(distrib_dir,'config','lc2ms.properties')}\n"
              f"SDPPROCESS_EXEC={os.path.join(distrib_dir,'bin','sdp-process')}\n"
              f"MSMOD_EXEC={os.path.join('/opt/iris','bin','msmod')}\n"
              "\n")
    return s


def _create_run_station_func(fixed_dir, output_dir, distrib_dir, force_quality_D=False,
                             out_fnames_model="%E.%S.00.%C.%Y.%D.%T.mseed"):
    force_quality_cmd = ""
    if distrib_dir is not None:
        # Set up variables for running with noued A LC2MS code
        title = "Run lcfix and lc2MS for one station"
        lc2ms_cmd = ('LC2MS_EXEC $lchfiles -d \\"$STATION_DIR\\" -i \\"lcheapo_fixed\\" '
                     '-o \\"$STATION_DIR/{output_dir}\\" -m ":{out_fnames_model} '
                     '--experiment \\"$1\\" --sitename \\"$2\\" --obstype \\"$3\\" '
                     '--sernum \\"$4\\" -p $LC2MS_CONFIG\n')
        if force_quality_D is True:
            force_quality_cmd = __force_quality_commands(rel_path, "D")
    else:
        # Set up variables for running with lc2ms_py
        title = "Run lcfix and lc2ms_py for one station"
        lc2ms_cmd = (f'lc2ms_py $lchfiles -d \\"$STATION_DIR\\" -i \\"{fixed_dir}\\" '
                     f'-o \\"$DATA_DIR/{output_dir}\\" '
                     '--network \\"$1\\" --station \\"$2\\" --obs_type \\"$3\\"')
    s = ('run_station () {\n'
         f'    # {title}\n'
         '    # $1: network code\n'
         '    # $2: station code\n'
         '    # $3: obs type\n'
         '    # $4: obs serial number\n'
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
         f'    command cd $STATION_DIR/{fixed_dir}\n'
         "    lchfiles=$(command ls *.fix.lch | tr '\\n' ' ')\n"
         '    command cd -\n'
         '    echo "lchfiles:" $lchfiles\n'
         f'    cmd="{lc2ms_cmd}"\n'
         '    echo "Running: $cmd"\n'
         '    eval $cmd\n'
         '    echo "------------------------------------------------------------"\n'
         '    echo "Removing intermediate files"\n'
         f'    command rm -r $STATION_DIR/{fixed_dir}\n'
         f'    {force_quality_cmd}\n'
         '}\n\n'
         )
    return s



def __force_quality_commands(rel_path, quality="D"):
    """ Forces miniseed files to have given quality ('D' by default)
    """
    s = ('    echo "{"-"*60}"\n'
         '    echo "Forcing data quality to {quality}"\n'
         '    echo "{"-"*60}"\n'
         # THE FOLLOWING ASSUMES THAT SDP-PROCESS IS IN OUR PATH, NOT NECESSARILY THE CASE
         f'    $SDPPROCESS_EXEC -d $STATION_DIR -c="Forcing data quality to {quality}" '
         '--cmd="$MSMOD_EXEC --quality {quality} -i {rel_path}/*.mseed"\n')
    return s


def _call_run_station(network_code, station):

    """
    Write a call to the run_station() function

    Args:
        network_code (str): network code
        station (:class:`.Station`): station information
    Returns:
        s (str): single-line call
    """
    inst = station.instrumentations[0]
    return 'run_station "{}" "{}" "{}" "{}"\n'.format(
        network_code, station.code, get_ref_code(inst),
        inst.equipment.serial_number)


def _parse_args(argv, default_suffix, set_distrib_path):
    """
    Create a bash-script to convert LCHEAPO data to basic miniSEED
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog="obsinfo-make_process_scripts_LC2MS", description=__doc__
    )
    parser.add_argument("subnetwork_file", help="Subnetwork information file")
    parser.add_argument("station_data_path", help="Base path containing stations data")
    if set_distrib_path is True:
        parser.add_argument("distrib_path", help="Path to lcheapo software distribution")
    parser.add_argument("-i", "--input_dir", default=".",
                        help="subdirectory of station_data_path/{STATION}/ "
                             "containing input *.raw.lch files")
    parser.add_argument("-o", "--output_dir", default="BASIC_MINISEED",
                        help="subdirectory of station_data_path "
                             "to put output *.mseed files")
    parser.add_argument("--suffix", default=default_suffix,
                        help="suffix for script filename")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("--no_header", action="store_true",
                        help="do not include a script header")
    parser.add_argument("-q", "--quiet", action="store_true", help="run silently")
    return parser.parse_args()

def _read_subnetwork(args):
    """
    Read in subnetwork file and return Subnetwork object
    """
    # READ IN SUBNETWORK INFORMATION
    dp = Datapath()
    if args.verbose:
        print(f'Reading subnetwork file: {args.subnetwork_file}')
    args.subnetwork_file = str(Path(os.getcwd()).joinpath(args.subnetwork_file))
    info_dict = ObsMetadata.read_info_file(args.subnetwork_file, dp, False)
    subnet_dict = info_dict.get('subnetwork', None)
    if not subnet_dict:
        return
    if args.verbose:
        print(f'Processing subnetwork file: {args.subnetwork_file}')
    subnetwork = Subnetwork(ObsMetadata(subnet_dict))

    if not args.quiet:
        print("network {}, subnetwork stations {}"
             .format(subnetwork.network.code,
                     ", ".join([x.code for x in subnetwork.stations])))
    return subnetwork

def _write_process_file(script, args):
    """
    """
    fname = "process" + args.suffix + ".sh"
    if not args.quiet:
        print(f"Writing file {fname}", flush=True)
    with open(fname, "w") as f:
        f.write(script)
        f.close()
    if not args.verbose and not args.quiet:
        print("")

def console_lc2mspy(argv=None):
    """
    Runs python codes to create miniSEED files
    """
    args = _parse_args(argv, "_LC2MSPY", False)
    subnetwork = _read_subnetwork(args)
    script = process_script(subnetwork, args.station_data_path,
                            None,
                            args.input_dir, args.output_dir)
    _write_process_file(script, args)


def console_lc2ms_noeuda(argv=None):
    """
    Runs SMM noeud A codes to create miniSEED files

    Requires O Dewee program lc2ms, and IRIS program msmod
    """
    args = _parse_args(argv, "_LC2MS_NOEUDA", True)
    subnetwork = _read_subnetwork(args)
    script = process_script(subnetwork, args.station_data_path,
                            args.distrib_path,
                            args.input_dir, args.output_dir)
    _write_process_file(script, args)

