"""
Station Class
"""
# Standard library modules
import logging
import json

# Non-standard modules
from obspy.core.inventory.station import Station as obspy_Station

from obspy.core.inventory.util import (Comment)
from obspy.core.utcdatetime import UTCDateTime
# from obspy.taup.seismic_phase import self_tokenizer

# obsinfo modules
from .processing import Processing
from ..instrumentation import Instrumentation, Instrumentations
from ..helpers import (Location, Locations, OIDate,
                       str_list_str, str_indent, verify_dict_is_empty,
                       ObsinfoClassList, Comments, ExternalReferences, Identifiers)
from .operator import Operators
from ..obsmetadata import ObsMetadata
from .site import Site

logger = logging.getLogger("obsinfo")


class Stations(ObsinfoClassList):
    """
    A list of Station objects
    """
    def __init__(self, stations_dict, operators, comments, leapseconds=None):
        """
        Args:
            stations_dict: (dict or :class:`.ObsMetadata`): dictionary
                from station or network info file with YAML or JSON
                attributes
            operators (:class:`.Operators`): default station
                operators
            comments: (:class:`.Comments`): default station comments
            leapseconds (dict): leapsecond information
        """
        if stations_dict is None:
            super().__init__([])
        else:
            super().__init__([Station(k, v, operators, comments, leapseconds)
                             for k, v in (stations_dict.items())], Station)


class Station(object):
    """
    Station. Equivalent to obspy/StationXML Station

    Methods convert info files to an instance of this class and convert the
    object to an `obspy` object.

    Attributes:
        code (str): Station code (FDSN)
        site (str): Site name
        start_date (str with date format): station start date
        end_date (str with date format): station end date
        location_code (str):
        restricted_status (str): status of station
        locations (list of :class:`.Location`)
        location (:class:`.Location`): default location code
            of channels, corresònding to `location_code`
        instrumentation (:class:`.Instrumentation` or list of
            :class:`.Instrumentation`):
        processing (list of objects of :class:`.Processing`) : attributes
            for clock correction processing
        comments (list of str):
        extras (list of str):
        source_id (str): StationXML sourceID (URI format)
        identifiers: (list of str): permanent identifiers (URI format)
        extra_references (list of dict): external references, each one is
            a dict with keys ['uri', 'description']
        water_level (number): elevation (m) of water surface (useful for lakes)
        obspy_station (:class:`obspy.core.inventory.station.Station`):
            Equivalent obspy object
    """

    def __init__(self, code, attributes_dict, stations_operators=None,
                 stations_comments=None, leapseconds=None):
        """
        Constructor

        Args:
            attributes_dict: (dict or :class:`.ObsMetadata`): dictionary
                from station or network info file with YAML or JSON attributes
            stations_operators (:class:`.Operators`): default station
                operator(s)
            stations_comments: (:class:`.Comments`): default station comments
            leapseconds (dict): leapsecond information 
        Raises:
            TypeError
        """
        if not attributes_dict:
            msg = 'No station attributes'
            logger.error(msg)
            raise TypeError(msg)

        logger.info(f'Creating Station "{code}"')
        self.code = code
        self.site = Site(attributes_dict.pop("site", code)) # defaults to station code
        self.start_date = OIDate(attributes_dict.pop("start_date"))
        self.end_date = OIDate(attributes_dict.pop("end_date"))
        self.location_code = attributes_dict.pop("location_code", None)
        self.restricted_status = attributes_dict.pop("restricted_status", None)
        if 'operators' in attributes_dict:
            self.operators = Operators(attributes_dict.pop("operators"))
        else:
            self.operators = stations_operators
        self.description = attributes_dict.pop("description", None)
        self.locations = Locations.from_locations_dict(attributes_dict.pop('locations'))

        # Find/validate location code
        if self.location_code is not None:
            self.location = self.locations.get_by_loc_code(self.location_code)
            if self.location is None:
                raise ValueError('{location_code=} not in locations')
        else:
            if len(self.locations) > 1:
                raise ValueError('location_code not specified but more than one location specifed')
            self.location = self.locations[0]
            self.location_code = self.location.code


        if 'instrumentation' in attributes_dict:
            instr_dict_list =  [attributes_dict.pop('instrumentation')]
        elif 'instrumentations' in attributes_dict:
            instr_dict_list = attributes_dict.pop('instrumentations')
        else:
            raise NameError('Neither "instrumentation" nor "instrumentations" declared for station {code}')
        self.instrumentations = Instrumentations(
            instr_dict_list, self.locations, self.location_code,
            self.start_date.date, self.end_date.date)

        self.processing = Processing(attributes_dict.pop('processing', []), leapseconds)
        self.comments = Comments(attributes_dict.pop("comments", []))
        if stations_comments is not None:
            self.comments += stations_comments
        self.source_id = attributes_dict.pop('source_id', None)
        self.identifiers = Identifiers(attributes_dict.pop('identifiers', None))
        self.extras = attributes_dict.pop('extras', None)
        self.external_references = ExternalReferences(attributes_dict.pop('external_references', None))
        self.comments += Comments.from_extras(attributes_dict.pop('extras', None))
        self.comments += self.processing.to_comments()
        if 'notes' in attributes_dict:
            del attributes_dict['notes']
        verify_dict_is_empty(attributes_dict)

    def __repr__(self):
        s =  f'station(dict(code={self.code}, site={self.site}, '
        s += f'start_date={self.start_date}, end_date={self.end_date}, '
        s += f'location_code={self.location_code}, '
        s += f'{len(self.locations)} Locations, '
        if self.processing:
            s += f'processing-steps: {self.processing.processing_list}'
        s += ')'
        return s

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{self.__class__.__name__} {self.code}'
        kwargs = dict(indent=indent+4, n_subclasses=n_subclasses-1)
        s = f'{self.__class__.__name__}:\n'
        s += f'    code: {self.code}\n'
        s += f'    site: {self.site}\n'
        s += f'    start_date: {self.start_date}\n'
        s += f'    end_date: {self.end_date}\n'
        s += f'    location_code: {self.location_code}\n'
        s += f'    restricted_status: {self.restricted_status}\n'
        s += f'    locations: {self.locations.__str__(**kwargs)}\n'
        s += f'    instrumentations: {self.instrumentations.__str__(**kwargs)}\n'
        s += f'    processing: {self.processing}'
        if len(self.comments) > 0:
            s += f'\n    comments: {str_list_str([str(self.comments)], **kwargs)}'
        if len(self.external_references) > 0:
            s += f'\n    external_references: {str_list_str(self.external_references, **kwargs)}'
        if self.source_id is not None:
            s += f'\n    source_id: {self.source_id}'
        if self.description is not None:
            s += f'\n    description: {self.description}'
        if len(self.identifiers) > 0:
            s += f'\n    identifiers: {str_list_str(self.identifiers,  **kwargs)}'
        if self.extras is not None:
            print(f'{self.extras=}')
            s += f'\n    extras: {str_list_str([json.dumps(self.extras)], **kwargs)}'
        return str_indent(s, indent)

    def to_obspy(self):
        """
        Convert station object to obspy object

        Returns:
            (:class:`obspy.core.inventory.station.Station`):
                  corresponding obspy Station object
        """
        channels_number = 0
        chnl_list = []
        equip_list = []
        for x in self.instrumentations:
            channels_number += len(x.channels)
            chnl_list += [ch.to_obspy() for ch in x.channels]
            equip_list += [x.equipment.to_obspy()]

        if len(self.external_references) > 0:
            msg = ('obspy 1.4.0 could not create station-level '
                   "external_references, so your's will not be written. "
                   "If this has been fixed in obspy, put an issue on the "
                   "obsinfo gitlab page so that we can update this")
            logger.warning(msg)

        return obspy_Station(
            code=self.code,
            latitude=self.location.latitude.to_obspy(),
            longitude=self.location.longitude.to_obspy(),
            elevation=self.location.elevation.to_obspy(),
            water_level=self.location.water_level_m,
            channels=chnl_list,
            site=self.site.to_obspy(),
            vault=self.location.vault,
            geology=self.location.geology,
            equipments=equip_list,
            operators=self.operators.to_obspy(),
            creation_date=self.start_date.to_obspy(),
            termination_date=self.end_date.to_obspy(),
            # external_references=self.external_references.to_obspy(),
            total_number_of_channels=channels_number,
            selected_number_of_channels=channels_number,
            comments=self.comments.to_obspy(),
            start_date=self.start_date.to_obspy(),
            end_date=self.end_date.to_obspy(),
            restricted_status=self.restricted_status,
            source_id=self.source_id,
            identifiers=self.identifiers.to_obspy(),
            description=self.description,
            alternate_code=None,
            historical_code=None,
            data_availability=None)

    def add_extras_to_comments(self):
        """
        Convert processing info and extras to comments
        """

        if self.extras:
            self.comments.append('EXTRA ATTRIBUTES (for documentation only):')
            self.comments = self.comments + self.extras
        if self.processing.processing_list:
            self.comments.append(self.processing.processing_list)
