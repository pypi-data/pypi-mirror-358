"""
Channel, Instrument and Operator classes
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
from obspy.core.inventory.channel import Channel as obspy_Channel
from obspy.core.inventory.util import Comment

# obsinfo modules
from ..obsmetadata import ObsMetadata
from ..helpers import (Location, OIDate, str_indent, verify_dict_is_empty,
                       Comments, ExternalReferences, Identifiers, ObsinfoClassList)
from .orientation import Orientation
from .instrument import Instrument

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Channels(ObsinfoClassList):
    """
    A list of Channel objects
    """
    def __init__(self, channels_list=None):
        """
        Args:
            channels_list: (list of :class:`Instrumentations`):
        """
        if channels_list is None:
            super().__init__([], Channel)
        elif isinstance(channels_list, list):
            super().__init__(channels_list, Channel)
        else:
            raise TypeError('channels_list is neither a list nor None')


class Channel(object):
    """
    Corresponds to StationXML/obspy Channel plus channel code

    Attributes:
        das_channel (:class:`ObsMetadata`): represents a channel with defaults
            incorporated
        location (:class:`Location`): location for this channel
        start_date (str): inherited from Station
        end_date (str): inherited from Station
        instrument (:class:`Instrument`): a sensor, a datalogger and an
            optional preamplifier
        orientation (:class:`Orientation`):
        comments (list of str)
    """

    def __init__(self, attributes_dict, ic_modifs: dict, location, equipment):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): channel attributes
            ic_modifs (dict or :class:`ObsMetadata`): modifications to pass
                through to InstrumentComponents
            location (:class:`Location`): channel location
            equipment (:class:`Equipment`): channel equipment
        """
        # For __repr__
        self.input = {
                      'attributes_dict':   {} if not attributes_dict else '<ObsMetaData>',
                      'ic_modifs':   {} if not ic_modifs else '<ObsMetaData>',
                      'location': location,
                      'equipment': '<obsinfo.Equipment>'
                     }

        # o_code = self._get_orientation_code(orientation)
        self.equipment = equipment
        self.location = location
        if 'location_code' in attributes_dict:
            if not self.location.code == attributes_dict['location_code']:
                raise ValueError('location.code != channel["location_code"] '
                                 f'({self.location.code}!={attributes_dict["location_code"]})')
            del attributes_dict['location_code']
        # print(f'Channel attributes_dict={attributes_dict}, {ic_modifs=}')
        self.start_date = OIDate(attributes_dict.pop('start_date'))
        self.end_date = OIDate(attributes_dict.pop('end_date'))
        self.comments = Comments(attributes_dict.pop("comments", None))
        self.comments += Comments.from_extras(attributes_dict.pop("extras", None))
        self.orientation = Orientation(attributes_dict.pop('orientation', None))
        self.source_id = attributes_dict.pop('source_id', None)
        self.identifiers = Identifiers(attributes_dict.pop('identifiers', None))
        self.restricted_status = attributes_dict.pop('restricted_status', None)
        self.external_references = ExternalReferences(attributes_dict.pop('external_references', None))

        self.instrument = Instrument(attributes_dict, ic_modifs)

        verify_dict_is_empty(attributes_dict)

    def __repr__(self):
        s =  f'Channel(default_attributes={self.input["default_attributes"]}\n'
        s += f'        ch_attributes={self.input["ch_attributes"]},\n'
        s += f'        ic_modifs={self.input["modifs"]},\n'
        s += f'        location={self.input["location"]}\n'
        s += f'        equipment={self.input["equipment"]}'
        s += f'       )'
        return s

    def __str__(self, indent=0, n_subclasses=0):
        """
        Args:
            indent (int): number of extra characters to indent lines by
            n_subclasses (int): number of levels of subclass to print out
        """
        if n_subclasses < 0:
            if self.location is not None:
                return f'{self.__class__.__name__} {self.location.code}.{self.seed_code}'
            else:
                return f'{self.__class__.__name__} {self.seed_code}'

        kwargs = {'indent': 4, 'n_subclasses': n_subclasses-1}
        s = f'{self.__class__.__name__} {self.seed_code}:\n'
        if self.location is not None:
            s += f'    location: {self.location.__str__(**kwargs)}\n'
        s += f'    orientation: {self.orientation.__str__(**kwargs)}\n'
        s += f'    start_date: {self.start_date}\n'
        s += f'    end_date: {self.end_date}\n'
        s += f'    equipment: {self.equipment.__str__(**kwargs)}\n'
        s += f'    comments: {self.comments}\n'
        s += f'    equipment: {self.instrument.__str__(**kwargs)}\n'

        return str_indent(s, indent)

    @property
    def seed_code(self):
        """
        This is equivalent to channel code for self.instrument.sample_rate
        """
        return self.channel_code()

    def channel_code(self, sample_rate=None):
        """
        Return channel code.

        Validates instrument and orientation codes according to FDSN
        specifications (for instruments, just the length). Channel codes
        specified by user are indicative and are refined using actual sample
        rate.
        
        Args:
            sample_rate (float or None): sample rate to use.  If None, uses
                self.instrument sample_rate
        """
        ORIENTATION_CODES = '123HGXYZEN'
        inst_code = self.instrument.sensor.seed_instrument_code

        if len(inst_code) != 1:
            msg = f'Instrument code "{inst_code}" is not a single letter'
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError(msg)
        if self.orientation.code not in ORIENTATION_CODES:
            msg = f'Orientation code "{self.orientation.code}" is not in '\
                  f'the approved list: "{ORIENTATION_CODES}"'
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError(msg)
        
        if sample_rate is None:
            band_code = self.instrument.seed_band_code
        else:
            band_code = self.instrument._seed_band_code(
                sample_rate, self.instrument.seed_band_base)
        return (band_code + inst_code + self.orientation.code)

    def to_obspy(self):
        """
         Create obspy Channel object

         Returns:
            (~class:`obspy.core.inventory.channel.Channel`)
        """
        channel = obspy_Channel(
            self.seed_code,
            self.location.code,
            latitude=self.location.latitude.to_obspy(),
            longitude=self.location.longitude.to_obspy(),
            elevation=self.location.elevation.to_obspy(),
            depth=self.location.depth_m,
            water_level=self.location.water_level_m,
            azimuth=self.orientation.azimuth.to_obspy(),
            dip=self.orientation.dip.to_obspy(),
            types=['CONTINUOUS', 'GEOPHYSICAL'],
            external_references=self.external_references,
            sample_rate=self.instrument.sample_rate,
            clock_drift_in_seconds_per_sample=1 / (1e8 * float(self.instrument.sample_rate)),
            sensor=self.instrument.sensor.equipment.to_obspy(),
            pre_amplifier=self.instrument.preamplifier.equipment.to_obspy()
                          if self.instrument.preamplifier else None,
            data_logger=self.instrument.datalogger.equipment.to_obspy(),
            equipments=[self.equipment.to_obspy()],
            response=self.instrument.to_obspy(),
            comments=self.comments.to_obspy(),
            start_date=self.start_date.to_obspy(),
            end_date=self.end_date.to_obspy(),
            restricted_status=self.restricted_status,
            identifiers=self.identifiers.to_obspy(),
            source_id=self.source_id,
            sample_rate_ratio_number_samples=None,
            sample_rate_ratio_number_seconds=None,
            description=None,
            calibration_units=None,
            calibration_units_description=None,
            storage_format=None,
            alternate_code=None,
            historical_code=None,
            data_availability=None)
        return channel

    def _channel_id(self, orientation_code):
        """
        Uniquely identify channel through orientation and location code

        format: {orientation}-{location}
        Args:
            orientation_code (str): single-letter orientation code
        :returns: channel code
        """
        return orientation_code + "-" + self.location.code

    @staticmethod
    def _get_comments(comments=[], extras={}):
        extras_list = [str(k) + ": " + str(v) for k, v in (extras).items()]
        if extras_list:
            comments.extend([f'Extra attribute: {{{e}}}' for e in extras_list])
        return comments
