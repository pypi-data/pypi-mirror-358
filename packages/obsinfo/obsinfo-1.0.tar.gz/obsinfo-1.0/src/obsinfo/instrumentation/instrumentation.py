"""
Instrumentation class
"""
# Standard library modules
import warnings
import logging
from pprint import pprint

# Non-standard modules

# obsinfo modules
from ..obsmetadata import ObsMetadata
from .equipment import Equipment
# from .instrument_component import Equipment
from .channel import Channel, Channels
from ..helpers import (str_indent, verify_dict_is_empty, Location,
                       null_location, ObsinfoClassList)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Instrumentations(ObsinfoClassList):
    """
    A list of Instrumentation objects
    """
    def __init__(self, attributes_dict_list, locations,
                 station_location_code, station_start_date, station_end_date):
        """
        Args:
            attributes_dict_list (list of (dict, :class:`ObsMetadata`, or str)):
                instrumentations attributes
            locations (:class:`Locations`):  list of Locations
            station_location_code (str): station's location code
            station_start_date (str): station start date
            station_end_date (str): station end date
        """
        instrumentations_list = []
        if isinstance(attributes_dict_list, list):
            for inst in attributes_dict_list:
                instrumentations_list.append(
                    Instrumentation(inst, locations,
                                    station_location_code,
                                    station_start_date, station_end_date))
        else:
            raise TypeError('instrumentation_list is not a list')
        super().__init__(instrumentations_list, Instrumentation)


class Instrumentation(object):
    """
    One or more Instrument Channels. Part of an obspy/StationXML Station

    Methods convert info files to an instance of this class. No equivalent
    obspy/StationXML class

    A more detailed description the class and its attributes is found in XXX

    Attributes:
        equipment (:class:`Equipment`):
        channels (list): list of channels (:class:`Channel`)
    """
    def __init__(self, attributes_dict, locations, station_location_code,
                 station_start_date, station_end_date):
        """
        Constructor

        attributes_dict may contain a configuration_selection for the
        instrumentation and the corresponding configs for the components:
        datalogger, preamplifier and sensor

        Args:
            attributes_dict (dict or :class:`ObsMetadata`):
                instrumentation attributes
            locations (:class:`Locations`):  list of Locations.  If
                None, will print warning and create a null location for 
                each station and channel location_code
            station_location_code (str): station's location code
            station_start_date (str): station start date
            station_end_date (str): station end date

        It is assumed an instrumentation's default location,
        start date and end_date are the same as its station's.
        """
        if isinstance(attributes_dict, str):
            self.equipment = attributes_dict
            self.input = attributes_dict
            self.channels = []
            return
        if locations is None:
            logger.error('locations is None, creating a null location for each channel')
        if not isinstance(station_location_code, str):
            raise TypeError(f'station_location_code is a {type(station_location_code)}, should be a str')
        if isinstance(attributes_dict['base'], str):
            # No base instrument defined, should act like a None
            self.channels = Channels()
            self.equipment = Equipment({'description': attributes_dict['base']})
            return
        
        ic_names = ('datalogger', 'sensor', 'preamplifier')

        self.input = {'attributes_dict': {} if not attributes_dict else '<ObsMetaData>',
                      'locations': locations,
                      'station_start_date': station_start_date,
                      'station_end_date': station_end_date,
                      'station_location_code': station_location_code}
        
        # Syntax checking - Check whether
        if not attributes_dict:
            msg = 'No instrumentation attributes'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        elif isinstance(attributes_dict, dict):
            if not isinstance(attributes_dict, ObsMetadata):
                attributes_dict = ObsMetadata(attributes_dict)
        else:
            # Easy mistake of including a dash in the yaml file
            msg = 'Instrumentation is not a dict'
            logger.error(msg)
            raise TypeError(msg)

        # Remove elements not to be processed here
        channel_modifs = attributes_dict.pop('channel_modifications', ObsMetadata({}))
        if 'notes' in attributes_dict:
            del attributes_dict['notes']

        # Extract instrument_component modifications
        mods = attributes_dict.get('modifications', None)
        if mods is not None:
            # Extract InstrumentComponent modifications
            ic_modifs = ObsMetadata({ic: mods.pop(ic)
                                    for ic in ic_names if ic in mods})
            # Put remaining modifications back
            attributes_dict['modifications'] = mods
        else:
            ic_modifs = ObsMetadata({})

        # Put shortcuts in the right place:
        if 'serial_number' in attributes_dict:
            x = attributes_dict.pop('serial_number')
            attributes_dict.safe_update(
                {'modifications': {'equipment': {'serial_number': x}}},
                warn_crush=True)
        if 'datalogger_configuration' in attributes_dict:
            x = attributes_dict.pop('datalogger_configuration')
            channel_modifs.safe_update(
                {'*-*': {'datalogger': {'configuration': x}}},
                warn_crush=True)


        # Get main elements
        base_dict = attributes_dict.get_configured_modified_base()
        base_location_code = base_dict.pop('location_code', station_location_code)
        ### 'configuration' is solely informational
        base_configuration = base_dict.pop('configuration', None)
        self.equipment = Equipment(base_dict.pop('equipment', None))
        bcd = base_dict.pop('configuration_description', None)
        if 'configuration_description' in base_dict:
            self.equipment.description += f' [config: {base_dict.pop("configuration_description")}]'
        channels_dict = base_dict.pop('channels', {})
        channel_default = channels_dict.pop('default')

        # Fill in channels
        self.channels = Channels()
        matched_channel_modif_codes = []
        for das_label, ch_attributes in channels_dict.items():
            if not 'location_code' in ch_attributes:
                ch_attributes['location_code'] = base_location_code
            ch_modifs, matched_codes = self._select_channel_modifs(ch_attributes, channel_modifs)
            if len(matched_codes) > 0:
                matched_channel_modif_codes.extend(matched_codes)
            # Extract InstrumentComponent modifiers and update ic_modifiers dict
            ic_names = ('datalogger', 'sensor', 'preamplifier')
            ic_ch_modifs = ic_modifs.copy()
            ic_ch_modifs.safe_update({ic: ObsMetadata(ch_modifs.pop(ic))
                                      for ic in ic_names if ic in ch_modifs})

            # Update dictionairies
            ch_attributes.safe_update(ch_modifs)
            ch_dict = channel_default.copy()
            # There can only be one orientation code
            if 'orientation' in ch_dict and 'orientation' in ch_attributes:
                if not ch_dict['orientation'].keys() == ch_attributes['orientation'].keys():
                    ch_dict['orientation'] = ch_attributes['orientation']
            ch_dict.safe_update(ch_attributes)
            
            # Put start_date and end_date in dictionary
            if not 'start_date' in ch_dict:
                ch_dict['start_date'] = station_start_date
            if not 'end_date' in ch_dict:
                ch_dict['end_date'] = station_end_date

            # Select location
            location_code = ch_dict.pop('location_code')
            if locations is not None:
                location = locations.get_by_loc_code(location_code)
                if location is None:
                    raise ValueError(f'{location_code=} not in locations')
            else:
                location = null_location(location_code)
            # Create channel
            self.channels.append(Channel(ch_dict, ic_ch_modifs, location,
                                         self.equipment))
        # verify that each channel modif code was matched
        for k in channel_modifs.keys():
            if not k in matched_channel_modif_codes:
                logger.error(f'channel_modification code "{k}" not matched by an existing channel')
        verify_dict_is_empty(base_dict)

    def __repr__(self):
        if isinstance(self.equipment, str):
            return f'Instrumentation("{self.equipment}")'
        s = (f'Instrumentation(attributes_dict={self.input["attributes_dict"]}, '
             f'locations={self.input["locations"]}, '
             f'station_location_code={self.input["station_location_code"]}, '
             f'station_start_date={self.input["station_start_date"]}, '
             f'station_end_date={self.input["station_end_date"]})')
        return s

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return self.__class__.__name__
        kwargs = dict(indent=4, n_subclasses=n_subclasses-1)
        if isinstance(self.equipment, str):
            return f'Instrumentation: "{self.equipment}"'
        s = 'Instrumentation:\n'
        s += f'    equipment: {self.equipment.__str__(**kwargs)}\n'
        s += f'    channels: {self.channels.__str__(**kwargs)}\n'
        return str_indent(s, indent)

    @staticmethod
    def _select_channel_modifs(chan_dict: dict, channel_modifs: dict):
        """
        Select channel_modifications for the provided chan_dict

        Args:
            chan_dict (dict or :class:`ObsMetadata`): channel attributes.
                Must have 'orientation' and 'location_code' keys
            channel_modifs (dict): channel_modifications, keys are
                id_codes, in order of priority:
                    "<ORT>-<LOC>": orientation_code <ORT> & location_code <LOC>
                    "<ORT>": orientation_code <ORT>
                    "*-<LOC>": location_code <LOC>, all orientation_codes
                    "<ORT>-*": orientation_code <ORT>, all location_codes
                    "*-*": All ``id_codes``

        Returns:
            (:class:`ObsMetadata``): the selected channel modifications
        """
        for k in ('orientation', 'location_code'):
            if k not in chan_dict:
                raise ValueError(f'chan_dict has no "{k}" key')
        oc = chan_dict['orientation']['code']
        lc = chan_dict['location_code']
        id_patterns = [oc, oc + "-" + lc]
        loc_pattern = "*-" + lc
        orient_pattern = oc + '-*'
        glob_patterns = ["*", "*-*"]
        
        # Get modifications, classed by specification type
        mods_specific = ObsMetadata(channel_modifs.get(id_patterns[0], {}))
        mods_specific.safe_update(channel_modifs.get(id_patterns[1], {}))
        mods_loc = channel_modifs.get(loc_pattern, {})
        mods_orient = channel_modifs.get(orient_pattern, {})
        mods_default = ObsMetadata(channel_modifs.get(glob_patterns[0], {}))
        mods_default.safe_update(channel_modifs.get(glob_patterns[1], {}))

        # Put modifications in order of priority
        chmods = ObsMetadata(mods_default)
        chmods.safe_update(mods_orient)
        chmods.safe_update(mods_loc)
        chmods.safe_update(mods_specific)

        matched_patterns = [
            x for x in id_patterns+[loc_pattern]+[orient_pattern]+glob_patterns
            if x in channel_modifs]
        return chmods, matched_patterns
