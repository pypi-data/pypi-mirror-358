"""
Network :class:, network to which the subnetwork belongs
"""
# Standard library modules
import logging

# obsinfo modules
from .operator import Operators
from ..helpers import (str_indent, str_list_str, verify_dict_is_empty,
                       OIDate, Identifiers, Comments)

logger = logging.getLogger("obsinfo")


class Network(object):
    """
    Equivalent to obspy/StationXML Network

    Attributes:
         code (str)
         name (str)
         operators (:class:`Operators`): operators
         start_date (str with date format): network start date
         end_date (str with date format): network end date
         description  (str): network description
         comments (list of str):
         restricted_status (str): 'open', 'closed', or 'partial'
         source_id (str): network-level data source identifier in URI format
         identifiers (list of str): persistent identifiers as URIs, scheme (prefix) will be extracted
    """

    def __init__(self, attributes_dict=None):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): dictionary from
                subnetwork info file
        Raises:
            (TypeError): if attributes_dict is empty
        """
        if not attributes_dict:
            msg = 'No {self.__class__.__name__} attributes'
            logger.error(msg)
            raise TypeError(msg)

        self.code = attributes_dict.pop("code", None)
        self.operators = Operators(attributes_dict.pop("operators", None))
        self.start_date = OIDate(attributes_dict.pop("start_date", None))
        self.end_date = OIDate(attributes_dict.pop("end_date", None))
        self.description = attributes_dict.pop("description", None)
        self.restricted_status = attributes_dict.pop("restricted_status", None)
        self.source_id = attributes_dict.pop("source_id", None)
        self.identifiers = Identifiers(attributes_dict.pop("identifiers", None))
        self.comments = Comments(attributes_dict.pop("comments", None))
        verify_dict_is_empty(attributes_dict)

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        kwargs = {'indent': 4, 'n_subclasses': n_subclasses-1}
        s = f'{self.__class__.__name__}:\n'
        s += f'    code: {self.code}\n'
        s += f'    description: {self.description}\n'
        s += f'    operators: {self.operators.__str__(**kwargs)}\n'
        s += f'    start_date: {self.start_date}\n'
        s += f'    end_date: {self.end_date}\n'
        s += f'    restricted_status: {self.restricted_status}'
        if self.source_id is not None:
            s += f'\n    source_id: {self.source_id}'
        if self.identifiers is not None:
            s += f'\n    identifiers: {self.identifiers.__str__(**kwargs)}'
        if len(self.comments) > 0:
            s += f'\n    comments: {self.comments.__str__(**kwargs)}'
        return str_indent(s, indent)
