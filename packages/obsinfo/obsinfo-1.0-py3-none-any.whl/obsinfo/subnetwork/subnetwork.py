"""
Subnetwork :class:, all stations of a network deployed by one operator
"""
# Standard library modules
import warnings
import logging
from time import perf_counter

# Non-standard modules
from obspy.core.inventory.network import Network as obspy_network

# obsinfo modules
from .network import Network
from .station import Stations
from .operator import Operators
from ..helpers import (str_indent, str_list_str, verify_dict_is_empty,
                       OIDate, Identifiers, Comments)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Subnetwork(object):
    """
    Equivalent to obspy/StationXML Network

    Attributes:
         campaign_ref (str): campaign reference name:
         operator_ref (str): operator reference name
         network (:class:`Network`): FDSN network
         stations_operators (:class:`.Operators`): default operators for all stations
         stations (list of :class:`.Station`)
         comments (list of str)
         extras (list of str)
    """

    def __init__(self, attributes_dict=None, debug=False):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): dictionary from
                network info file
        Raises:
            (TypeError): if attributes_dict is empty
        """
        if debug is True:
            tic = perf_counter()
        if not attributes_dict:
            msg = 'No network attributes'
            logger.error(msg)
            raise TypeError(msg)

        ref_names = attributes_dict.pop("reference_names", None)
        if ref_names is not None:
            self.campaign_ref = ref_names.get("campaign", None)
            self.operator_ref = ref_names.get("operator", None)
        else:
            self.campaign_ref = None
            self.operator_ref = None
        if debug is True:
            tic = _timing_message(tic, 'Subnetwork:__init_() setup')

        self.network = Network(attributes_dict.pop("network", None))

        if debug is True:
            tic = _timing_message(tic, 'Subnetwork:__init_() created Network')

        self.operators = Operators(attributes_dict.pop("operators"))
        self.comments = Comments(attributes_dict.pop("comments", None))
        self.leapseconds = attributes_dict.pop("leapseconds", None)
        self.extras = [str(k) + ": " + str(v)
                       for k, v in (attributes_dict.pop('extras', {})).items()]
        self.add_extras_to_comments()

        if debug is True:
            tic = _timing_message(tic, 'Subnetwork:__init_() created Operators and Comments')

        self.stations = Stations(attributes_dict.pop("stations", None),
                                 self.operators, self.comments,
                                 self.leapseconds)

        if debug is True:
            tic = _timing_message(tic, 'Subnetwork:__init_() created Stations')
            
        verify_dict_is_empty(attributes_dict)

        if debug is True:
            tic = _timing_message(tic, 'Subnetwork:__init_() verify_dict_is_empty')
            


    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        kwargs = {'indent': 4, 'n_subclasses': n_subclasses-1}
        s = f'{self.__class__.__name__}:\n'
        if self.operator_ref is not None or self.campaign_ref is not None:
            s += f'    references:\n'
            if self.operator_ref is not None:
                s += f'        operator: {self.operator_ref}\n'
            if self.campaign_ref is not None:
                s += f'        campaign: {self.campaign_ref}\n'
        s += f'    network: {self.network.__str__(**kwargs)}\n'
        if len(self.extras) > 0:
            s += f'    extras: {str_list_str(self.extras, **kwargs)}\n'
        if len(self.comments) > 0:
            s += f'    stations_comments: {str_list_str(self.comments, **kwargs)}\n'
        s += f'    stations_operators: {self.operators.__str__(**kwargs)}\n'
        s += f'    stations: {self.stations.__str__(**kwargs)}'
        return str_indent(s, indent)

    def to_obspy(self):
        """
         Convert subnetwork object to obspy object

         Returns:
            (:class:~obspy.core.inventory.network.Network): corresponding
                obspy Network
        """
        return obspy_network(
            code=self.network.code,
            description=self.network.description,
            comments=self.network.comments.to_obspy(),
            start_date=self.network.start_date.to_obspy(),
            end_date=self.network.end_date.to_obspy(),
            restricted_status=self.network.restricted_status,
            identifiers=self.network.identifiers.to_obspy(),
            operators=self.network.operators.to_obspy(),
            source_id=self.network.source_id,
            stations=self.stations.to_obspy(),
            selected_number_of_stations=len(self.stations),
            total_number_of_stations=None,
            alternate_code=None,
            historical_code=None,
            data_availability=None)

    def add_extras_to_comments(self):
        """
        Convert info file extras to XML comments
        """
        if self.extras:
            self.comments += Comments.from_extras(self.extras)


def _timing_message(tic=None, message=None):
    """
    Returns perf_timer()

    If tic and message provided, writes out time elapsed message
    """
    toc = perf_counter()
    if message is not None:
        print(f'{toc-tic:.1f} seconds: {message}')
    return toc
