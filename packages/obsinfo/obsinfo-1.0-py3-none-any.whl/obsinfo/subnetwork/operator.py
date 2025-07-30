"""
Operator class
"""
# Standard library modules
import warnings
import logging

from obspy.core.inventory.util import Operator as obspy_Operator

from ..helpers import Persons, ObsinfoClassList, str_indent, str_list_str


warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Operators(ObsinfoClassList):
    """
    A list of Operator objects
    """
    def __init__(self, seq):
        """
        Args:
            seq: (list of attribute_dict, Operator or None): Operators, or
                attribute dicts describing a Operator
        """
        super().__init__(seq, Operator)


class Operator(object):
    """
    Contact information for the operator of the instrumentation or network

    Attributes:
        agency (str): Reference name of agency
        contacts (:class:`Persons`):
        website (str): operator website
    """
    def __init__(self, attributes_dict):
        """
        Args:
            attributes_dict (dict or :class:`.ObsMetadata`):
                operator information
        Returns:
            None if attributes_dict is None, Operator object otherwise
        """
        self.agency = None
        if attributes_dict is None:
            return None

        self.agency = attributes_dict['agency']     # required
        self.contacts = Persons(attributes_dict.get('contacts', None))
        self.website = attributes_dict.get('website', None)

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 1:
            return f'agency: {self.agency}'
        kwargs = dict(indent=4, n_subclasses=n_subclasses-1)
        s = f'{self.__class__.__name__}:\n'
        s += f'    agency: {self.agency}\n'
        s += f'    contacts: {self.contacts.__str__(**kwargs)}\n'
        s += f'    website: {self.website}'
        return str_indent(s, indent)

    def to_obspy(self):
        if self.agency is None:
            return None
        return obspy_Operator(agency=self.agency,
                              contacts=self.contacts.to_obspy(),
                              website=self.website)
