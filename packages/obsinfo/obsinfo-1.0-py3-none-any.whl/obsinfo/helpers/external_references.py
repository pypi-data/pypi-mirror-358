"""
ExternalReferences Class, used in Channels and Stations
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


class ExternalReferences(ObsinfoClassList):
    """
    A list of ExternalReference objects
    """
    def __init__(self, attributes_list):
        """
            Args:
                attributes_list: (list of dict or str): list
                    of external references read from YAML/JSON file
        """
        if attributes_list is None:
            super().__init__([], ExternalReference)
        else:
            super().__init__(attributes_list, ExternalReference)


class ExternalReference(object):
    def __init__(self, attributes_dict):
        self.uri = attributes_dict.pop('uri')
        self.description = attributes_dict.pop('description')

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return(f'{self.__class__.__name__}: {self.uri}')
        s = f'{self.__class__.__name__}:\n'
        s += f'    uri: {self.uri}\n'
        s += f'    description: {self.description}'
        return str_indent(s, indent)

    def to_obspy(self):
        return obspy_extref(uri=self.uri, description=self.description)
