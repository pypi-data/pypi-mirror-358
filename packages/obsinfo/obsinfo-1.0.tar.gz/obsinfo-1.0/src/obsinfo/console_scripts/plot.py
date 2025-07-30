#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application to plot obsinfo information files.
"""
import logging
import warnings
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from obspy.core.inventory.station import Station as obspy_Station
from obspy.core.inventory.network import Network as obspy_Network
# from obspy.core.inventory.channel import Channel as obspy_Channel
from obspy.core.inventory.response import Response as obspy_Response, InstrumentSensitivity

# obsinfo modules
from ._helpers import file_list
from ..obsmetadata import ObsMetadata
from ..instrumentation import (Instrumentation, Stage, Filter, FilterTemplate,
                               Preamplifier, Sensor, Datalogger,
                               FIR, Coefficients, PolesZeros, ResponseList)
from ..helpers import init_logging  # Location, Locations,  Person
from ..subnetwork import (Subnetwork)  # , Network, Operator)
from ..misc.datapath import Datapath
from .print import print_single_file

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)

logger = init_logging("plot", console_level='WARNING')

plottable_filetypes = ('subnetwork', 'instrumentation_base',
                       'datalogger_base', 'sensor_base', 'preamplifier_base',
                       'stage_base', 'filter')


def main(args):
    """
    Entry point for obsinfoplot. Plot information from information file
    according to its type, and levels below up to the specified level.

    Levels are, in order:
        - subnetwork (plot map)
        - stations (plot station and channel time limits)
        - instrumentations (plot all instrumentations' channel total
            responses')
        - instrumentation (plot instrumentation channel total responses)
        - instrument_components (datalogger, preamplifer, sensor): plot total
            and stage responses
        - stage: plot stage response
        - filter: plot filter response (gain 1)

    ADD OPTION TO COMPARE CONFIGURATIONS!
    """
    files, skipped = file_list(args.input, args.drilldown, ('.yaml', '.json'))
    if args.out_dir is not None:
        Path(args.out_dir).mkdir(exist_ok=True)
    for f in files:
        if len(files) > 1:
            filetype = ObsMetadata.get_information_file_type(str(f))
            if filetype not in plottable_filetypes:
                if args.verbose is True:
                    logger.warning(f'{filetype=} cannot be plotted, printing {f.stem}...')
                    print_single_file(args.info_file, args.n_levels, args.verbose)
                elif args.quiet is False:
                    logger.warning(f'{f.stem}: {filetype=} cannot be plotted')
                continue
            if args.quiet is False:
                print(f'Plotting {f.stem}...')
        _plot_one_file(str(f), args)


def _plot_one_file(info_file, args):
    """
    Plot the information within a single file

    Args:
        info_file (str): input file name
        args (:class:`NameSpace`): command-line arguments or their defaults
    """
    file_base = Path(info_file).stem
    filetype = ObsMetadata.get_information_file_type(info_file)
    try:
        dp = Datapath()
        attributes_dict = ObsMetadata().read_info_file(info_file, dp,
                                                       quiet=True)
    except Exception as e:
        print(str(e))
        return False

    if args.n_levels > 3:
        logger.warning('Requested levels={args.n_levels} limited to 3')
        args.n_levels = 3
    # no_class_msg = f"Can't plot {filetype} files (no associated class)"
    if filetype not in plottable_filetypes:
        if args.verbose is True:
            logger.warning(f'{filetype=} cannot be plotted, passing to print')
            print_single_file(info_file, args.n_levels, args.verbose)
        elif args.quiet is False:
            logger.warning(f'{filetype=} cannot be plotted')
        return

    kwargs = {'file_base': file_base, 'args': args,
              'show': not args.noshow, 'out_dir': args.out_dir}
    if filetype == 'subnetwork':
        n_levels = args.n_levels  # Avoids changing args.n_levels
        if args.n_levels == 0:
            n_levels = 2
        obj = Subnetwork(attributes_dict[filetype])
        _plot_map(obj, **kwargs)  # subnetwork level
        if n_levels > 1:
            _plot_time_spans(obj, **kwargs)  # stations level
        if n_levels > 2:
            _plot_response(obj, **kwargs)  # instrumentations level
    elif filetype == 'instrumentation_base':
        x = logger.level
        logger.setLevel(logging.CRITICAL)   # Avoids error message for locations=None
        obj = Instrumentation({'base': attributes_dict[filetype]},
                              None, '00',
                              '2000-01-01', '3000-01-01')
        logger.setLevel(x)
        _plot_response(obj, **kwargs)   # Instrumentation level
        if args.n_levels > 1:
            for chan in obj.channels:
                for ic in (chan.datalogger, chan.preamplifer, chan.sensor):
                    _plot_response(ic, **kwargs)   # Instrument-component level
                    if args.n_levels > 2:
                        for st in ic.stages:
                            _plot_response(st, **kwargs)  # stage level
    elif filetype in ('datalogger_base', 'preamplifier_base', 'sensor_base'):
        if filetype == 'datalogger_base':
            obj = Datalogger({'base': attributes_dict[filetype]})
        elif filetype == 'sensor_base':
            obj = Sensor({'base': attributes_dict[filetype]})
        elif filetype == 'preamplifier_base':
            obj = Preamplifier({'base': attributes_dict[filetype]})
        _plot_response(obj, **kwargs)
        if args.n_levels > 1:
            for st, i in zip(obj.stages, range(len(obj.stages))):
                kwargs2 = kwargs.copy()
                kwargs2['file_base'] = f'{file_base}_stage{i}'
                _plot_response(obj, **kwargs2)   # stage level
        if args.n_levels > 2:
            logger.error(f'Only two levels ({type(ic)} + stage) available '
                         f'for {type(ic)}')
    elif filetype == 'stage_base':
        obj = Stage({'base': attributes_dict[filetype]}, sequence_number=1)
        _plot_response(obj, **kwargs)
        if args.n_levels > 1:
            logger.error('Only one level available for Stage')
    elif filetype == 'filter':
        obj = Filter.construct(attributes_dict[filetype], 1, 'print')
        _plot_response(obj, **kwargs)
        if args.n_levels > 1:
            logger.error('Only one level available for Stage')
    else:
        raise ValueError(f'Unplottable {filetype=}: SHOULD NEVER GET HERE!')


def _plot_map(subnetwork, file_base, args, show=False, out_dir=None, outfile_format="png"):
    """
    Plots a station map, based on a Subnetwork object

    Args:
        subnetwork (:class:`Subnetwork`): the subnetwork object
        file_base (str): the input filename without its suffix
        out_dir(str or None): directory in which to put output file
        outfile_format (str or None): outfile format ('png', 'pdf', ...)
        show (bool): show plot on the screen
    """
    assert isinstance(subnetwork, Subnetwork)
    # obj = subnetwork.to_obspy()  # returns an osbpy Network object
    # fig = obj.plot(projection='local', resolution='h', show=False)
    fig = _plot_subnetwork_map(subnetwork, args, projection='local', show=False,
                               title=file_base)
    if out_dir is not None:
        plt.savefig(Path(out_dir) / f'{file_base}_plot_map.{outfile_format}')
    if show is True:
        if args.quiet is True:
            plt.pause(5)
        else:
            plt.show()
    plt.close(fig)


def _plot_subnetwork_map(subnetwork, args, projection='local', resolution='50m',
                         show=False, title=None, scale='h'):
    """
    Imitates obspy's Network.plot() function, but with bound checking
    and lat/lon labels

    Args:
        subnetwork (:class:`Subnetwork`): The station subnetwork
        args (:class:`argparse.Namespace`): command-line arguments and defaults
        projection (str): passed directly to cartopy
        resolution (str): passed directly to cartopy
        show (bool): show the figure on the screen?
    """
    extent = _get_map_extent(subnetwork, args.min_map_extent)
    c_lat = np.mean(extent[-2:])
    c_lon = np.mean(extent[:2])
    if c_lat > 60:
        crs = ccrs.NorthPolarStereo(central_longitude=c_lon)
    elif c_lat < -60:
        crs = ccrs.SouthPolarStereo(central_longitude=c_lon)
    else:
        crs = ccrs.AlbersEqualArea(central_longitude=c_lon,
                                   central_latitude=c_lat)
    fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection=crs))
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    water_fill_color="lightblue"
    continent_fill_color='beige'
    land = cfeature.LAND.with_scale(resolution)
    ocean = cfeature.OCEAN.with_scale(resolution)
    ax.set_facecolor(water_fill_color)
    ax.add_feature(ocean, facecolor=water_fill_color)
    ax.add_feature(land, facecolor=continent_fill_color)
    # coast = cfeature.GSHHSFeature(scale=scale)
    # ax.add_feature(coast)
    ax.coastlines(color='0.4')
    gl = ax.gridlines(draw_labels=True, dms=args.show_minutes,
                      x_inline=False, y_inline=False)
    gl.top_labels = False
    gl.right_labels = False
    for s in subnetwork.stations:
        l = s.locations[0]
        ax.plot(l.longitude.value, l.latitude.value, '^', transform=ccrs.PlateCarree())
        ax.text(l.longitude.value, l.latitude.value,
                f'{subnetwork.network.code}.{s.code}', transform=ccrs.PlateCarree())

    if title is not None:
        ax.set_title(title)
    plt.tight_layout()
    if show:
        plt.show()
    return fig


def _get_map_extent(subnetwork, min_map_extent):
    lats = [x.locations[0].latitude.value for x in subnetwork.stations]
    lons = [x.locations[0].longitude.value for x in subnetwork.stations]
    return _get_map_extent_from_lons_lats(lons, lats, min_map_extent)


def _get_map_extent_from_lons_lats(lons, lats, min_map_extent):
    lon_min, lon_max = min(lons), max(lons)
    lat_min, lat_max = min(lats), max(lats)
    lon_cent, lat_cent = (lon_min+lon_max)/2., (lat_min+lat_max)/2.
    km_per_deg_lat = (1.852*60)
    km_per_deg_lon = km_per_deg_lat*np.cos(np.radians(lat_cent))

    lon_min, lon_max = _adjust_minmax(lon_min, lon_max, min_map_extent/km_per_deg_lon)
    lat_min, lat_max = _adjust_minmax(lat_min, lat_max, min_map_extent/km_per_deg_lat)
    return lon_min, lon_max, lat_min, lat_max


def _adjust_minmax(lmin, lmax, min_extent):
    if not lmin == lmax:
        lbuff = 0.2*(lmax-lmin)
        lmin -= lbuff
        lmax += lbuff
    if lmax-lmin < min_extent:
        lbuff = (min_extent - (lmax-lmin))/2.
        lmin -= lbuff
        lmax += lbuff
    return lmin, lmax


def _plot_time_spans(subnetwork, file_base, args, show=False, out_dir=None,
                     outfile_format="pdf"):
    """
    Plots time spans

    Args:
        subnetwork (:class:`Subnetwork`): the subnetwork object
        file_base (str): the input filename without its suffix
        outfile_format (str or None): outfile format ('png', 'pdf', ...)
        show (bool): show plot on the screen
    """
    tick_fs = 'x-small'
    assert isinstance(subnetwork, Subnetwork)
    net = subnetwork.to_obspy()
    sta = []
    sta_colors = ['#cfcfff', '#ffcfcf', '#cfffcf', '#afffff', '#ffafff', '#ffffaf']
    ch = {'starttimes': [], 'widths': [], 'names': []}
    for s in net:
        sta.append({'starttime': s.start_date.matplotlib_date,
                    'width': (s.end_date - s.start_date)/86400,
                    'name': f'{net.code}.{s.code}',
                    'n_chan': len(s.channels)})
        for c in s:
            ch['starttimes'].append(c.start_date.datetime)
            ch['widths'].append((c.end_date - c.start_date)/86400)
            ch['names'].append(f'{s.code}.{c.location_code}.{c.code}')
    f, ax = plt.subplots()
    nch = len(ch['widths'])
    # plot station time spans
    yanchor = 0
    for s, i in zip(sta, range(len(s)+1)):
        ax.add_patch(Rectangle((s["starttime"], yanchor-.45),
                               s["width"], s["n_chan"]-.1,
                               ec='k', fc=sta_colors[i % len(sta_colors)]))
        ax.text(s["starttime"] + s["width"]*1.01, yanchor + s["n_chan"]/2-.5,
                s['name'], ha='left', va='center', rotation='vertical',
                fontsize=tick_fs)
        yanchor += s["n_chan"]
    # plot channel time spans
    ax.barh(y=range(nch), width=ch['widths'], left=ch['starttimes'],
            height=0.8, fc='k')
    ax.set_yticks(range(nch), labels=ch['names'], fontsize=tick_fs)
    first_date = min([x.start_date for x in net.stations])
    last_date = max([x.end_date for x in net.stations])

    # Make x-axis date labels
    major = mdates.YearLocator()
    ax.xaxis.set_major_locator(major)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    if first_date.year == last_date.year:
        ax.set_xlabel(f'{first_date.year}')
    if first_date.year == last_date.year and first_date.month == last_date.month:
        ax.set_xlabel(f'{first_date.year}/{first_date.month}')
        minor = mdates.DayLocator(interval=7)
        ax.xaxis.set_minor_locator(minor)
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    else:
        minor = mdates.MonthLocator(interval=1)
        ax.xaxis.set_minor_locator(minor)
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))

    ax.set_title(file_base)
    plt.xticks(rotation=90, minor=False)
    plt.xticks(rotation=60, minor=True, fontsize='small')
    plt.tight_layout()
    if out_dir is not None:
        plt.savefig(Path(out_dir) / f'{file_base}_time_spans.{outfile_format}')
    if show is True:
        if args.quiet is True:
            plt.pause(5)
        else:
            plt.show()
    return
    plt.close(f)


def _plot_response(in_obj, file_base, args, show=False, out_dir=None,
                   outfile_format='png', min_freq=None, max_freq=None):
    """
    Plots instrument response(s)

    Uses obspy's Network.plot_response() or Response.plot()

    Also plots coefficients for FIR and Coefficient filters

    Args:
        in_obj (:class: `Subnetwork` or `Instrumentation` or
                `Datalogger`, 'Sensor' or 'PreAmplifer' or `Stage`
                or `Filter`): object with response or responses
        file_base (str): input filename, without suffix
        show (bool): show plot on the screen
        outfile_format (str or None): outfile format ('png', 'pdf', ...)
    """
    if isinstance(in_obj, Subnetwork):
        network = in_obj.to_obspy()  # creates obspy Network
        _plot_network_response(network, f'{in_obj.code}_subnetwork', args,
                               show, out_dir, outfile_format)
    elif isinstance(in_obj, Instrumentation):
        channels = [x.to_obspy() for x in in_obj.channels]
        station = obspy_Station('', 0., 0., 0., channels=channels)
        network = obspy_Network('', stations=[station])
        _plot_network_response(network, file_base, args,
                               show, out_dir, outfile_format)
    else:
        min_freq, max_freq = _calc_resp_freq_bounds(in_obj, min_freq, max_freq)
        if isinstance(in_obj, (Datalogger, Preamplifier, Sensor)):
            if in_obj.stages[0].input_sample_rate is None:
                in_obj.stages[0].input_sample_rate = max_freq
            prev_isr = in_obj.stages[0].input_sample_rate
            prev_dec_fact = in_obj.stages[0].decimation_factor
            for s in in_obj.stages[1:]:
                if s.input_sample_rate is None:
                    s.input_sample_rate = prev_isr / prev_dec_fact
                prev_isr = s.input_sample_rate
                prev_dec_fact = s.decimation_factor
            response = obspy_Response(
                instrument_sensitivity=in_obj.instrument_sensitivity,
                response_stages=[x.to_obspy() for x in in_obj.stages])
            if isinstance(in_obj, Datalogger):
                sampling_rate = in_obj.sample_rate
            else:
                sampling_rate = 2*max_freq
            _plot_response_response(response, file_base,  args, show, out_dir,
                                    outfile_format, min_freq,
                                    sampling_rate=sampling_rate)
        elif isinstance(in_obj, Stage):
            if in_obj.input_sample_rate is None:
                in_obj.input_sample_rate = max_freq
            response = obspy_Response(
                instrument_sensitivity=InstrumentSensitivity(
                    in_obj.gain, in_obj.gain_frequency, in_obj.input_units,
                    in_obj.output_units),
                response_stages=[in_obj.to_obspy()])
            _plot_response_response(response, file_base,  args, show, out_dir,
                                    outfile_format, min_freq,
                                    sampling_rate=max_freq)
        elif isinstance(in_obj, FilterTemplate):
            stage = Stage({'base': {'name': 'Filter',
                                    'gain': {'value': 1, 'frequency': 1},
                                    'input_units': {'name': 'm/s',
                                                    'description': 'None'},
                                    'output_units': {'name': 'V',
                                                     'description': 'None'},
                                    'input_sample_rate': 2 * max_freq,
                                    'filter': {'type': 'DIGITAL'}  # Overwritten below
                                   }
                          },
                          sequence_number=1)
            stage.filter = in_obj
            response = obspy_Response(
                instrument_sensitivity=InstrumentSensitivity(1, 1, 'm/s', 'V'),
                response_stages=[stage.to_obspy()])
            _plot_response_response(response, file_base,  args, show, out_dir,
                                    outfile_format, min_freq,
                                    sampling_rate=max_freq)
            if isinstance(in_obj, (FIR, Coefficients)):
                _plot_coeffs(in_obj, file_base, args, show, out_dir, outfile_format)
        else:
            print(f'{type(in_obj)=}, not handled by plot_response')
            return


def _calc_resp_freq_bounds(in_obj, min_freq, max_freq):
    if min_freq is not None and max_freq is not None:
        return min_freq, max_freq
    freq_bounds = [None, None]
    if isinstance(in_obj, Datalogger):
        min_freq = 0.001
        max_freq = in_obj.sample_rate
    elif isinstance(in_obj, (Preamplifier, Sensor)):
        for stage in in_obj.stages:
            fb = _freq_bounds(stage)
            if fb[0] is not None:
                if freq_bounds[0] is None:
                    freq_bounds[0] = fb[0]
                else:
                    freq_bounds[0] = min(freq_bounds[0], min(fb))
            if fb[1] is not None:
                if freq_bounds[1] is None:
                    freq_bounds[1] = fb[1]
                else:
                    freq_bounds[1] = max(freq_bounds[1], min(fb))
    elif isinstance(in_obj, (Stage, FilterTemplate)):
        fb = _freq_bounds(in_obj)
    if max_freq is None:
        if fb[1] is not None:
            max_freq = fb[1]
        else:
            max_freq = 1
    if min_freq is None:
        if fb[0] is not None:
            min_freq = fb[0]
        else:
            min_freq = max_freq/1e5
    assert min_freq <= max_freq/100
    return min_freq, max_freq


def _freq_bounds(in_obj):
    if isinstance(in_obj, Stage):
        in_obj = in_obj.filter
    if not isinstance(in_obj, FilterTemplate):
        raise TypeError("in_obj is not of type Stage or Filter")
    if isinstance(in_obj, PolesZeros):
        given_freqs = [abs(x)/(2*np.pi)
                       for x in in_obj.poles + in_obj.zeros
                       if not x == 0.]
        if len(given_freqs) == 0:  # constant slope response
            return 0.001, 100
        else:
            min_freq = min(given_freqs)/10
            max_freq = max(given_freqs)*10
            return _adjust_bounds(min_freq, max_freq)
    elif isinstance(in_obj, ResponseList):
        given_freqs = [x[0] for x in in_obj.elements if not x == 0.]
        max_freq = max(given_freqs)
        min_freq = min(given_freqs)
        return _adjust_bounds(min_freq, max_freq)
    else:
        return (None, None)


def _adjust_bounds(min_freq, max_freq, min_range=1e5):
    if (max_freq / min_freq) > min_range:
        return min_freq, max_freq
    else:
        add_range = min_range / (max_freq / min_freq)
        return min_freq / np.sqrt(add_range), max_freq * np.sqrt(add_range)


def _plot_network_response(net, file_base, args, show=True, out_dir=None,
                           outfile_format=None, min_freq=0.001):
    """
    Args:
        net (:class:~obspy.core.inventory.network.Network): Network
        file_base (str): input filename without suffix
        show (bool): Show plot on screen
        out_dir (str or None): Directory to output plot to
        outfile_format (str): output file format ('png', 'pdf', etc).  None
            means do not output to a file
        min_freq (float): minimum frequency to plot
    """
    if show is True:
        fig = net.plot_response(min_freq=min_freq, show=False)
        fig.suptitle(file_base)
        if args.quiet is True:
            plt.pause(5)
        else:
            plt.show()
        plt.close(fig)
    if out_dir is not None:
        fig = net.plot_response(min_freq=min_freq, show=False)
        fig.suptitle(file_base)
        plt.savefig(Path(out_dir) / f'{file_base}_responses.{outfile_format}')
        plt.close(fig)


def _plot_response_response(resp, file_base, args, show=True, out_dir=None, outfile_format=None,
                            min_freq=0.001, sampling_rate=2000):
    if resp.response_stages[0].input_units.lower() in ("meter", "m"):
        output = 'DISP'
    elif resp.response_stages[0].input_units.lower() in ("m/s"):
        output = 'VEL'
    elif resp.response_stages[0].input_units.lower() in ("m/s**2"):
        output = 'ACC'
    elif resp.response_stages[0].input_units.lower() in ("pa", "v", "counts"):
        output = 'DEF'
    else:
        logging.warning(f'input_units={resp.response_stages[0].input_units} not in predefined '
                        'values, will use default units')
        output = 'DEF'
    kwargs = dict(min_freq=min_freq, output=output, label=file_base.split('.')[0],
                  sampling_rate=sampling_rate)
    fig = resp.plot(show=False, **kwargs)
    fig.suptitle(file_base)
    if out_dir is not None:
        plt.savefig(Path(out_dir) / f'{file_base}_responses.{outfile_format}')
    if show is True:
        if args.quiet is True:
            plt.pause(5)
        else:
            plt.show()
    plt.close(fig)


def _plot_coeffs(obj, file_base, args, show, out_dir, outfile_format):
    if isinstance(obj, FIR):
        fig, ax = plt.subplots()
        ax.stem(range(len(obj.expanded_coefficients)), obj.expanded_coefficients, markerfmt='b', linefmt='k')
        # ax.axhline(obj.coefficient_divisor, color='green')
        ax.axvline(obj.delay_samples, color='red', label='delay')
        ax.legend()
        ax.set_title(f'{file_base}, divisor={obj.coefficient_divisor}')
        ax.set_xlabel('Offset')
        ax.set_ylabel('Coefficients')
    elif isinstance(obj, Coefficients):
        fig, ax = plt.subplots(2, 1, sharex=True)
        if len(obj.numerator_coefficients) > 0:
            ax[0].stem(obj.numerator_coefficients)
            ax[0].set_xlabel('numerator')
            ax[0].set_title(file_base)
        if len(obj.denominator_coefficients) > 0:
            ax[1].stem(obj.denominator_coefficients)
            ax[1].set_xlabel('denominator')
            ax[1].set_xlabel('Offset')
    else:
        return
    if out_dir is not None:
        plt.savefig(Path(out_dir) / f'{file_base}_plot_coeffs.{outfile_format}')
    if show is True:
        if args.quiet is True:
            plt.pause(5)
        else:
            plt.show()


if __name__ == '__main__':
    raise ValueError('Do not try to run from the command line')
