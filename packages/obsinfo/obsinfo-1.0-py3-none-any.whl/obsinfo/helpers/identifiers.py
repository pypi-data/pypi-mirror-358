"""
Identifiers Class, used in Networks, Channels and Stations
"""
# Standard library modules
import warnings
import logging
import json

from obspy.core.inventory.util import ExternalReference as obspy_extref

from .functions import str_indent
from .person import Persons
from .oi_date import OIDate
from .obsinfo_class_list import ObsinfoClassList

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Identifiers(ObsinfoClassList):
    """
    A list of :class:`Identifier` objects
    """
    def __init__(self, attributes_list):
        """
            Args:
                attributes_list: (list of dict or str): list
                    of external references read from YAML/JSON file
        """
        if attributes_list is None:
            super().__init__([], Identifier)
        else:
            super().__init__(attributes_list, Identifier)


class Identifier(object):
    """
    A type to document persistent identifiers. Must provide a scheme (prefix)
    """
    def __init__(self, uri):
        if ':' not in uri:
            raise ValueError(f'would-be Identifier "{uri}" has no scheme (prefix + ":")')
        self.uri = uri

    def __str__(self, indent=0, n_subclasses=0):
        """ Always a one-liner """
        return(f'{self.__class__.__name__}: {self.uri}')

    def to_obspy(self):
        """
        obspy handles identifiers as single strings
        """
        return self.uri
